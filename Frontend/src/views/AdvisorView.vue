<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdvisorAPI from '../apis/AdvisorAPI'
import AppointmentAPI from '../apis/AppointmentAPI'
import StudentFormCard from '../components/StudentFormCard.vue'
import { useUserStore } from '../store/user.js'

/* =========================
    STATE
========================= */
const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref(null)
const studentList = ref([]) 
const store = useUserStore()

const advisorId = computed(() => {
  if (!store.isLoggedIn) return null

  if (store.userRole === 'UAFS_ADVISORS') {
    return store.roleID ? Number(store.roleID) : null
  } else {
    //selected_user2 == advisor left ambiguous for security purposes
    //localStorage.getItem('selected_user2', userStore.selectedAdvisorID)
    return Number(localStorage.getItem('selected_user2'))
  }
})


const showStudentForm = ref(false)
const studentToEdit = ref(null)

const editMode = ref(false)

const searchQuery = ref('')
const selectedCategoryFilter = ref('All Students') 
const categoryOptions = [
  'All Students',
  'Pressing Holds',
  'Upcoming Advising Appointments',
  'Needs Advising',
  'All Clear'
]


/* ==============
    DATA FETCH 
================= */
async function fetchUpcomingAppointments(students) {
    const now = new Date();
    const studentPromises = students.map(async (s) => {
        try {
            const appointmentData = await AppointmentAPI.getAppointment(s.userid); 
            
            if (appointmentData && appointmentData.starttime && appointmentData.appointmentstatus === 'Scheduled') {
                const startTime = new Date(appointmentData.starttime);
                
                if (startTime > now) {
                    return {
                        ...s,
                        upcomingAppointmentDate: startTime.toISOString(),
                        isUpcomingAppointment: true
                    };
                }
            }
            return s;
        } catch (e) {
            console.warn(`Could not fetch appointment for student ${s.userid}:`, e);
            return s; 
        }
    });
    return Promise.all(studentPromises);
}


async function fetchStudents() {
  loading.value = true
  error.value = null
  try {
    let response = await AdvisorAPI.getAdvisorStudents(advisorId.value)
    
    response = await fetchUpcomingAppointments(response)
    studentList.value = response

    const now = new Date()
    studentList.value.sort((a, b) => {
      const aHold = a.advisinghold || a.academichold || a.financialhold
      const bHold = b.advisinghold || b.academichold || b.financialhold
      if (aHold !== bHold) return bHold - aHold

      const aUpcoming = a.isUpcomingAppointment
      const bUpcoming = b.isUpcomingAppointment
      if (aUpcoming !== bUpcoming) return aUpcoming ? -1 : 1

      const aDate = a.upcomingAppointmentDate ? new Date(a.upcomingAppointmentDate) : (a.dateadvised ? new Date(a.dateadvised) : null)
      const bDate = b.upcomingAppointmentDate ? new Date(b.upcomingAppointmentDate) : (b.dateadvised ? new Date(b.dateadvised) : null)

      if (aUpcoming && bUpcoming) return aDate.getTime() - bDate.getTime()

      // Students with no date advised come before students with a past date advised
      if (!aDate && bDate && bDate < now) return -1
      if (aDate && aDate < now && !bDate) return 1

      return a.lastname.localeCompare(b.lastname)
    })
  } catch (e) {
    console.error('Error fetching students:', e)
    error.value = 'Failed to load students. Please try again.'
  } finally {
    loading.value = false
  }
}


/* =========================
    DERIVED / FILTERED DATA 
========================= */
const isAdvised = (student) => student.advisingstatus === true || student.advisingstatus === 'Advised'
const hasAnyHold = (student) => student.advisinghold || student.academichold || student.financialhold

const holdStudents = computed(() => {
  return studentList.value.filter(hasAnyHold)
})

const upcomingStudents = computed(() => {
  const holdUserIds = new Set(holdStudents.value.map(s => s.userid))
  return studentList.value.filter(s =>
    !holdUserIds.has(s.userid) && s.isUpcomingAppointment
  ).sort((a, b) => {
    const dateA = new Date(a.upcomingAppointmentDate).getTime()
    const dateB = new Date(b.upcomingAppointmentDate).getTime()
    return dateA - dateB
  })
})

const needsAdvisingStudents = computed(() => {
  const upcomingUserIds = new Set(upcomingStudents.value.map(s => s.userid))
  const holdUserIds = new Set(holdStudents.value.map(s => s.userid))
  
  return studentList.value.filter(s =>
    !holdUserIds.has(s.userid) && 
    !upcomingUserIds.has(s.userid) &&
    !isAdvised(s) 
  ).sort((a, b) => a.lastname.localeCompare(b.lastname)) 
})

const allClearStudents = computed(() => {
  const upcomingUserIds = new Set(upcomingStudents.value.map(s => s.userid))
  const holdUserIds = new Set(holdStudents.value.map(s => s.userid))
  
  return studentList.value.filter(s =>
    !holdUserIds.has(s.userid) && 
    !upcomingUserIds.has(s.userid) &&
    isAdvised(s)
  ).sort((a, b) => a.lastname.localeCompare(b.lastname))
})

const categorizedStudents = computed(() => [
  { name: 'Pressing Holds', students: holdStudents.value, color: 'red-hold-bg' },
  { name: 'Upcoming Advising Appointments', students: upcomingStudents.value, color: 'blue-upcoming-bg' },
  { name: 'Needs Advising', students: needsAdvisingStudents.value, color: 'yellow-needs-bg' },
  { name: 'All Clear', students: allClearStudents.value, color: 'green-clear-bg' },
])

const filteredDisplayList = computed(() => {
  let list = []
  
  if (selectedCategoryFilter.value === 'All Students') {
    list = [
      ...holdStudents.value, 
      ...upcomingStudents.value, 
      ...needsAdvisingStudents.value, 
      ...allClearStudents.value
    ]
  } else {
    const category = categorizedStudents.value.find(c => c.name === selectedCategoryFilter.value)
    if (category) {
      list = category.students
    }
  }

  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return list

  return list.filter((s) => {
    const first = (s.firstname || '').toLowerCase()
    const last = (s.lastname || '').toLowerCase()
    const fullName = `${first} ${last}`.trim()
    const idStr = String(s.userid || '').toLowerCase()

    return (
      fullName.includes(q) ||
      first.includes(q) ||
      last.includes(q) ||
      idStr.includes(q)
    )
  })
})


/* =========================
    ACTIONS & UI HELPERS
========================= */
function handleStudentClick(student) {
    if (editMode.value) {
        studentToEdit.value = student
        showStudentForm.value = true
        localStorage.setItem('selected_user1', student.userid)

    } else {
        localStorage.setItem('selected_user1', student.userid)
        router.push(`/student`)
    }
}

function toggleEditMode() {
  editMode.value = !editMode.value
  studentToEdit.value = null 
}

function hasInfo(s) {
  return (
    hasAnyHold(s) ||
    s.advisingstatus ||
    s.registrationstatus
  )
}

function getCardStyle(s) {
  const isSelected = editMode.value && studentToEdit.value && studentToEdit.value.userid === s.userid

  const hasHold = hasAnyHold(s)
  const advised = isAdvised(s)
  let bg = '#E0E0E0' 

  if (hasHold) bg = '#FF746C' 
  else if (advised || s.isUpcomingAppointment) bg = '#ADEBB3' 
  
  return {
    backgroundColor: isSelected ? '#D1E5F4' : bg,
    border: '1px solid #002856',
    borderColor: isSelected ? '#0050a0' : '#002856',
    borderRadius: '10px'
  }
}

function getAdvisingDateText(s) {
    if (s.upcomingAppointmentDate) {
        const date = new Date(s.upcomingAppointmentDate)
        const dateOptions = { year: 'numeric', month: 'numeric', day: 'numeric' };
        const timeOptions = { hour: '2-digit', minute: '2-digit' };
        
        const formattedDate = date.toLocaleDateString(undefined, dateOptions);
        const formattedTime = date.toLocaleTimeString(undefined, timeOptions);
        
        return `Upcoming Appointment: ${formattedDate} at ${formattedTime}`
    }
    
    if (s.dateadvised) {
        const date = new Date(s.dateadvised)
        const formattedDate = date.toLocaleDateString()
        if (date > new Date()) {
            return `Upcoming Advising: ${formattedDate}`
        } else {
            return `Advised On: ${formattedDate}`
        }
    }
    return null
}

onMounted(async () => {
  const userData = await AdvisorAPI.getAdvisorById(advisorId.value)
  console.log(userData)
})
onMounted(fetchStudents)
</script>

<template>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <v-row>
      <v-col cols="12" class="mx-auto advisor-shell">
        <v-card
          class="pa-5 heavy-page"
          style="background-color:#BDD5E7;border:1px solid #002856;border-radius:16px;"
        >
          <v-row class="mb-4" align="center" no-gutters>
            <v-col cols="12" md="4" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title class="py-2 px-3 title-chip">
                  LIST OF STUDENTS
                </v-card-title>
              </v-card>
            </v-col>

            <v-col
              cols="12"
              md="8"
              class="d-flex justify-end align-center flex-wrap header-actions"
            >
              <v-select
                v-model="selectedCategoryFilter"
                :items="categoryOptions"
                class="filter-select"
                variant="outlined"
                density="compact"
                hide-details
                :color="'#002856'"
                label="Filter by Category"
                prepend-inner-icon="mdi-filter-variant"
              />

              <v-text-field
                v-model="searchQuery"
                class="search-input"
                variant="outlined"
                density="compact"
                hide-details
                clearable
                :color="'#002856'"
                label="Search students"
                prepend-inner-icon="mdi-magnify"
              />

              <v-btn variant="outlined" color="#002856" @click="fetchStudents">
                <v-icon start>mdi-refresh</v-icon>
                Refresh
              </v-btn>
            </v-col>
          </v-row>
          
          <v-card class="pa-4 mb-5 glass-card">
            <v-row justify="center">
              <v-col
                cols="12"
                class="d-flex flex-column align-center justify-center text-center"
              >
                <v-btn
                  color="#0032A0"
                  class="text-on-dark mb-3 main-edit-btn"
                  @click="toggleEditMode"
                >
                  {{ editMode ? 'Exit Edit Mode' : 'Edit' }}
                </v-btn>

                <template v-if="editMode">
                    <div class="mt-3 text-caption" style="color:#002856;">
                        In **Edit Mode**, click a student card to update their details (holds, status, etc.).
                    </div>
                </template>
              </v-col>
            </v-row>
          </v-card>
          
          <v-card class="pa-4 glass-card">
            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              class="mb-4"
              :border="'start'"
              style="border-left:4px solid #b00020;"
            >
              {{ error }}
            </v-alert>

            <v-row v-if="loading" dense>
              <v-col v-for="i in 8" :key="i" cols="12" sm="6" md="4" lg="3">
                <v-skeleton-loader
                  type="image, text, text"
                  class="glass-card pa-3"
                />
              </v-col>
            </v-row>
            
            <div
              v-else-if="!studentList.length"
              class="text-center brand-primary py-10"
            >
              <v-icon size="48" class="mb-2">mdi-account-off</v-icon>
              <div class="text-h6 mb-1">No students found</div>
              <div>Try refreshing or check your advisor assignment.</div>
            </div>

            <div
              v-else-if="studentList.length && !filteredDisplayList.length"
              class="text-center brand-primary py-10"
            >
              <v-icon size="48" class="mb-2">mdi-account-search</v-icon>
              <div class="text-h6 mb-1">No matching students</div>
              <div>
                No students match "<strong>{{ searchQuery }}</strong
                >" in the selected category.
              </div>
            </div>

            <div v-else>
              <template v-if="selectedCategoryFilter === 'All Students'">
                <template v-for="(category, index) in categorizedStudents" :key="category.name">
                  <template v-if="category.students.length > 0">
                    <h3 :class="['category-heading', category.color]">
                      <v-icon start>
                        {{ category.name === 'Pressing Holds' ? 'mdi-alert-circle' : '' }}
                        {{ category.name === 'Upcoming Advising Appointments' ? 'mdi-calendar-check' : '' }}
                        {{ category.name === 'Needs Advising' ? 'mdi-account-clock' : '' }}
                        {{ category.name === 'All Clear' ? 'mdi-check-circle' : '' }}
                      </v-icon>
                      {{ category.name }} ({{ category.students.length }})
                    </h3>
                    
                    <v-row dense class="mb-5">
                      <v-col
                        v-for="s in category.students"
                        :key="s.userid"
                        cols="12" sm="6" md="4" lg="3"
                      >
                         <v-card
                            class="pa-4 text-center student-card"
                            flat
                            :style="getCardStyle(s)"
                            @click="handleStudentClick(s)"
                          >
                            <v-card-text class="py-1">
                              <div :class="['user-date', s.isUpcomingAppointment ? 'upcoming-date' : '']">{{ getAdvisingDateText(s) || 'No Advising Date' }}</div>
                              <div
                                class="d-flex justify-center align-center mb-2"
                                style="gap:8px;"
                              >
                                <span class="user-name">
                                  {{ s.firstname }} {{ s.lastname }}
                                </span>
                                <v-tooltip location="top">
                                  <template #activator="{ props }">
                                    <v-icon
                                      v-if="hasInfo(s)"
                                      v-bind="props"
                                      size="18"
                                      color="#002856"
                                      class="cursor-pointer"
                                    >
                                      mdi-information-outline
                                    </v-icon>
                                  </template>
                                  <div style="white-space: pre-line; font-size: 0.9rem;">
                                    <strong>Advising Hold:</strong>
                                    {{ s.advisinghold ? 'Yes' : 'No' }}\n
                                    <strong>Academic Hold:</strong>
                                    {{ s.academichold ? 'Yes' : 'No' }}\n
                                    <strong>Financial Hold:</strong>
                                    {{ s.financialhold ? 'Yes' : 'No' }}\n
                                    <strong>Advising Status:</strong>
                                    {{ s.advisingstatus === true || s.advisingstatus === 'Advised' ? 'Advised' : (s.advisingstatus || 'N/A') }}\n
                                    <strong>Registration Status:</strong>
                                    {{ s.registrationstatus || 'N/A' }}
                                  </div>
                                </v-tooltip>
                              </div>
                            </v-card-text>
                          </v-card>
                      </v-col>
                    </v-row>
                    <hr v-if="index < categorizedStudents.length - 1 && categorizedStudents[index + 1].students.length > 0" class="category-divider" />
                  </template>
                </template>
              </template>
              
              <template v-else>
                <h3 :class="['category-heading', categorizedStudents.find(c => c.name === selectedCategoryFilter)?.color]">
                    <v-icon start>
                        {{ selectedCategoryFilter === 'Pressing Holds' ? 'mdi-alert-circle' : '' }}
                        {{ selectedCategoryFilter === 'Upcoming Advising Appointments' ? 'mdi-calendar-check' : '' }}
                        {{ selectedCategoryFilter === 'Needs Advising' ? 'mdi-account-clock' : '' }}
                        {{ selectedCategoryFilter === 'All Clear' ? 'mdi-check-circle' : '' }}
                    </v-icon>
                    {{ selectedCategoryFilter }} ({{ filteredDisplayList.length }})
                </h3>
                <v-row dense class="mb-5">
                    <v-col
                      v-for="s in filteredDisplayList"
                      :key="s.userid"
                      cols="12" sm="6" md="4" lg="3"
                    >
                      <v-card
                          class="pa-4 text-center student-card"
                          flat
                          :style="getCardStyle(s)"
                          @click="handleStudentClick(s)"
                        >
                          <v-card-text class="py-1">
                            <div :class="['user-date', s.isUpcomingAppointment ? 'upcoming-date' : '']">{{ getAdvisingDateText(s) || 'No Advising Date' }}</div>
                            <div
                              class="d-flex justify-center align-center mb-2"
                              style="gap:8px;"
                            >
                              <span class="user-name">
                                {{ s.firstname }} {{ s.lastname }}
                              </span>
                              <v-tooltip location="top">
                                <template #activator="{ props }">
                                  <v-icon
                                    v-if="hasInfo(s)"
                                    v-bind="props"
                                    size="18"
                                    color="#002856"
                                    class="cursor-pointer"
                                  >
                                    mdi-information-outline
                                  </v-icon>
                                </template>
                                <div style="white-space: pre-line; font-size: 0.9rem;">
                                  <strong>Advising Hold:</strong>
                                  {{ s.advisinghold ? 'Yes' : 'No' }}\n
                                  <strong>Academic Hold:</strong>
                                  {{ s.academichold ? 'Yes' : 'No' }}\n
                                  <strong>Financial Hold:</strong>
                                  {{ s.financialhold ? 'Yes' : 'No' }}\n
                                  <strong>Advising Status:</strong>
                                  {{ s.advisingstatus === true || s.advisingstatus === 'Advised' ? 'Advised' : (s.advisingstatus || 'N/A') }}\n
                                  <strong>Registration Status:</strong>
                                  {{ s.registrationstatus || 'N/A' }}
                                </div>
                              </v-tooltip>
                            </div>
                          </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
              </template>
            </div>
          </v-card>
        </v-card>
      </v-col>
    </v-row>

    <StudentFormCard
      v-model:visible="showStudentForm"
      :student="studentToEdit"
      @saved="fetchStudents"
    />
    
  </v-container>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <div class="text-center mt-6 brand-primary"style="padding-right: 5%;">
      © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
    </div>
  </v-container>
</template>

<style scoped>
/* Existing Styles */
.advisor-shell {
  width: 95%;
  padding-right: 5%;
  margin-left: auto;
  margin-right: auto;
}

.heavy-page {
  font-size: 1.06rem;
  line-height: 1.55;
}

.title-chip {
  color: #002856;
  border: 1px solid #002856;
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: 0.25px;
  font-size: 1.15rem;
}

.glass-card {
  background-color: rgba(255, 255, 255, 0.6);
  border: 1px solid #002856;
  border-radius: 12px;
}

.brand-primary {
  color: #002856;
}

.header-actions > .v-btn {
  margin-left: 10px;
  margin-top: 8px;
}

.search-input {
  min-width: 220px;
  max-width: 260px;
  margin-top: 8px;
}

/* NEW: Filter Select */
.filter-select {
  min-width: 240px;
  max-width: 280px;
  margin-top: 8px;
  margin-right: 10px;
}

/* Cards */
.student-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  cursor: pointer;
}
.student-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}
.user-name {
  font-weight: 650;
  font-size: 1.05rem;
}
.user-date {
  font-size: 0.85rem;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}
.upcoming-date {
  color: #0032a0;
  font-weight: 600;
}


.main-edit-btn {
  text-transform: none;
  font-weight: 600;
}

/* CATEGORY STYLES */
.category-heading {
  font-size: 1.35rem;
  font-weight: 700;
  color: #002856;
  padding: 8px 15px;
  border-radius: 8px;
  margin-top: 20px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-divider {
    border: 0;
    height: 1px;
    background-color: rgba(0, 40, 86, 0.2);
    margin: 20px 0;
}

.red-hold-bg {
  background-color: #ffcdd2; /* Light Red */
  border: 1px solid #e57373;
}

.blue-upcoming-bg {
  background-color: #bbdefb; /* Light Blue */
  border: 1px solid #64b5f6;
}

.yellow-needs-bg {
  background-color: #fff9c4; /* Light Yellow */
  border: 1px solid #ffee58;
}

.green-clear-bg {
  background-color: #c8e6c9; /* Light Green */
  border: 1px solid #a5d6a7;
}

@media print {
  .v-btn,
  .v-select,
  .v-text-field,
  .v-tabs {
    display: none !important;
  }
  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .v-card {
    box-shadow: none !important;
  }
}
</style>