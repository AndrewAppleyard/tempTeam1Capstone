<template>
  <v-container fluid class="pa-1" style="background-color: transparent;">
    <v-row justify="center">
      <v-col cols="12">
        <v-card class="pa-4" style="background-color:#BDD5E7;border:1px solid #002856;border-radius:12px;">
          <!-- Header / Title -->
          <v-row class="mb-3" text-align="center">
            <v-col cols="12" md="6">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title class="py-2 px-3" style="color:#002856;border:1px solid #002856;border-radius:4px;">
                  USER PROFILE
                </v-card-title>
              </v-card>
            </v-col>

            <v-col cols="12" md="6" class="d-flex justify-end align-center gap-2">
              <v-btn variant="outlined" :ripple="false" class="mr-2" color="#002856" @click="goBack">
                <v-icon start>mdi-arrow-left</v-icon>
                Back to Students
              </v-btn>
              <v-btn variant="outlined" color="#002856" class="mr-2" @click="printPage">
                <v-icon start>mdi-printer</v-icon>
                Print / Save PDF
              </v-btn>
              <v-btn color="#002856" style="color:white" class="mr-2" @click="downloadVCF">
                <v-icon start>mdi-card-account-phone</v-icon>
                Export vCard
              </v-btn>
              <v-btn color="#002856" style="color:white" @click="openEdit=true">
                <v-icon start>mdi-account-edit</v-icon>
                Edit
              </v-btn>
            </v-col>
          </v-row>

          <!-- Profile Summary -->
          <v-card class="pa-4 mb-4" style="background-color:rgba(255,255,255,.6);border:1px solid #002856;">
            <v-row align="center">
              <v-col cols="12" md="3" class="d-flex align-center">
                <v-avatar size="96" color="#002856">
                  <span class="text-h5" style="color:white">{{ initials(profile.firstName, profile.lastName) }}</span>
                </v-avatar>
                <div class="ml-4" style="text-align:left;">
                  <div class="text-h6 mb-1" style="color:#002856;">{{ fullName }}</div>
                  <div class="text-body-2">ID: <strong>{{ profile.studentID }}</strong></div>
                  <div class="text-body-2">Level: <strong>{{ profile.level }}</strong></div>
                </div>
              </v-col>

              <v-col cols="12" md="6">
                <v-row class="gap-4">
                  <v-col cols="12" sm="6" class="py-1">
                    <div class="text-caption mb-1">Major</div>
                    <div class="text-body-1"><strong>{{ profile.major || '—' }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-1">
                    <div class="text-caption mb-1">Minor</div>
                    <div class="text-body-1"><strong>{{ profile.minor || '—' }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-1">
                    <div class="text-caption mb-1">Expected Graduation</div>
                    <div class="text-body-1"><strong>{{ profile.gradTerm }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-1">
                    <div class="text-caption mb-1">Academic Standing</div>
                    <div class="text-body-1"><strong>{{ profile.standing }}</strong></div>
                  </v-col>
                </v-row>
              </v-col>

              <v-col cols="12" md="3">
                <v-row>
                  <v-col cols="12" class="py-1 text-right">
                    <div><strong>Total Credits:</strong> {{ stats.totalCredits }}</div>
                    <div><strong>Cumulative GPA:</strong> {{ stats.gpa.toFixed(2) }}</div>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" class="py-0 d-flex justify-end">
                    <v-progress-circular :model-value="progressPercent" size="72" width="10">
                      {{ Math.round(progressPercent) }}%
                    </v-progress-circular>
                  </v-col>
                  <v-col cols="12" class="pt-0 text-right">
                    <div class="text-caption">Degree Progress</div>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card>

          <!-- Quick Info -->
          <v-row class="mb-4">
            <v-col cols="12" md="4">
              <v-card class="pa-4" style="background-color:rgba(255,255,255,.6);border:1px solid #002856;">
                <div class="text-subtitle-1 mb-3" style="color:#002856;">Contact</div>
                <div class="d-flex align-center mb-2">
                  <v-icon class="mr-2">mdi-email</v-icon>
                  <a :href="`mailto:${profile.email}`">{{ profile.email }}</a>
                </div>
                <div class="d-flex align-center mb-2">
                  <v-icon class="mr-2">mdi-phone</v-icon>
                  <a :href="`tel:${profile.phone}`">{{ profile.phone }}</a>
                </div>
                <div class="d-flex align-center mb-2">
                  <v-icon class="mr-2">mdi-map-marker</v-icon>
                  <span>{{ profile.address }}</span>
                </div>
                <div class="d-flex align-center">
                  <v-icon class="mr-2">mdi-account</v-icon>
                  <span>Pronouns: {{ profile.pronouns || '—' }}</span>
                </div>
              </v-card>
            </v-col>

            <v-col cols="12" md="4">
              <v-card class="pa-4" style="background-color:rgba(255,255,255,.6);border:1px solid #002856;">
                <div class="text-subtitle-1 mb-3" style="color:#002856;">Advisor</div>
                <div class="mb-1"><strong>{{ advisor.name }}</strong></div>
                <div class="mb-2">{{ advisor.title }}</div>
                <div class="d-flex align-center mb-2">
                  <v-icon class="mr-2">mdi-email</v-icon>
                  <a :href="`mailto:${advisor.email}`">{{ advisor.email }}</a>
                </div>
                <div class="d-flex align-center">
                  <v-icon class="mr-2">mdi-calendar-clock</v-icon>
                  <span>Next appt: {{ advisor.nextAppt }}</span>
                </div>
              </v-card>
            </v-col>

            <v-col cols="12" md="4">
              <v-card class="pa-4" style="background-color:rgba(255,255,255,.6);border:1px solid #002856;">
                <div class="text-subtitle-1 mb-3" style="color:#002856;">Tags & Badges</div>
                <div class="d-flex flex-wrap gap-2">
                  <v-chip v-for="t in tags" :key="t" class="ma-1" variant="outlined" color="#002856">{{ t }}</v-chip>
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- Tabs -->
          <v-card class="pa-2" style="background-color:rgba(255,255,255,.6);border:1px solid #002856;">
            <v-tabs v-model="tab" bg-color="transparent" class="px-2">
              <!-- Back to Students tab -->
              <v-tab value="students">
                <v-icon start>mdi-arrow-left</v-icon>Students
              </v-tab>
              <v-tab value="overview"><v-icon start>mdi-view-dashboard</v-icon>Overview</v-tab>
              <v-tab value="academics"><v-icon start>mdi-school</v-icon>Academics</v-tab>
              <v-tab value="involvement"><v-icon start>mdi-account-group</v-icon>Involvement</v-tab>
              <v-tab value="documents"><v-icon start>mdi-file-document</v-icon>Documents</v-tab>
            </v-tabs>

            <v-window v-model="tab">
              <!-- Overview -->
              <v-window-item value="overview">
                <v-card flat class="pa-4">
                  <div class="text-subtitle-1 mb-3" style="color:#002856; text-align: left;">Recent Activity</div>
                  <v-timeline align="start" density="compact">
                    <v-timeline-item v-for="item in activity" :key="item.id" :dot-color="item.color" :icon="item.icon">
                      <div class="mb-1"><strong>{{ item.title }}</strong></div>
                      <div class="text-caption">{{ item.when }}</div>
                    </v-timeline-item>
                  </v-timeline>
                </v-card>
              </v-window-item>

              <!-- Academics -->
              <v-window-item value="academics">
                <v-card flat class="pa-4">
                  <div class="text-subtitle-1 mb-3" style="color:#002856;">Current & Recent Courses</div>
                  <v-data-table :headers="courseHeaders" :items="recentCourses" item-key="id" class="elevation-0">
                    <template #item.points="{ item }">
                      <span>{{ (item.credits * gradePoint(item.grade)).toFixed(2) }}</span>
                    </template>
                  </v-data-table>
                </v-card>
              </v-window-item>

              <!-- Involvement (forced left alignment) -->
              <v-window-item value="involvement">
                <v-card flat class="pa-4">
                  <div class="text-subtitle-1 mb-3" style="color:#002856; text-align:left;">Organizations & Roles</div>
                  <v-list lines="two" class="text-left" style="text-align:left;">
                    <v-list-item
                      v-for="org in orgs"
                      :key="org.id"
                      :title="org.name"
                      :subtitle="org.role + ' • ' + org.since"
                      prepend-icon="mdi-shield-account"
                    />
                  </v-list>
                </v-card>
              </v-window-item>

              <!-- Documents -->
              <v-window-item value="documents">
                <v-card flat class="pa-4">
                  <div class="text-subtitle-1 mb-3" style="color:#002856;">Files</div>
                  <v-data-table :headers="docHeaders" :items="documents" item-key="id" class="elevation-0">
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

    <!-- Edit Dialog -->
    <v-dialog v-model="openEdit" max-width="560">
      <v-card>
        <v-card-title>Edit Profile</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveEdit">
            <v-text-field v-model="editable.email" label="Email" prepend-inner-icon="mdi-email" type="email"/>
            <v-text-field v-model="editable.phone" label="Phone" prepend-inner-icon="mdi-phone"/>
            <v-text-field v-model="editable.address" label="Address" prepend-inner-icon="mdi-map-marker"/>
            <v-text-field v-model="editable.pronouns" label="Pronouns" prepend-inner-icon="mdi-account"/>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn variant="text" @click="openEdit=false">Cancel</v-btn>
          <v-btn color="#002856" style="color:white" @click="saveEdit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// GPA map
const GPA_POINTS: Record<string, number> = {
  'A': 4.0, 'A-': 3.7,
  'B+': 3.3, 'B': 3.0, 'B-': 2.7,
  'C+': 2.3, 'C': 2.0, 'C-': 1.7,
  'D+': 1.3, 'D': 1.0,
  'F': 0.0, 'P': 0.0, 'W': 0.0, 'I': 0.0,
}
const gradePoint = (g: string) => GPA_POINTS[g] ?? 0

// Routing
const route = useRoute()
const router = useRouter()
const studentIdParam = route.params.studentID as string | undefined

// Profile data
const profile = reactive({
  studentID: studentIdParam || 'S1002',
  firstName: 'Andrew',
  lastName: 'Mackey',
  level: 'Undergraduate',
  major: 'Computer Science',
  minor: 'Mathematics',
  gradTerm: 'Spring 2026',
  standing: 'Good Standing',
  email: 'amackey@uafs.edu',
  phone: '(479) 555-1234',
  address: '5210 Grand Ave, Fort Smith, AR',
  pronouns: 'he/him',
})

// Stats
const stats = reactive({
  totalCredits: 86,
  gpa: 3.64,
  degreeCredits: 120,
})
const progressPercent = computed(() => (stats.totalCredits / stats.degreeCredits) * 100)

// Advisor
const advisor = reactive({
  name: 'Dr. Dave Stevens',
  title: 'Dean of Students',
  email: 'dave.stevens@uafs.edu',
  nextAppt: 'Nov 4, 2025 • 2:30 PM',
})

// Tags
const tags = ref<string[]>(['IFC President', 'Sigma Nu', 'Dean\'s List', 'Senior'])

// Activity timeline
const activity = ref([
  { id: 'a1', title: 'Submitted Degree Audit', when: 'Oct 20, 2025', icon: 'mdi-check-circle', color: 'primary' },
  { id: 'a2', title: 'Advising Session Completed', when: 'Oct 14, 2025', icon: 'mdi-account-tie', color: 'primary' },
  { id: 'a3', title: 'Enrolled in Spring 2026', when: 'Oct 10, 2025', icon: 'mdi-calendar-plus', color: 'primary' },
])

// Recent courses section
interface CourseRow { id: string; term: string; code: string; title: string; credits: number; grade: string }
const recentCourses = ref<CourseRow[]>([
  { id: 'r1', term: 'Fall 2025', code: 'CS 4013', title: 'Operating Systems', credits: 3, grade: 'A' },
  { id: 'r2', term: 'Fall 2025', code: 'CS 4113', title: 'Database Systems', credits: 3, grade: 'A-' },
  { id: 'r3', term: 'Fall 2025', code: 'CS 4213', title: 'Networks', credits: 3, grade: 'B+' },
  { id: 'r4', term: 'Fall 2025', code: 'MATH 3403', title: 'Linear Algebra', credits: 3, grade: 'A' },
])

const courseHeaders = [
  { title: 'Term', key: 'term', sortable: true },
  { title: 'Course #', key: 'code', sortable: true },
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Credits', key: 'credits', sortable: true, align: 'end' },
  { title: 'Grade', key: 'grade', sortable: true, align: 'center' },
  { title: 'Points', key: 'points', align: 'end' },
]

// Involvement
const orgs = ref([
  { id: 'o1', name: 'Interfraternity Council', role: 'President', since: '2025' },
  { id: 'o2', name: 'Sigma Nu', role: 'Member', since: '2023' },
  { id: 'o3', name: 'UAFS AI Society', role: 'Co-founder', since: '2024' },
])

// Documents
interface DocRow { id: string; name: string; type: string; updated: string; size: string }
const documents = ref<DocRow[]>([
  { id: 'd1', name: 'Unofficial_Transcript.pdf', type: 'PDF', updated: 'Oct 22, 2025', size: '142 KB' },
  { id: 'd2', name: 'Degree_Audit.pdf', type: 'PDF', updated: 'Oct 20, 2025', size: '228 KB' },
  { id: 'd3', name: 'Resume_YashPatel.pdf', type: 'PDF', updated: 'Oct 08, 2025', size: '198 KB' },
])

const docHeaders = [
  { title: 'Name', key: 'name' },
  { title: 'Type', key: 'type', align: 'center' },
  { title: 'Updated', key: 'updated', align: 'center' },
  { title: 'Size', key: 'size', align: 'end' },
  { title: '', key: 'actions', align: 'end' },
]

// Tabs + back-to-students behavior
type RealTab = 'overview' | 'academics' | 'involvement' | 'documents'
type AnyTab = RealTab | 'students'
const tab = ref<AnyTab>('overview')
const lastRealTab = ref<RealTab>('overview')

watch(tab, (next) => {
  if (next === 'students') {
    goBack()
    tab.value = lastRealTab.value
  } else {
    lastRealTab.value = next as RealTab
  }
})

// Edit dialog state
const openEdit = ref(false)
const editable = reactive({ email: profile.email, phone: profile.phone, address: profile.address, pronouns: profile.pronouns })

// Computed helpers
const fullName = computed(() => `${profile.firstName} ${profile.lastName}`)
function initials(f: string, l: string) { return `${f?.[0] ?? ''}${l?.[0] ?? ''}`.toUpperCase() }

// Actions
function goBack() {
  if (router && router.currentRoute.value.name !== 'students') {
    router.push({ name: 'students' }).catch(() => window.history.back())
  } else {
    window.history.back()
  }
}
function printPage() { window.print() }

function downloadVCF() {
  const vcf = [
    'BEGIN:VCARD',
    'VERSION:3.0',
    `N:${profile.lastName};${profile.firstName};;;`,
    `FN:${fullName.value}`,
    `EMAIL;TYPE=INTERNET:${profile.email}`,
    `TEL;TYPE=CELL:${profile.phone}`,
    `ADR;TYPE=HOME:;;${profile.address};;;;`,
    'ORG:UAFS',
    'TITLE:Student',
    'END:VCARD'
  ].join('\n')

  const blob = new Blob([vcf], { type: 'text/vcard;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${profile.studentID}_${profile.lastName}.vcf`
  a.click()
  URL.revokeObjectURL(url)
}

function downloadDoc(item: DocRow) {
  // Placeholder: wire up to your backend/download URL
  alert(`Downloading: ${item.name}`)
}

function saveEdit() {
  Object.assign(profile, editable)
  openEdit.value = false
}
</script>

<style scoped>
.student-card{cursor:pointer;transition:transform .15s ease, box-shadow .15s ease}
.student-card:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.15)}

@media print{
  .v-btn,.v-select,.v-text-field,.v-tabs{display:none!important}
  body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .v-card{box-shadow:none!important}
}

/* utilities */
.gap-2{gap:.5rem}
.gap-4{gap:1rem}
</style>
