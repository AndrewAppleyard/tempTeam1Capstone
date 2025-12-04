<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useViewModeStore } from '../store/pinia.js'
import { storeToRefs } from 'pinia'
import AdminAPI from '../apis/AdminAPI.js'
import AdvisorAPI from '../apis/AdvisorAPI.js'
import StudentAPI from '../apis/StudentAPI.js'
import StudentFormCard from '../components/StudentFormCard.vue'
import AdvisorFormCard from '../components/AdvisorFormCard.vue'

/* =========================================================
   STATE & STORES
========================================================= */
const store = useViewModeStore()
const { viewMode } = storeToRefs(store)
const router = useRouter()

const advisors = ref([])
const students = ref([])
const selectedItem = ref(null)
const editMode = ref(false)

const showStudentForm = ref(false)
const studentToEdit = ref(null)
const showAdvisorForm = ref(false)
const advisorToEdit = ref(null)

/* =========================================================
   FETCH FUNCTIONS
========================================================= */
async function fetchAdvisors() {
  try {
    const data = await AdvisorAPI.getAllAdvisors()
    advisors.value = data
  } catch (err) {
    console.error('Error fetching advisors:', err)
  }
}

async function fetchStudents() {
  try {
    const data = await StudentAPI.getAllStudents()
    const now = new Date()

    students.value = data.sort((a, b) => {
      const aHold = a.advisinghold || a.academichold || a.financialhold
      const bHold = b.advisinghold || b.academichold || b.financialhold
      if (aHold !== bHold) return bHold - aHold

      const aUpcoming = a.dateadvised && new Date(a.dateadvised) > now
      const bUpcoming = b.dateadvised && new Date(b.dateadvised) > now
      if (aUpcoming !== bUpcoming) return aUpcoming ? -1 : 1

      if (!a.dateadvised && b.dateadvised) return -1
      if (a.dateadvised && !b.dateadvised) return 1

      const aPast = a.dateadvised && new Date(a.dateadvised) < now
      const bPast = b.dateadvised && new Date(b.dateadvised) < now
      if (aPast !== bPast) return aPast ? 1 : -1

      return a.lastname.localeCompare(b.lastname)
    })
  } catch (err) {
    console.error('Error fetching students:', err)
  }
}

/* =========================================================
   ACTIONS & HANDLERS
========================================================= */
function goToUser(id) {
  if (viewMode.value === 'students') router.push(`/student/${id}`)
  else router.push(`/advisor/${id}`)
}

function selectUser(item) {
  if (editMode.value) selectedItem.value = item
  else goToUser(item[viewMode.value === 'students' ? 'studentid' : 'userid'])
}

function toggleEditMode() {
  editMode.value = !editMode.value
  selectedItem.value = null
}

function addUser() {
  if (viewMode.value === 'students') {
    studentToEdit.value = null
    showStudentForm.value = true
  } else {
    advisorToEdit.value = null
    showAdvisorForm.value = true
  }
}

function updateUser() {
  if (!selectedItem.value) return
  if (viewMode.value === 'students') {
    studentToEdit.value = selectedItem.value
    showStudentForm.value = true
  } else {
    advisorToEdit.value = selectedItem.value
    showAdvisorForm.value = true
  }
}

async function deleteUser() {
  if (!selectedItem.value) return
  const id = selectedItem.value[viewMode.value === 'students' ? 'studentid' : 'userid']
  try {
    if (viewMode.value === 'students') {
      await AdminAPI.deleteStudent(id)
      alert("Successfully deleted student.")
      fetchStudents()
    } else {
      await AdminAPI.deleteAdvisor(id)
      alert("Successfully deleted advisor.")
      fetchAdvisors()
    }
    selectedItem.value = null
  } catch (err) {
    console.error('Error deleting:', err)
  }
}

function refreshList() {
  if (viewMode.value === 'students') fetchStudents()
  else fetchAdvisors()
}

async function updateDegreePlans() {
  try {
    let count = 2
    const response = await AdminAPI.updateDegreePlans(count)
    console.log("Degree Plan Updated:", response);
    alert("Successfully updated degree plans.\n" + response);
    refreshList();
  } catch (err) {
    console.error("Degree Plan Update Error:", err);
    alert("Error updating degree plans. Check console for details.");
  }
}

async function updateCurrentCourses() {
  try {
    const response = await AdminAPI.updateCurrentCourses()
    console.log("Current Courses Updated:", response);
    alert("Successfully updated current courses.\n" + response.count);
    refreshList();
  } catch (err) {
    console.error("Current Courses Update Error:", err);
    alert("Error updating current courses. Check console for details.");
  }
}

/* =========================================================
   CARD LOGIC
========================================================= */
function hasInfo(item) {
  return (
    item.advisinghold ||
    item.academichold ||
    item.financialhold ||
    item.advisingstatus ||
    item.registrationstatus
  )
}

function getCardStyle(item) {
  if (viewMode.value === 'students') {
    const hasHold = item.advisinghold || item.academichold || item.financialhold
    const advising = item.advisingstatus
    let bg = 'transparent'

    if (hasHold) bg = '#FF746C'        // red-ish for holds
    else if (advising) bg = '#ADEBB3'  // green-ish if advised

    return {
      backgroundColor: selectedItem.value === item ? '#D1E5F4' : bg,
      border: '1px solid #002856',
      borderColor: selectedItem.value === item ? '#0050a0' : '#002856',
      borderRadius: '10px'
    }
  } else {
    return {
      backgroundColor: selectedItem.value === item ? '#D1E5F4' : 'transparent',
      border: '1px solid #002856',
      borderColor: selectedItem.value === item ? '#0050a0' : '#002856',
      borderRadius: '10px'
    }
  }
}

/* =========================================================
   WATCHERS
========================================================= */
watch(
  viewMode,
  (newMode) => {
    if (newMode === 'students') fetchStudents()
    else fetchAdvisors()
  },
  { immediate: true }
)
</script>

<template>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <v-row>
      <!-- 95% width shell, centered to match other pages -->
      <v-col cols="12" class="mx-auto admin-shell">
        <v-card class="pa-5 heavy-page"
                style="background-color:#BDD5E7;border:1px solid #002856;border-radius:16px;">

          <!-- Header / Title -->
          <v-row class="mb-4" align="center" no-gutters>
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title class="py-2 px-3 title-chip">
                  LIST OF {{ viewMode === 'students' ? 'STUDENTS' : 'ADVISORS' }}
                </v-card-title>
              </v-card>
              <v-btn @click="updateDegreePlans"> Update Degree Plans </v-btn>
              <v-btn @click="updateCurrentCourses"> Update Current Courses </v-btn>
            </v-col>

            <!-- (Optional) you can place a mini switch here to swap viewMode if needed -->
            <v-col cols="12" md="6" class="d-flex justify-end align-center flex-wrap header-actions">
              <!-- reserved for future filters / search -->
            </v-col>
          </v-row>

          <!-- Centered Control Bar -->
          <v-card class="pa-4 mb-5 glass-card">
            <v-row justify="center">
              <v-col cols="12" class="d-flex flex-column align-center justify-center text-center">
                <!-- Edit / Exit Edit Mode Button -->
                <v-btn color="#0032A0" class="text-on-dark mb-3" @click="toggleEditMode">
                  {{ editMode ? 'Exit Edit Mode' : 'Edit' }}
                </v-btn>

                <!-- Action Buttons (forced on new line & centered) -->
                <template v-if="editMode">
                  <div class="d-flex flex-wrap justify-center" style="gap: 12px;">
                    <v-btn class="action-btn" color="#002856" variant="flat" style="color:#F5F5F5" @click="addUser">
                      Add {{ viewMode === 'students' ? 'Student' : 'Advisor' }}
                    </v-btn>

                    <v-btn
                      class="action-btn"
                      color="warning"
                      @click="updateUser"
                      :disabled="!selectedItem"
                    >
                      Update {{ viewMode === 'students' ? 'Student' : 'Advisor' }}
                    </v-btn>

                    <v-btn
                      class="action-btn"
                      color="error"
                      @click="deleteUser"
                      :disabled="!selectedItem"
                    >
                      Delete {{ viewMode === 'students' ? 'Student' : 'Advisor' }}
                    </v-btn>
                  </div>
                </template>
              </v-col>
            </v-row>
          </v-card>

          <!-- User List -->
          <v-card class="pa-4 glass-card">
            <v-row>
              <v-col
                v-for="item in (viewMode === 'students' ? students : advisors)"
                :key="item[viewMode === 'students' ? 'studentid' : 'userid']"
                cols="12" sm="6" md="4" lg="3"
              >
                <v-card
                  :style="getCardStyle(item)"
                  class="pa-4 d-flex flex-column align-center justify-center user-card"
                  hover
                  @click="selectUser(item)"
                >
                  <v-card-title class="user-name">
                    {{ item.firstname }} {{ item.lastname }}

                    <v-tooltip location="top">
                      <template #activator="{ props }">
                        <v-icon
                          v-if="hasInfo(item)"
                          v-bind="props"
                          size="18"
                          color="#002856"
                          class="cursor-pointer"
                        >
                          mdi-information-outline
                        </v-icon>
                      </template>

                      <div style="white-space: pre-line; font-size: 0.9rem;">
                        <strong>Advising Hold:</strong> {{ item.advisinghold ? 'Yes' : 'No' }}\n
                        <strong>Academic Hold:</strong> {{ item.academichold ? 'Yes' : 'No' }}\n
                        <strong>Financial Hold:</strong> {{ item.financialhold ? 'Yes' : 'No' }}\n
                        <strong>Advising Status:</strong> {{ item.advisingstatus || 'N/A' }}\n
                        <strong>Registration Status:</strong> {{ item.registrationstatus || 'N/A' }}
                      </div>
                    </v-tooltip>
                  </v-card-title>

                  <v-card-subtitle v-if="item.dateadvised" class="text-caption" style="color: black;">
                    {{
                      new Date(item.dateadvised) > new Date()
                        ? `Upcoming advising appointment: ${new Date(item.dateadvised).toLocaleDateString()}`
                        : `Advised on: ${new Date(item.dateadvised).toLocaleDateString()}`
                    }}
                  </v-card-subtitle>
                </v-card>
              </v-col>
            </v-row>
          </v-card>

          <!-- Footer -->
          <div class="text-center mt-6 brand-primary">
            © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Popup Forms -->
    <StudentFormCard
      v-model:visible="showStudentForm"
      :student="studentToEdit"
      @saved="refreshList"
    />
    <AdvisorFormCard
      v-model:visible="showAdvisorForm"
      :advisor="advisorToEdit"
      @saved="refreshList"
    />
  </v-container>
</template>

<style scoped>
/* 95% width shell, centered to align with your other pages */
.admin-shell{
  width:95%;
  margin-left:auto;
  margin-right:auto;
}

/* Heavier but not flashy, consistent with profile/login */
.heavy-page{
  font-size:1.06rem;
  line-height:1.55;
}

/* Title chip */
.title-chip{
  color:#002856;
  border:1px solid #002856;
  border-radius:8px;
  font-weight:700;
  letter-spacing:.25px;
  font-size:1.15rem;
}

/* Subtle glass card look */
.glass-card{
  background-color:rgba(255,255,255,.6);
  border:1px solid #002856;
  border-radius:12px;
}

/* Brand helpers */
.brand-primary{ color:#002856; }
.text-on-dark{ color:#F5F5F5 !important; }

/* Buttons row */
.action-btn{ min-width:210px; }

/* User card hover & typography */
.user-card{ transition:transform .15s ease, box-shadow .15s ease; text-align:center; }
.user-card:hover{ transform:translateY(-2px); box-shadow:0 6px 16px rgba(0,0,0,.15); }
.user-name{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  font-weight:600;
  font-size:1.05rem;
}

/* Print */
@media print{
  .v-btn,.v-select,.v-text-field,.v-tabs{ display:none !important; }
  body{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .v-card{ box-shadow:none !important; }
}
</style>
