<script setup>
import { useViewModeStore } from '../store/pinia.js'
import { storeToRefs } from 'pinia'

const store = useViewModeStore()
const { viewMode } = storeToRefs(store)

const advisors = [
  { advisorID: 1, firstName: 'Andrew', lastName: 'Mackey' },
  { advisorID: 2, firstName: 'Israel', lastName: 'Cuevas' },
  { advisorID: 3, firstName: 'Brittany', lastName: 'Bright' },
  { advisorID: 4, firstName: 'John', lastName: 'Hightower' },
  { advisorID: 5, firstName: 'Brian', lastName: 'McLaughlan' }
]

const students = [
  { studentID: 1, firstName: 'Yash', lastName: 'Patel' },
  { studentID: 2, firstName: 'Andrew', lastName: 'Appleyard' },
  { studentID: 3, firstName: 'Robert', lastName: 'Farrar' },
  { studentID: 4, firstName: 'Christopher', lastName: 'Monterroza' },
  { studentID: 5, firstName: 'Sophia', lastName: 'Praphan' }
]

// placeholder
// function goToAdvisor(id) { // shows list of students assigned to advisor
//   console.log('Clicked Advisor:', id)
// }

function goToUser(id) {
  console.log('Clicked User:', id)
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
                  LIST OF {{ viewMode === 'students' ? 'STUDENTS' : 'ADVISORS' }}
                </v-card-title>
              </v-card>
            </v-col>
          </v-row>

          <v-card-text>
            <v-row>
              <v-col
                v-for="item in (viewMode === 'students' ? students : advisors)"
                :key="item[viewMode === 'students' ? 'studentID' : 'advisorID']"
                cols="12"
                sm="6"
                md="4"
              >
                <v-card
                  class="pa-2 text-center student-card"
                  flat
                  style="background-color: transparent; border: 1px solid #002856; border-radius: 8px;"
                  @click="goToUser(item.studentID || item.advisorID)"
                >
                  <v-card-title class="text-subtitle-3 font-weight-medium">
                    {{ item.firstName }} {{ item.lastName }}
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