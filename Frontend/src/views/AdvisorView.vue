<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Test from '../components/test.vue'

const router = useRouter()

const studentList = ref({
    name: ref("")
})

const students = [
  { studentID: 1, firstName: 'Yash', lastName: 'Patel' },
  { studentID: 2, firstName: 'Andrew', lastName: 'Appleyard' },
  { studentID: 3, firstName: 'Robert', lastName: 'Farrar' },
  { studentID: 4, firstName: 'Christopher', lastName: 'Monterroza' },
  { studentID: 5, firstName: 'Sophia', lastName: 'Praphan' }
]

function goToStudent(studentID) {
  // router.push(`/student/${studentID}`)
}
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
                :key="student.studentID"
                cols="12"
                sm="6"
                md="4"
              >
                <v-card
                  class="pa-2 text-center student-card"
                  flat
                  style="background-color: transparent; border: 1px solid #002856; border-radius: 8px;"
                  @click="goToStudent(student.studentID)"
                >
                  <v-card-title class="text-subtitle-3 font-weight-medium">
                    {{ student.firstName }} {{ student.lastName }}
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