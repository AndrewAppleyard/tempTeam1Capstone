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
    students.value = data
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
                  class="pa-2 text-center student-card"
                  flat
                  :style="{ 
                    backgroundColor: selectedItem === item ? '#D1E5F4' : 'transparent', 
                    borderColor: selectedItem === item ? '#0050a0' : '#002856' 
                  }"
                  @click="selectUser(item)"
                >
                  <v-card-title class="text-subtitle-3 font-weight-medium">
                    {{ item.firstname }} {{ item.lastname }}
                  </v-card-title>
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

<style scoped>
.student-card {
  transition: background-color 0.3s ease;
  cursor: pointer;
}
.student-card:hover {
  background-color: #D1E5F4;
  border-color: #0050a0;
}
</style>