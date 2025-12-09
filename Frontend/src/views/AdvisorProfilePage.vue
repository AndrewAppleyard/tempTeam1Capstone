<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user.js'
import AdvisorAPI from '../apis/AdvisorAPI.js'
import AppointmentAPI from '../apis/AppointmentAPI.js'
import StudentAPI from '../apis/StudentAPI.js' 

// --- Utility Functions ---
function formatPhoneNumber(rawNumber: string | null | undefined): string {
  if (!rawNumber) return 'N/A'
  const cleaned = ('' + rawNumber).replace(/\D/g, '')
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`
  }
  return rawNumber
}
function initials(f: string, l: string) { return `${f?.[0] ?? ''}${l?.[0] ?? ''}`.toUpperCase() }

/* Routing */
const route = useRoute()
const router = useRouter()
//const advisorIdParam = route.params.advisorID as string | undefined 

/* Store access */
const userStore = useUserStore()
const currentRoleID = computed(() => userStore.roleID) // advisorID
const fullName = computed(() => `${profile.firstName} ${profile.lastName}`)

/* Loading State */
const isLoading = ref(true)

/* --- DATA MODELS --- */
const profile = reactive({
  advisorID: '',
  firstName: '',
  lastName: '',
  title: '',
  department: '',
  officeLocation: '',
  email: '',
  phone: '',
  pronouns: '',
})

/* Advisor Stats */
const stats = reactive({
  totalStudents: 0,
  studentsOnHold: 0,
  avgStudentGPA: 0, // Placeholder
  nextAppt: '—',
})

/* Students */
interface StudentRow {
    id: string; 
    name: string; 
    major: string; 
    gpa: number; 
    standing: string;
    holds: boolean;
}
const studentLoad = ref<StudentRow[]>([])
const studentHeaders = [
  { title: 'ID', key: 'id' },
  { title: 'Name', key: 'name' },
  { title: 'Major', key: 'major' },
  { title: 'GPA', key: 'gpa' },
  { title: 'Standing', key: 'standing' },
  { title: 'Holds', key: 'holds' },
  { title: 'Actions', key: 'actions' },
]

/* Activity, Documents */
const recentActivity = ref<any[]>([]) // Recent advising notes/actions
const documents = ref<any[]>([]) // Advisor-specific documents (training certs)
const activityHeaders = [
    { title: 'Date', key: 'date' },
    { title: 'Student', key: 'student' },
    { title: 'Action/Note', key: 'action' },
]

/* --- DATA FETCHING LOGIC --- */

function mapAdvisorData(response: any) {
    const data = response.advisor || response;
    
    // --- Profile Data ---
    profile.advisorID = String(data.advisorid) || ''
    profile.firstName = data.firstname || ''
    profile.lastName = data.lastname || ''
    profile.title = data.title || 'Academic Advisor'
    profile.department = data.department || '—'
    profile.officeLocation = data.officeLocation || '—'
    
    // --- Contact Data ---
    profile.email = data.email || userStore.email || '' 
    profile.phone = String(data.phone) || '' 
    // profile.pronouns = data.pronouns || '' 
    
    fetchAdvisorStudents(profile.advisorID)
    fetchNextAppointment(profile.advisorID)
    // fetchRecentActivity(profile.advisorID) and fetchDocuments(profile.advisorID)
}

async function fetchAdvisorStudents(id: string) {
    let totalGPA = 0
    let studentsWithHold = 0
    
    try {
        const students = await StudentAPI.getStudentsByAdvisor(id)
        
        studentLoad.value = students.map((s: any) => {
            const gpa = Number(s.gpa || 0)
            const holds = !!s.advisinghold || !!s.financialhold || !!s.academichold

            if(gpa > 0) totalGPA += gpa
            if(holds) studentsWithHold++

            return {
                id: String(s.studentid),
                name: `${s.firstname} ${s.lastname}`,
                major: s.major || 'Undeclared',
                gpa: gpa,
                standing: s.advisingstatus === false ? 'Advising Hold' : (s.academichold ? 'Academic Hold' : 'Good Standing'),
                holds: holds
            }
        })
        
        stats.totalStudents = studentLoad.value.length
        stats.studentsOnHold = studentsWithHold
        stats.avgStudentGPA = stats.totalStudents > 0 ? totalGPA / stats.totalStudents : 0
        
    } catch (e) {
        console.error('Could not fetch advisor student load:', e)
        stats.totalStudents = 0
        stats.studentsOnHold = 0
        stats.avgStudentGPA = 0
        studentLoad.value = []
    }
}

// async function fetchNextAppointment(id: string) {
//   try {
//     const apptData = await AppointmentAPI.getNextAppointment(id) 
    
//     if (apptData.appointmentstatus === 'Scheduled' && apptData.starttime) {
//       const startTime = new Date(apptData.starttime)
      
//       const formattedTime = startTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
//       const formattedDate = startTime.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
      
//       stats.nextAppt = `${formattedDate} at ${formattedTime}`
      
//     } else {
//       stats.nextAppt = 'None Scheduled'
//     }
//   } catch (e) {
//     const errorMsg = String(e)
//     if (errorMsg.includes('404') || errorMsg.includes('No appointments')) {
//         stats.nextAppt = 'None Scheduled'
//     } else {
//         console.error('Could not fetch advisor next appointment:', e)
//         stats.nextAppt = 'Error Fetching'
//     }
//   }
// }


onMounted(async () => {
    await userStore.restoreLogin()
    if (!userStore.roleID) {
        console.error('User role ID not available. Cannot fetch profile.')
        isLoading.value = false
        return
    }

    const targetID = currentRoleID.value
    
    try {
        const advisorData = await AdvisorAPI.getAdvisorById(targetID)
        mapAdvisorData(advisorData)

    } catch (e) {
        console.error('Error fetching advisor profile data:', e)
        snack.show = true
        snack.message = 'Failed to load advisor profile data.'
        snack.color = 'error'
    } finally {
        isLoading.value = false
    }
})


type AdvisorTab = 'overview' | 'students' | 'activity' | 'documents'
const tab = ref<AdvisorTab>('overview')

/* Actions */
function printPage() { window.print() }
function viewStudent(studentId: string) { 
    router.push({ name: 'student-profile', params: { studentID: studentId } }) 
}

/* Edit dialog state */
const openEdit = ref(false)
const snack = reactive({ show: false, message: '', color: 'success' })
async function saveEdit() {
    snack.message = 'Save logic for Advisor not yet implemented.'
    snack.color = 'warning'
    snack.show = true
    openEdit.value = false
}
</script>

<template>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <v-row>
      <v-col cols="12" class="mx-auto profile-shell">
        <v-card class="pa-5 heavy-page"
                style="background-color:#BDD5E7;border:1px solid #002856;border-radius:16px;">
          
          <v-row class="mb-4" align="center" no-gutters>
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title class="py-2 px-3 title-chip">
                  ADVISOR PROFILE
                </v-card-title>
              </v-card>
            </v-col>

            <v-col cols="12" md="6"
                   class="d-flex justify-end align-center flex-wrap header-actions">
              <v-btn variant="outlined" color="#002856" @click="printPage">
                <v-icon start>mdi-printer</v-icon>
                Print / Save PDF
              </v-btn>
              <v-btn color="#0032A0" class="text-on-dark" @click="openEdit = true">
                <v-icon start>mdi-account-edit</v-icon>
                Edit
              </v-btn>
            </v-col>
          </v-row>

          <v-card class="pa-5 mb-5 glass-card">
            <v-row align="center">
              <v-col cols="12" md="3" class="d-flex align-center">
                <v-avatar size="112" class="brand-avatar">
                  <span class="text-h5" style="color:white">{{ initials(profile.firstName, profile.lastName) }}</span>
                </v-avatar>
                <div class="ml-4 text-left">
                  <div class="text-h6 mb-1 brand-primary">{{ fullName }}</div>
                  <div class="text-body-2">ID: <strong>{{ profile.advisorID }}</strong></div>
                  <div class="text-body-2">Title: <strong>{{ profile.title }}</strong></div>
                </div>
              </v-col>

              <v-col cols="12" md="6" class="brand-primary text-left">
                <v-row>
                  <v-col cols="12" sm="6" class="py-2">
                    <div class="text-caption mb-1">Department</div>
                    <div class="text-body-1"><strong>{{ profile.department || '—' }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-2">
                    <div class="text-caption mb-1">Office Location</div>
                    <div class="text-body-1"><strong>{{ profile.officeLocation || '—' }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-2">
                    <div class="text-caption mb-1">Email</div>
                    <div class="text-body-1"><strong>{{ profile.email }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-2">
                    <div class="text-caption mb-1">Phone</div>
                    <div class="text-body-1"><strong>{{ formatPhoneNumber(profile.phone) }}</strong></div>
                  </v-col>
                </v-row>
              </v-col>

              <v-col cols="12" md="3">
                <v-row>
                  <v-col cols="12" class="py-1 text-right brand-primary">
                    <div><strong>Students:</strong> {{ stats.totalStudents }}</div>
                    <div><strong>Holds:</strong> {{ stats.studentsOnHold }}</div>
                    <div><strong>Avg GPA:</strong> {{ Number(stats.avgStudentGPA).toFixed(2) }}</div>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" class="py-1 d-flex justify-end">
                    <div class="text-caption mr-2">Next Appointment:</div>
                    <v-chip color="success" variant="flat" size="large">{{ stats.nextAppt }}</v-chip>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card>

          <v-row class="mb-5" dense>
            <v-col cols="12" md="6" class="text-left">
              <v-card class="pa-5 glass-card">
                <div class="section-title mb-3">Student Load Summary</div>
                <div class="d-flex justify-space-between align-center mb-2">
                    <span class="text-body-1">Total Assigned Students:</span>
                    <strong class="text-h5 brand-primary">{{ stats.totalStudents }}</strong>
                </div>
                <v-divider class="my-2"/>
                <div class="d-flex justify-space-between align-center mb-2">
                    <span class="text-body-1">Students with Advising/Academic Holds:</span>
                    <strong class="text-h5 text-error">{{ stats.studentsOnHold }}</strong>
                </div>
                <v-divider class="my-2"/>
                <div class="d-flex justify-space-between align-center">
                    <span class="text-body-1">Average Student GPA:</span>
                    <strong class="text-h5 text-success">{{ Number(stats.avgStudentGPA).toFixed(2) }}</strong>
                </div>
              </v-card>
            </v-col>

            <v-col cols="12" md="6" class="text-left">
              <v-card class="pa-5 glass-card">
                <div class="section-title mb-3">Advisor Scheduling & Roles</div>
                <div class="d-flex align-center mb-2">
                  <v-icon class="mr-2">mdi-calendar-check</v-icon>
                  <span>Upcoming Appointment: **{{ stats.nextAppt }}**</span>
                </div>
                <div class="d-flex align-center mb-2">
                  <v-icon class="mr-2">mdi-clock-time-four-outline</v-icon>
                  <span>Office Hours: N/A</span> <!-- set variable for this -->
                </div>
              </v-card>
            </v-col>
          </v-row>

          <v-card class="pa-2 glass-card">
            <v-tabs v-model="tab" bg-color="transparent" class="px-2 bold-tabs">
              <v-tab value="overview"><v-icon start>mdi-view-dashboard</v-icon>Overview</v-tab>
              <v-tab value="students"><v-icon start>mdi-account-group</v-icon>My Students</v-tab>
              <v-tab value="activity"><v-icon start>mdi-history</v-icon>Recent Activity</v-tab>
              <v-tab value="documents"><v-icon start>mdi-file-document</v-icon>Documents</v-tab>
            </v-tabs>

            <v-window v-model="tab">
              <v-window-item value="overview" class="brand-primary text-left">
                <v-card flat class="pa-5">
                    <div class="text-body-1">Summary statistics and key performance indicators (KPIs) relevant to advising effectiveness and student success metrics are displayed here.</div>
                    <v-alert type="info" variant="tonal" class="mt-4">
                        This section can be populated with advising metrics like student retention rate, average time-to-graduation for your cohort, and advising appointment totals.
                    </v-alert>
                </v-card>
              </v-window-item>

              <v-window-item value="students" class="brand-primary text-left">
                <v-card flat class="pa-5">
                  <div class="section-title mb-3">Assigned Student Load ({{ studentLoad.length }} students)</div>
                  <v-data-table
                    :headers="studentHeaders"
                    :items="studentLoad"
                    item-key="id"
                    class="elevation-0 bigger-table"
                    density="comfortable"
                  >
                    <template #item.holds="{ item }">
                      <v-chip :color="item.holds ? 'error' : 'success'" variant="flat" size="small">
                        {{ item.holds ? 'YES' : 'No' }}
                      </v-chip>
                    </template>
                    <template #item.actions="{ item }">
                      <v-btn variant="text" size="small" @click="viewStudent(item.id)">
                        <v-icon start>mdi-eye</v-icon>View Profile
                      </v-btn>
                    </template>
                  </v-data-table>
                </v-card>
              </v-window-item>

              <v-window-item value="activity">
                <v-card flat class="pa-5 brand-primary text-left">
                  <div class="section-title mb-3">Recent Advising Notes & Actions</div>
                  <v-data-table
                    :headers="activityHeaders"
                    :items="recentActivity"
                    item-key="date"
                    class="elevation-0 bigger-table"
                    density="comfortable"
                  >
                    </v-data-table>
                </v-card>
              </v-window-item>

              <v-window-item value="documents" class="brand-primary text-left">
                <v-card flat class="pa-5">
                  <div class="section-title mb-3">Advisor Documents & Resources</div>
                  <v-data-table
                    :headers="['Name','Type','Updated','Actions']"
                    :items="documents"
                    item-key="name"
                    class="elevation-0 bigger-table"
                    density="comfortable"
                  >
                    <template #item.actions="{ item }">
                      <v-btn variant="text" size="small" @click="downloadDoc(item)">
                        <v-icon start>mdi-download</v-icon>Download
                      </v-btn>
                    </template>
                  </v-data-table>
                </v-card>
              </v-window-item>
            </v-window>
          </v-card>

        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="openEdit" max-width="880">
      <v-card>
        <v-card-title class="brand-primary">Edit Advisor Profile</v-card-title>
        <v-card-text>
            <div class="text-body-1 py-4">
                This is the placeholder for the editable advisor form. Fields would include Title, Department, Office Location, Phone, and other professional details.
            </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="openEdit=false">Cancel</v-btn>
          <v-btn color="#0032A0" class="text-on-dark" @click="saveEdit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snack.show" :color="snack.color" timeout="2500">
      {{ snack.message }}
    </v-snackbar>
  </v-container>
</template>