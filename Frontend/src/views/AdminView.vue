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
import Popups from '../components/Popups.vue'
import { VIcon } from 'vuetify/components'

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

    students.value = data.sort((a, b) => {
      const now = new Date()

      const aHold = a.advisinghold || a.academichold || a.financialhold
      const bHold = b.advisinghold || b.academichold || b.financialhold
      if (aHold !== bHold) return bHold - aHold

      const aUpcoming = a.dateadvised && new Date(a.dateadvised) > now
      const bUpcoming = b.dateadvised && new Date(b.dateadvised) > now

      const aPast = a.dateadvised && new Date(a.dateadvised) < now
      const bPast = b.dateadvised && new Date(b.dateadvised) < now

      // upcoming or no advising appointments higher
      if (aUpcoming !== bUpcoming) return aUpcoming ? -1 : 1

      if (!a.dateadvised && b.dateadvised) return -1
      if (a.dateadvised && !b.dateadvised) return 1

      if (aPast !== bPast) return aPast ? 1 : -1

      return a.lastname.localeCompare(b.lastname)
    })
  } catch (err) {
    console.error('Error fetching students:', err)
  }
}

function goToUser(id) {
  if (viewMode.value === 'students') {
    router.push(`/student/${id}`)
  } else {
    router.push(`/advisor/${id}`)
  }
}

function selectUser(item) {
  if (editMode.value) {
    selectedItem.value = item
  } else {
    goToUser(item[viewMode.value === 'students' ? 'studentid' : 'userid']) // userid = advisorid
  }
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
  const id = selectedItem.value[viewMode.value === 'students' ? 'studentid' : 'userid'] // advisorid = userid
  try {
    console.log("Deleting ")
    if (viewMode.value === 'students') {
      console.log("Student: " + id)
      await AdminAPI.deleteStudent(id)
      fetchStudents()
    } else {
      console.log("Advisor: " + id)
      await AdminAPI.deleteAdvisor(id)
      fetchAdvisors()
    }
    
    selectedItem.value = null
  } catch (err) {
    console.error('Error deleting:', err)
  }
}

function refreshList() {
  if (viewMode.value === 'students') {
    fetchStudents()
  } else {
    fetchAdvisors()
  }
}

function hasInfo(item) {
  return item.advisinghold || item.academichold || item.financialhold || item.advisingstatus || item.registrationstatus
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
      borderRadius: '8px'
    }
  } else {
    return {
      backgroundColor: selectedItem.value === item ? '#D1E5F4' : 'transparent',
      border: '1px solid #002856',
      borderColor: selectedItem.value === item ? '#0050a0' : '#002856',
      borderRadius: '8px'
    }
  }
}

watch(viewMode, (newMode) => {
  if (newMode === 'students') fetchStudents()
  else fetchAdvisors()
}, { immediate: true })
</script>

<template>
  <v-container fluid class="pa-1" style="background-color: transparent;">
    <v-row justify="center">
      <v-col cols="12">
        <v-card class="pa-4" style="background-color: #BDD5E7; border: 1px solid #002856; border-radius: 12px;">

          <v-row>
            <v-col>
              <v-card flat>
                <v-card-title style="color: #002856; border: 1px solid #002856; border-radius: 4px;">
                  LIST OF {{ viewMode === 'students' ? 'STUDENTS' : 'ADVISORS' }}
                </v-card-title>
              </v-card>
            </v-col>
          </v-row>

          <!-- edit mode -->
          <v-row justify="center" class="mb-2">
            <v-col cols="auto">
              <v-btn color="secondary" @click="toggleEditMode">
                {{ editMode ? 'Exit Edit Mode' : 'Edit' }}
              </v-btn>
            </v-col>
          </v-row>

          <v-row justify="center" v-if="editMode" class="mb-4">
            <v-col cols="auto" class="d-flex justify-center" style="gap: 12px;">
              <v-btn color="primary" @click="addUser">
                Add {{ viewMode === 'students' ? 'Student' : 'Advisor' }}
              </v-btn>
              <v-btn color="warning" @click="updateUser" :disabled="!selectedItem">
                Update {{ viewMode === 'students' ? 'Student' : 'Advisor' }}
              </v-btn>
              <v-btn color="error" @click="deleteUser" :disabled="!selectedItem">
                Delete {{ viewMode === 'students' ? 'Student' : 'Advisor' }}
              </v-btn>
            </v-col>
          </v-row>

          <!-- pop ups --> <!-- advisorid = userid -->
          <v-card-text>
            <v-row> 
              <v-col
                v-for="item in (viewMode === 'students' ? students : advisors)"
                :key="item[viewMode === 'students' ? 'studentid' : 'userid']"
                cols="12" sm="6" md="4"
              >
                <v-card
                  :style="getCardStyle(item)"
                  class="pa-3 d-flex flex-column align-center justify-center"
                  hover
                  @click="selectUser(item)"
                >
                  <v-card-title
                    class="text-subtitle-3 font-weight-medium"
                    style="display: flex; align-items: center; justify-content: center; gap: 6px;"
                  >
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

                      <div style="white-space: pre-line; font-size: 0.85rem;">
                        <strong>Advising Hold:</strong> {{ item.advisinghold ? 'Yes' : 'No' }}<br>
                        <strong>Academic Hold:</strong> {{ item.academichold ? 'Yes' : 'No' }}<br>
                        <strong>Financial Hold:</strong> {{ item.financialhold ? 'Yes' : 'No' }}<br>
                        <strong>Advising Status:</strong> {{ item.advisingstatus || 'N/A' }}<br>
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
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Popup forms -->
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