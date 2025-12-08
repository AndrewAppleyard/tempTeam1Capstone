<script setup>
import { ref, watch, computed } from 'vue'
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

const newAdvisorType = ref('') // 'ROAR' | 'COLLEGE'

// Search terms
const advisorSearch = ref('')
const studentSearch = ref('')

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmAction = ref(null) 

const showSnackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

/* =========================================================
   FETCH FUNCTIONS
========================================================= */
async function fetchAdvisors() {
  try {
    const data = await AdvisorAPI.getAllAdvisors()
    advisors.value = data || []
  } catch (err) {
    console.error('Error fetching advisors:', err)
  }
}

async function fetchStudents() {
  try {
    const data = await StudentAPI.getAllStudents()
    const now = new Date()

    students.value = (data || []).sort((a, b) => {
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
   ADVISOR CATEGORY HELPER
========================================================= */
function advisorCategory(a) {
  const raw = (a.advisortype || '').toString().trim().toUpperCase()

  if (raw === 'ROAR') return 'ROAR'
  if (raw === 'COLLEGE') return 'COLLEGE'
  return 'UNASSIGNED'
}

/* =========================================================
   COMPUTED: ADVISOR GROUPS + FILTERING
========================================================= */
const roarAdvisors = computed(() =>
  advisors.value.filter(a => advisorCategory(a) === 'ROAR')
)

const collegeAdvisors = computed(() =>
  advisors.value.filter(a => advisorCategory(a) === 'COLLEGE')
)

const unassignedAdvisors = computed(() =>
  advisors.value.filter(a => advisorCategory(a) === 'UNASSIGNED')
)


const filteredRoarAdvisors = computed(() => {
  const q = advisorSearch.value.trim().toLowerCase()
  if (!q) return roarAdvisors.value

  return roarAdvisors.value.filter(a => {
    const fullName = `${a.firstname || ''} ${a.lastname || ''}`.toLowerCase()
    const email = (a.email || '').toLowerCase()
    return fullName.includes(q) || email.includes(q)
  })
})

const filteredCollegeAdvisors = computed(() => {
  const q = advisorSearch.value.trim().toLowerCase()
  if (!q) return collegeAdvisors.value

  return collegeAdvisors.value.filter(a => {
    const fullName = `${a.firstname || ''} ${a.lastname || ''}`.toLowerCase()
    const email = (a.email || '').toLowerCase()
    return fullName.includes(q) || email.includes(q)
  })
})

const filteredUnassignedAdvisors = computed(() => {
  const q = advisorSearch.value.trim().toLowerCase()
  if (!q) return unassignedAdvisors.value

  return unassignedAdvisors.value.filter(a => {
    const fullName = `${a.firstname || ''} ${a.lastname || ''}`.toLowerCase()
    const email = (a.email || '').toLowerCase()
    return fullName.includes(q) || email.includes(q)
  })
})

/* =========================================================
   COMPUTED: STUDENT FILTERING
========================================================= */
const filteredStudents = computed(() => {
  const q = studentSearch.value.trim().toLowerCase()
  if (!q) return students.value

  return students.value.filter(s => {
    const fullName = `${s.firstname || ''} ${s.lastname || ''}`.toLowerCase()
    const email = (s.email || '').toLowerCase()
    const id = (s.userid || '').toString().toLowerCase()
    return fullName.includes(q) || email.includes(q) || id.includes(q)
  })
})

/* =========================================================
   ACTIONS & HANDLERS
========================================================= */
function goToUser(id) {
  if (viewMode.value === 'students') router.push(`/student/${id}`)
  else router.push(`/advisor/${id}`)
}

function selectUser(item) {
  if (editMode.value) {
    selectedItem.value = item
  } else {
    const key = viewMode.value === 'students' ? 'studentid' : (item.advisorid ? 'advisorid' : 'userid')
    goToUser(item[key])
  }
}

function toggleEditMode() {
  editMode.value = !editMode.value
  selectedItem.value = null
}

/**
 * Add new Student / Advisor.
 * For advisors, we pass null so AdvisorFormCard knows this is "create".
 */
function addUser() {
  selectedItem.value = null

  if (viewMode.value === 'students') {
    studentToEdit.value = null
    fetchAdvisors()
    showStudentForm.value = true
  } else {
    advisorToEdit.value = null
    newAdvisorType.value = '' 
    showAdvisorForm.value = true
  }
}

/**
 * Update existing Student / Advisor
 */
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

  const idKey = viewMode.value === 'students' ? 'studentid' : 'userid'
  const id = selectedItem.value[idKey]

  console.log(`Deleting:\t${idKey.toUpperCase()}: ${id}`)

  try {
    if (viewMode.value === 'students') {
      await AdminAPI.deleteStudent(id)
      showNotification("Successfully deleted student.", 'success')
      fetchStudents()
    } else {
      await AdminAPI.deleteAdvisor(id)
      showNotification("Successfully deleted advisor.", 'success')
      fetchAdvisors()
    }
    selectedItem.value = null
  } catch (err) {
    console.error('Error deleting:', err)
    showNotification("Error deleting user.", 'error')
  }
}

function refreshList() {
  if (viewMode.value === 'students') fetchStudents()
  else fetchAdvisors()
}

async function updateDegreePlans() {
  showConfirmDialog(
    'Confirm Degree Plan Update',
    'Are you sure you want to update all degree plans?',
    executeUpdateDegreePlans
  )
}

async function updateCurrentCourses() {
  showConfirmDialog(
    'Confirm Current Courses Update',
    'Are you sure you want to update all current courses? This process can be resource-intensive and take several minutes.',
    executeUpdateCurrentCourses
  )
}

async function executeUpdateDegreePlans() {
  try {
    const count = 4
    const response = await AdminAPI.updateDegreePlans(count)
    console.log("Degree Plan Updated:", response);
    showNotification("Successfully updated degree plans.", 'success');
    refreshList();
  } catch (err) {
    console.error("Degree Plan Update Error:", err);
    showNotification("Error updating degree plans.", error);
  }
}

async function executeUpdateCurrentCourses() {
  try {
    const response = await AdminAPI.updateCurrentCourses()
    console.log("Current Courses Updated:", response);
    showNotification("Successfully updated current courses.", 'success');
    refreshList();
  } catch (err) {
    console.error("Current Courses Update Error:", err);
    showNotification("Error updating current courses. Check console for details.", 'error');
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

    if (hasHold) bg = '#FF746C'
    else if (advising) bg = '#ADEBB3'

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

function showNotification(message, color) {
    snackbarText.value = message
    snackbarColor.value = color
    showSnackbar.value = true
}

function showConfirmDialog(title, message, action) {
  confirmTitle.value = title
  confirmMessage.value = message
  confirmAction.value = action
  showConfirm.value = true
}

function handleConfirm() {
  if (confirmAction.value) {
    confirmAction.value()
  }
  showConfirm.value = false
  confirmAction.value = null
}

function handleCancel() {
  showConfirm.value = false
  confirmAction.value = null
}

/* =========================================================
   WATCHERS
========================================================= */
watch(
  viewMode,
  async newMode => {
    advisorSearch.value = ''
    studentSearch.value = ''
    selectedItem.value = null

    if (newMode === 'students') {
      await fetchStudents()
    } else {
      await fetchAdvisors()
    }
  },
  { immediate: true }
)
</script>

<template>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <v-row>
      <!-- 95% width shell, centered to match other pages -->
      <v-col cols="12" class="mx-auto admin-shell">
        <v-card
          class="pa-5 heavy-page"
          style="background-color:#BDD5E7;border:1px solid #002856;border-radius:16px;"
        >
          <!-- Header / Title -->
          <v-row class="mb-4" align="center" no-gutters>
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title class="py-2 px-3 title-chip">
                  LIST OF {{ viewMode === 'students' ? 'STUDENTS' : 'ADVISORS' }}
                </v-card-title>
              </v-card>
            </v-col>

            <!-- Header actions -->
            <v-col
              cols="12"
              md="6"
              class="d-flex justify-end align-center flex-wrap header-actions"
            >
              <v-btn
                class="header-update-btn brand-primary-btn"
                prepend-icon="mdi-file-tree"
                @click="updateDegreePlans"
              >
                Update Degree Plans
              </v-btn>

              <v-btn
                class="header-update-btn brand-primary-btn"
                prepend-icon="mdi-book-open-variant"
                @click="updateCurrentCourses"
              >
                Update Current Courses
              </v-btn>

            </v-col>
          </v-row>

          <!-- Centered Control Bar -->
          <v-card class="pa-4 mb-5 glass-card">
            <v-row justify="center">
              <v-col
                cols="12"
                class="d-flex flex-column align-center justify-center text-center"
              >
                <!-- Edit / Exit Edit Mode Button -->
                <v-btn
                  color="#0032A0"
                  class="text-on-dark mb-3 main-edit-btn"
                  @click="toggleEditMode"
                >
                  {{ editMode ? 'Exit Edit Mode' : 'Edit' }}
                </v-btn>

                <!-- Action Buttons -->
                <template v-if="editMode">
                  <div class="d-flex flex-wrap justify-center action-btn-row">
                    <v-btn
                      class="action-btn"
                      color="#002856"
                      variant="flat"
                      style="color:#F5F5F5"
                      @click="addUser"
                  >
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

                  <div class="mt-3 text-caption" style="color:#002856;">
                    When adding an advisor, be sure to select their category
                    (ROAR or College) in the advisor form.
                  </div>
                </template>
              </v-col>
            </v-row>
          </v-card>

          <!-- STUDENTS VIEW -->
          <v-card
            v-if="viewMode === 'students'"
            class="pa-4 glass-card"
          >
            <!-- Search Bar for Students -->
            <v-row class="mb-4" align="center">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="studentSearch"
                  label="Search students by name, email, or ID"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-magnify"
                  clearable
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col
                v-for="item in filteredStudents"
                :key="item.userid"
                cols="12"
                sm="6"
                md="4"
                lg="3"
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

                      <div class="info-tooltip">
                        <div><strong>Advising Hold:</strong> {{ item.advisinghold ? 'Yes' : 'No' }}</div>
                        <div><strong>Academic Hold:</strong> {{ item.academichold ? 'Yes' : 'No' }}</div>
                        <div><strong>Financial Hold:</strong> {{ item.financialhold ? 'Yes' : 'No' }}</div>
                        <div><strong>Advising Status:</strong> {{ item.advisingstatus || 'N/A' }}</div>
                        <div><strong>Registration Status:</strong> {{ item.registrationstatus || 'N/A' }}</div>
                      </div>
                    </v-tooltip>
                  </v-card-title>

                  <v-card-subtitle
                    v-if="item.dateadvised"
                    class="text-caption"
                    style="color: black;"
                  >
                    {{
                      new Date(item.dateadvised) > new Date()
                        ? `Upcoming advising appointment: ${new Date(item.dateadvised).toLocaleDateString()}`
                        : `Advised on: ${new Date(item.dateadvised).toLocaleDateString()}`
                    }}
                  </v-card-subtitle>
                </v-card>
              </v-col>

              <v-col
                v-if="filteredStudents.length === 0"
                cols="12"
                class="text-center text-caption"
              >
                No students found.
              </v-col>
            </v-row>
          </v-card>

          <!-- ADVISORS VIEW (ROAR / COLLEGE / UNASSIGNED) -->
          <v-card
            v-else
            class="pa-4 glass-card"
          >
            <!-- Search Bar for Advisors -->
            <v-row class="mb-4" align="center">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="advisorSearch"
                  label="Search advisors by name or email"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-magnify"
                  clearable
                />
              </v-col>
            </v-row>

            <!-- ROAR ADVISORS -->
            <v-row>
              <v-col cols="12">
                <h3 class="mb-3 brand-primary">ROAR Advisors</h3>
              </v-col>

              <v-col
                v-for="item in filteredRoarAdvisors"
                :key="item.userid"
                cols="12"
                sm="6"
                md="4"
                lg="3"
              >
                <v-card
                  :style="getCardStyle(item)"
                  class="pa-4 d-flex flex-column align-center justify-center user-card"
                  hover
                  @click="selectUser(item)"
                >
                  <v-card-title class="user-name">
                    {{ item.firstname }} {{ item.lastname }}
                  </v-card-title>
                  <v-card-subtitle class="text-caption" style="color:black;">
                    ROAR Advisor
                  </v-card-subtitle>
                </v-card>
              </v-col>

              <v-col
                v-if="filteredRoarAdvisors.length === 0"
                cols="12"
                class="text-center text-caption"
              >
                No ROAR advisors found.
              </v-col>
            </v-row>

            <v-divider class="my-6" />

            <!-- COLLEGE ADVISORS -->
            <v-row>
              <v-col cols="12">
                <h3 class="mb-3 brand-primary">College Advisors</h3>
              </v-col>

              <v-col
                v-for="item in filteredCollegeAdvisors"
                :key="item.userid"
                cols="12"
                sm="6"
                md="4"
                lg="3"
              >
                <v-card
                  :style="getCardStyle(item)"
                  class="pa-4 d-flex flex-column align-center justify-center user-card"
                  hover
                  @click="selectUser(item)"
                >
                  <v-card-title class="user-name">
                    {{ item.firstname }} {{ item.lastname }}
                  </v-card-title>
                  <v-card-subtitle class="text-caption" style="color:black;">
                    College Advisor
                  </v-card-subtitle>
                </v-card>
              </v-col>

              <v-col
                v-if="filteredCollegeAdvisors.length === 0"
                cols="12"
                class="text-center text-caption"
              >
                No college advisors found.
              </v-col>
            </v-row>

            <v-divider class="my-6" />

            <!-- OTHER / UNASSIGNED ADVISORS -->
            <v-row v-if="filteredUnassignedAdvisors.length">
              <v-col cols="12">
                <h3 class="mb-3 brand-primary">Other / Unassigned Advisors</h3>
              </v-col>

              <v-col
                v-for="item in filteredUnassignedAdvisors"
                :key="item.userid"
                cols="12"
                sm="6"
                md="4"
                lg="3"
              >
                <v-card
                  :style="getCardStyle(item)"
                  class="pa-4 d-flex flex-column align-center justify-center user-card"
                  hover
                  @click="selectUser(item)"
                >
                  <v-card-title class="user-name">
                    {{ item.firstname }} {{ item.lastname }}
                  </v-card-title>
                  <v-card-subtitle class="text-caption" style="color:black;">
                    Uncategorized
                  </v-card-subtitle>
                </v-card>
              </v-col>
            </v-row>
          </v-card>
        </v-card>
      </v-col>
    </v-row>

    <!-- Popup Forms -->
    <StudentFormCard
      v-model:visible="showStudentForm"
      :student="studentToEdit"
      :advisors="advisors"
      @saved="refreshList"
    />

    <!-- AdvisorFormCard -->
    <AdvisorFormCard
      v-model:visible="showAdvisorForm"
      :advisor="advisorToEdit"
      :default-type="newAdvisorType"
      @saved="refreshList"
    />
  </v-container>

  <v-container fluid class="pa-2" style="background-color: transparent;">
    <!-- <StudentFormCard
      v-model:visible="showStudentForm"
      :student="studentToEdit"
      @saved="refreshList"
    />
    <AdvisorFormCard
      v-model:visible="showAdvisorForm"
      :advisor="advisorToEdit"
      :default-type="newAdvisorType"
      @saved="refreshList"
    /> -->

    <v-dialog v-model="showConfirm" max-width="500">
      <v-card>
        <v-card-title class="bg-error text-white">{{ confirmTitle }}</v-card-title>
        <v-card-text>{{ confirmMessage }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="handleCancel"
            class="cancel-btn"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error" variant="flat"
            @click="handleConfirm"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>

  <v-container fluid class="pa-2" style="background-color: transparent;">
    <div class="text-center mt-6 brand-primary">
      © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
    </div>

    <v-snackbar
      v-model="showSnackbar"
      :color="snackbarColor"
      :timeout="4000"
      location="top right"
      class="snackbar-custom"
    >
      {{ snackbarText }}
      
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          @click="showSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<style scoped>
/* 95% width shell, centered to align with your other pages */
.admin-shell {
  width: 95%;
  margin-left: auto;
  margin-right: auto;
}

/* Heavier but not flashy, consistent with profile/login */
.heavy-page {
  font-size: 1.06rem;
  line-height: 1.55;
}

/* Title chip */
.title-chip {
  color: #002856;
  border: 1px solid #002856;
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: 0.25px;
  font-size: 1.15rem;
}

/* Subtle glass card look */
.glass-card {
  background-color: rgba(255, 255, 255, 0.6);
  border: 1px solid #002856;
  border-radius: 12px;
}

/* Brand helpers */
.brand-primary {
  color: #002856;
}
.text-on-dark {
  color: #F5F5F5 !important;
}

/* HEADER BUTTONS */
.header-actions {
  gap: 8px;
}

.header-update-btn {
  margin-left: 0.5rem;
  margin-top: 0.5rem;
  padding-inline: 16px;
  text-transform: none;
  font-weight: 600;
  border-radius: 999px;
  font-size: 0.92rem;
}

/* Brand primary pill-style button */
.brand-primary-btn {
  background-color: #0032A0 !important;
  color: #F5F5F5 !important;
}

/* Main Edit button */
.main-edit-btn {
  text-transform: none;
  font-weight: 600;
}

/* Buttons row */
.action-btn-row {
  gap: 12px;
}
.action-btn {
  min-width: 210px;
  text-transform: none;
  font-weight: 600;
}

/* User card hover & typography */
.user-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  text-align: center;
}
.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}
.user-name {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  font-size: 1.05rem;
}

/* Tooltip content */
.info-tooltip {
  white-space: normal;
  font-size: 0.9rem;
  line-height: 1.3;
}

/* Cancel buttons -> black text */
.cancel-btn {
  color: black !important;
}

/* Print */
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
