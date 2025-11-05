<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import StudentFormCard from '../components/StudentFormCard.vue'
import Popups from '../components/Popups.vue'
import { VIcon } from 'vuetify/components'

const router = useRouter()
const loading = ref(true)
const error = ref(null)
const students = ref([]) 

async function fetchStudents() {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/Advisor/Student/1') // change based off of advisor id
    
    students.value = response.data.sort((a, b) => {
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
    error.value = 'Failed to load students.'
  } finally {
    loading.value = false
  }
}

function goToStudent(studentid) {
  router.push(`/student/${studentid}`)
}

function hasInfo(student) {
  return student.advisinghold || student.academichold || student.financialhold || student.advisingstatus || student.registrationstatus
}

function getCardStyle(student) {
  const hasHold = student.advisinghold || student.academichold || student.financialhold
  const advising = student.advisingstatus

  let bg = 'transparent'
  if (hasHold) bg = '#FF746C' 
  else if (advising) bg = '#ADEBB3' 

  return {
    backgroundColor: bg,
    border: '1px solid #002856',
    borderRadius: '8px'
  }
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
                  :style="getCardStyle(student)"
                  @click="goToStudent(student.studentid)"
                >
                  <v-card-title class="text-subtitle-3 font-weight-medium">
                    {{ student.firstname }} {{ student.lastname }}

                    <v-tooltip location="top">
                      <template #activator="{ props }">
                        <v-icon
                          v-if="hasInfo(student)"
                          v-bind="props"
                          size="18"
                          color="#002856"
                          class="cursor-pointer"
                        >
                          mdi-information-outline
                        </v-icon>
                      </template>

                      <div style="white-space: pre-line; font-size: 0.85rem;">
                        <strong>Advising Hold:</strong> {{ student.advisinghold ? 'Yes' : 'No' }}<br>
                        <strong>Academic Hold:</strong> {{ student.academichold ? 'Yes' : 'No' }}<br>
                        <strong>Financial Hold:</strong> {{ student.financialhold ? 'Yes' : 'No' }}<br>
                        <strong>Advising Status:</strong> {{ student.advisingstatus || 'N/A' }}<br>
                        <strong>Registration Status:</strong> {{ student.registrationstatus || 'N/A' }}
                      </div>
                    </v-tooltip>
                  </v-card-title>

                  <v-card-subtitle v-if="student.dateadvised" class="text-caption" style="color: black;">
                    {{
                      new Date(student.dateadvised) > new Date()
                        ? `Upcoming advising appointment: ${new Date(student.dateadvised).toLocaleDateString()}`
                        : `Advised on: ${new Date(student.dateadvised).toLocaleDateString()}`
                    }}
                  </v-card-subtitle>
                  
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>