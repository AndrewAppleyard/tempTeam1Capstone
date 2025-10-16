<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const error = ref(null)

// const students = [
//   { studentid: 1, firstname: 'Yash', lastname: 'Patel' },
//   { studentid: 2, firstname: 'Andrew', lastname: 'Appleyard' },
//   { studentid: 3, firstname: 'Robert', lastname: 'Farrar' },
//   { studentid: 4, firstname: 'Christopher', lastname: 'Monterroza' },
//   { studentid: 5, firstname: 'Sophia', lastname: 'Praphan' }
// ]

const students = ref([]) 

async function fetchStudents() {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/Advisor/Student/1') // change based off of advisor id
    students.value = response.data
  } catch (err) {
    console.error('Error fetching students:', err)
    error.value = 'Failed to load students.'
  } finally {
    loading.value = false
  }
}

function goToStudent(studentid) {
  router.push(`/student/${studentid}`)
}

onMounted(() => {
  fetchStudents()
})
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
                  LIST OF STUDENTS
                </v-card-title>
              </v-card>
            </v-col>
          </v-row>

          <v-card-text>
            <v-row>
              <v-col
                v-for="student in students"
                :key="student.studentid"
                cols="12"
                sm="6"
                md="4"
              >
                <v-card
                  class="pa-2 text-center student-card"
                  flat
                  style="background-color: transparent; border: 1px solid #002856; border-radius: 8px;"
                  @click="goToStudent(student.studentid)"
                >
                  <v-card-title class="text-subtitle-3 font-weight-medium">
                    {{ student.firstname }} {{ student.lastname }}
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