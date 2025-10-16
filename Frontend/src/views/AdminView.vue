<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useViewModeStore } from '../store/pinia.js'
import { storeToRefs } from 'pinia'
import AdminAPI from '../apis/AdminAPI.js'
import AdvisorAPI from '../apis/AdvisorAPI.js'
import StudentAPI from '../apis/StudentAPI.js'

const store = useViewModeStore()
const { viewMode } = storeToRefs(store)
const router = useRouter()

// const advisors = [
//   { advisorid: 1, firstname: 'Andrew', lastname: 'Mackey' },
//   { advisorid: 2, firstname: 'Israel', lastname: 'Cuevas' },
//   { advisorid: 3, firstname: 'Brittany', lastname: 'Bright' },
//   { advisorid: 4, firstname: 'John', lastname: 'Hightower' },
//   { advisorid: 5, firstname: 'Brian', lastname: 'McLaughlan' }
// ]

// const students = [
//   { studentid: 1, firstname: 'Yash', lastname: 'Patel' },
//   { studentid: 2, firstname: 'Andrew', lastname: 'Appleyard' },
//   { studentid: 3, firstname: 'Robert', lastname: 'Farrar' },
//   { studentid: 4, firstname: 'Christopher', lastname: 'Monterroza' },
//   { studentid: 5, firstname: 'Sophia', lastname: 'Praphan' }
// ]

const advisors = ref([])
const students = ref([])

async function fetchAdvisors() {
  try {
    const data = await AdvisorAPI.getAllAdvisors()
    advisors.value = data
    console.log('Fetched Advisors:', advisors.value)
  } catch (err) {
    console.error('Error fetching advisors:', err)
  }
}

async function fetchStudents() {
  try {
    const data = await StudentAPI.getAllStudents()
    students.value = data
    console.log('Fetched Students:', students.value)
  } catch (err) {
    console.error('Error fetching students:', err)
  }
}

function goToUser(id) {
  console.log('Clicked User ID:', id)
  if (viewMode.value === 'students') {
    router.push(`/student/${id}`)
  } else {
    router.push(`/advisor/${id}`)
  }
}

watch(viewMode, (newMode) => {
  console.log('View mode changed to:', newMode)
  if (newMode === null) {
    newMode === 'advisors'
  }
  newMode === 'students' ? 'advisors' : fetchStudents(), fetchAdvisors()
}, { immediate: true })
</script>

<template>
  <v-container fluid class="pa-1" style="background-color: transparent;">
    <v-row justify="center">
      <v-col cols="12">
        <v-card
          class="pa-4"
          style="background-color: #BDD5E7; border: 1px solid #002856; border-radius: 12px;"
        >
          <v-row>
            <v-col>
              <v-card flat>
                <v-card-title style="color: #002856; border: 1px solid #002856; border-radius: 4px;">
                  LIST OF {{ viewMode === 'students' ? 'STUDENTS' : 'ADVISORS' }}
                </v-card-title>
              </v-card>
            </v-col>
          </v-row>

          <v-card-text>
            <v-row>
              <v-col
                v-for="item in (viewMode === 'students' ? students : advisors)"
                :key="item[viewMode === 'students' ? 'studentid' : 'advisorid']"
                cols="12"
                sm="6"
                md="4"
              >
                <v-card
                  class="pa-2 text-center student-card"
                  flat
                  style="background-color: transparent; border: 1px solid #002856; border-radius: 8px;"
                  @click="goToUser(viewMode === 'students' ? item.studentid : item.advisorid)"
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