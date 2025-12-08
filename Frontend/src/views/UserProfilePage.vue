<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user.js'
import StudentAPI from '../apis/StudentAPI.js'
import AdvisorAPI from '../apis/AdvisorAPI.js'

/* GPA map */
const GPA_POINTS: Record<string, number> = {
  'A': 4.0,
  'B': 3.0,
  'C': 2.0,
  'D': 1.0,
  'F': 0.0, 'P': 0.0, 'W': 0.0, 'I': 0.0,
}
const gradePoint = (g: string) => GPA_POINTS[g] ?? 0

/* Routing */
const route = useRoute()
const router = useRouter()
const studentIdParam = route.params.studentID as string | undefined

/* Store access */
const userStore = useUserStore() // <-- Initialize the store
const isStudentRole = computed(() => userStore.userRole === 'UAFS_STUDENTS')
const isAdvisorRole = computed(() => userStore.userRole === 'UAFS_ADVISORS')
const currentRoleID = computed(() => userStore.roleID) // studentID or advisorID

/* Loading State */
const isLoading = ref(true)

/* --- DATA MODELS --- */

/* Profile data */
const profile = reactive({
  studentID: '',
  firstName: '',
  lastName: '',
  level: '',
  major: '',
  minor: '',
  gradTerm: '',
  standing: '',
  email: '',
  phone: '',
  address: '',
  pronouns: '',
})

/* Stats */
const stats = reactive({
  totalCredits: 0,
  gpa: 0,
  degreeCredits: 120,
})
const progressPercent = computed(() => (stats.totalCredits / stats.degreeCredits) * 100)

/* Advisor */
const advisor = reactive({
  name: '—',
  title: '—',
  email: '—',
  nextAppt: '—', // would need to add value in db for appointment date, datepicker that sends email
})

/* Tags, Activity, Courses, Involvement, Documents */
const tags = ref<string[]>([])
const tagOptions = ref<string[]>([
  'IFC President','Sigma Nu','Dean\'s List','Senior','Athlete','Honors','Mentor'
])
const activity = ref<any[]>([]) // Placeholder for activity, not in provided APIs
const recentCourses = ref<CourseRow[]>([])
interface CourseRow { id: string; term: string; code: string; title: string; credits: number; grade: string }
const orgs = ref<any[]>([]) // Placeholder for involvement, not in provided APIs
interface DocRow { id: string; name: string; type: string; updated: string; size: string }
const documents = ref<DocRow[]>([])


/* --- DATA FETCHING LOGIC --- */
function mapStudentData(response: any) {
    const studentData = response.student || response; 
    const transcriptData = response.transcript || {};
    
    // --- Profile Data ---
    profile.studentID = String(studentData.studentid) || studentIdParam || ''
    profile.firstName = studentData.firstname || ''
    profile.lastName = studentData.lastname || ''
    profile.level = studentData.classstanding || transcriptData.year || 'Undergraduate'
    
    profile.major = studentData.major || transcriptData.program || ''
    profile.minor = studentData.minor || '' 
    
    // Grad term and standing are placeholders
    profile.gradTerm = '' 
    profile.standing = studentData.advisingstatus === false ? 'Advising Hold' : 'Good Standing' 
    
    // --- Contact Data ---
    profile.email = studentData.email || userStore.email || '' 
    profile.phone = String(studentData.phonenumber) || '' 
    profile.address = studentData.address || '' // 'address' field is not in this output
    profile.pronouns = studentData.pronouns || '' // 'pronouns' field is not in this output
    
    // --- Stats Data ---
    stats.totalCredits = 0 // 'totalCredits' field from transcript
    stats.gpa = parseFloat(studentData.gpa || transcriptData.cumulativegpa || 0)
    
    tags.value = studentData.tags || []

    fetchStudentDocuments(profile.studentID)
    fetchStudentAdvisor(profile.studentID)
}


function mapAdvisorData(response: any) {
    const data = response.advisor || response;

    profile.studentID = data.advisorid // using studentID field to hold advisor ID
    profile.firstName = data.firstname || ''
    profile.lastName = data.lastname || ''
    profile.email = userStore.email || '' 
    profile.phone = data.phone || ''
    profile.address = data.officeLocation || '' // no office location
    profile.level = 'Advisor'
    profile.major = '—'
    
    advisor.name = `${data.firstname} ${data.lastname}`
    advisor.title = data.title || 'Academic Advisor'
    advisor.email = data.email || ''
    
    // Tags, Stats, Courses, Documents not relevant for an advisor
    tags.value = []
    stats.totalCredits = 0
    stats.gpa = 0
}

async function fetchStudentAdvisor(id: string) {
    try {
        const advisorData = await AdvisorAPI.getAdvisorByStudent(id)
        advisor.name = `${advisorData.firstname} ${advisorData.lastname}`
        advisor.title = advisorData.title || 'Academic Advisor'
        advisor.email = advisorData.email
        // nextAppt hardcoded placeholder for now
    } catch (e) {
        console.error('Could not fetch student advisor:', e)
        advisor.name = 'No Advisor Assigned'
        advisor.email = ''
    }
}

async function fetchStudentDocuments(id: string) {
    try {
        const transcripts = await StudentAPI.getTranscripts(id)
        documents.value = transcripts.map((t: any, index: number) => ({
            id: t.id || `d${index}`,
            name: t.name || `${t.type}_Transcript.pdf`,
            type: t.type || 'PDF',
            updated: t.updatedDate || new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }),
            size: t.size || 'N/A'
        }))
    } catch (e) {
        console.error('Could not fetch student transcripts:', e)
        documents.value = []
    }
}


onMounted(async () => {
    await userStore.restoreLogin()
    if (!userStore.roleID) {
        console.error('User role ID not available. Cannot fetch profile.')
        isLoading.value = false
        return
    }

    const targetID = studentIdParam || currentRoleID.value
    
    try {
        if (studentIdParam || isStudentRole.value) {
            const studentData = await StudentAPI.getStudentById(targetID)
            mapStudentData(studentData)

            // NOTE: Courses and Activity are left as placeholder/initial data for now, 
            // but in a real app, you would fetch those using other APIs.
            // Example: recentCourses.value = await StudentAPI.getRecentCourses(targetID)

        } else if (isAdvisorRole.value && !studentIdParam) {
            const advisorData = await AdvisorAPI.getAdvisorById(targetID)
            mapAdvisorData(advisorData)

        } else {
            console.warn('Unknown role or missing ID. Cannot fetch profile.')
        }

    } catch (e) {
        console.error('Error fetching profile data:', e)
        snack.show = true
        snack.message = 'Failed to load user profile data.'
        snack.color = 'error'
    } finally {
        isLoading.value = false
    }
})


/* Tabs + back-to-students behavior */
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

/* Edit dialog state */
const openEdit = ref(false)
const editForm = ref()
const editValid = ref(false)
const rules = {
  required: (v: unknown) => (v !== null && v !== undefined && String(v).trim().length > 0) || 'Required',
  email: (v: string) => (!v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) || 'Invalid email',
}
const editable = reactive({
  // identity
  studentID: profile.studentID,
  firstName: profile.firstName,
  lastName: profile.lastName,
  level: profile.level,
  // academics
  major: profile.major,
  minor: profile.minor,
  gradTerm: profile.gradTerm,
  standing: profile.standing,
  totalCredits: stats.totalCredits,
  gpa: stats.gpa,
  // contact
  email: profile.email,
  phone: profile.phone,
  address: profile.address,
  pronouns: profile.pronouns,
  // tags
  tags: [...tags.value],
})

watch([profile, stats, tags], () => {
  editable.studentID = profile.studentID
  editable.firstName = profile.firstName
  editable.lastName = profile.lastName
  editable.level = profile.level
  editable.major = profile.major
  editable.minor = profile.minor
  editable.gradTerm = profile.gradTerm
  editable.standing = profile.standing
  editable.totalCredits = stats.totalCredits
  editable.gpa = stats.gpa
  editable.email = profile.email
  editable.phone = profile.phone
  editable.address = profile.address
  editable.pronouns = profile.pronouns
  editable.tags = [...tags.value]
})

/* Computed helpers */
const fullName = computed(() => `${profile.firstName} ${profile.lastName}`)
function initials(f: string, l: string) { return `${f?.[0] ?? ''}${l?.[0] ?? ''}`.toUpperCase() }

/* Actions */
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
  // Hook to real endpoint when ready
  alert(`Downloading: ${item.name}`)
}

/* Save edit — updates all fields */
const snack = reactive({ show: false, message: '', color: 'success' })
async function saveEdit() {
  const res = await editForm.value?.validate()
  if (!res?.valid) {
    snack.show = true
    snack.message = 'Please fix form errors.'
    snack.color = 'error'
    return
  }

  // API Update Logic
  try {
    const updates = {
      // Identity
      firstname: editable.firstName,
      lastname: editable.lastName,
      // studentid: editable.studentID, // Usually immutable
      level: editable.level,
      // Academics
      major: editable.major,
      minor: editable.minor,
      gradterm: editable.gradTerm,
      standing: editable.standing,
      totalCredits: editable.totalCredits,
      gpa: editable.gpa,
      // Contact
      email: editable.email,
      phone: editable.phone,
      address: editable.address,
      pronouns: editable.pronouns,
      // Tags
      tags: editable.tags,
    }

    if (isStudentRole.value || studentIdParam) {
      await StudentAPI.updateStudent(editable.studentID, updates)
      
      profile.firstName = editable.firstName
      profile.lastName = editable.lastName
      profile.level = editable.level
      profile.major = editable.major
      profile.minor = editable.minor
      profile.gradTerm = editable.gradTerm
      profile.standing = editable.standing
      stats.totalCredits = Number(editable.totalCredits) || 0
      stats.gpa = Math.max(0, Math.min(4, Number(editable.gpa) || 0))
      profile.email = editable.email
      profile.phone = editable.phone
      profile.address = editable.address
      profile.pronouns = editable.pronouns
      tags.value = [...editable.tags]

      snack.message = 'Profile updated.'
    } else {
        snack.message = 'Only student profiles can be updated here.'
        snack.color = 'warning'
    }

  } catch (e) {
      console.error('Save failed:', e)
      snack.message = 'Error updating profile.'
      snack.color = 'error'
  } finally {
      openEdit.value = false
      snack.show = true
      snack.color = snack.color === 'error' ? 'error' : 'success'
  }
}
</script>

<style scoped>
/* 95% width shell, centered */
.profile-shell {
  width: 95%;
  margin-left: auto;
  margin-right: auto;
}

/* Heavier but not flashy */
.heavy-page {
  font-size: 1.06rem;
  line-height: 1.55;
}

/* Brand helpers */
.brand-primary { color: #002856; }
.text-on-dark { color: #F5F5F5 !important; }
.brand-avatar { background:#002856; border:1px solid #002856; }

/* Chips / Title */
.title-chip {
  color:#002856;
  border:1px solid #002856;
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: .25px;
  font-size: 1.15rem;
}

/* Section titles */
.section-title {
  color:#002856;
  font-weight: 650;
  font-size: 1.15rem;
}
.section-sub {
  color:#002856;
  font-weight: 650;
  font-size: 1.05rem;
}

/* Header buttons spacing */
.header-actions > .v-btn {
  margin-left: 10px;
  margin-top: 8px;
}
.header-actions { gap: 10px; }

/* Subtle glass card look */
.glass-card {
  background-color: rgba(255,255,255,.6);
  border: 1px solid #002856;
  border-radius: 12px;
}

/* Tabs a bit bolder */
.bold-tabs .v-tab {
  font-weight: 600;
  font-size: 1.02rem;
}

/* Data tables a bit bigger */
.bigger-table .v-data-table-header__content,
.bigger-table .v-data-table__td {
  font-size: 1.02rem;
}

/* Print */
@media print {
  .v-btn, .v-select, .v-text-field, .v-tabs { display:none !important }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact }
  .v-card { box-shadow: none !important }
}
</style>

<template>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <v-row>
      <!-- 95% width shell, centered -->
      <v-col cols="12" class="mx-auto profile-shell">
        <v-card class="pa-5 heavy-page"
                style="background-color:#BDD5E7;border:1px solid #002856;border-radius:16px;">
          <!-- Header / Title -->
          <v-row class="mb-4" align="center" no-gutters>
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title class="py-2 px-3 title-chip">
                  USER PROFILE
                </v-card-title>
              </v-card>
            </v-col>

            <v-col cols="12" md="6"
                   class="d-flex justify-end align-center flex-wrap header-actions">
              <v-btn variant="outlined" :ripple="false" color="#002856" @click="goBack">
                <v-icon start>mdi-arrow-left</v-icon>
                Back
              </v-btn>
              <v-btn variant="outlined" color="#002856" @click="printPage">
                <v-icon start>mdi-printer</v-icon>
                Print / Save PDF
              </v-btn>
              <v-btn color="#002856" class="text-on-dark" @click="downloadVCF">
                <v-icon start>mdi-card-account-phone</v-icon>
                Export vCard
              </v-btn>
              <v-btn color="#0032A0" class="text-on-dark" @click="openEdit = true">
                <v-icon start>mdi-account-edit</v-icon>
                Edit
              </v-btn>
            </v-col>
          </v-row>

          <!-- Profile Summary -->
          <v-card class="pa-5 mb-5 glass-card">
            <v-row align="center">
              <v-col cols="12" md="3" class="d-flex align-center">
                <v-avatar size="112" class="brand-avatar">
                  <span class="text-h5" style="color:white">{{ initials(profile.firstName, profile.lastName) }}</span>
                </v-avatar>
                <div class="ml-4 text-left">
                  <div class="text-h6 mb-1 brand-primary">{{ fullName }}</div>
                  <div class="text-body-2">ID: <strong>{{ profile.studentID }}</strong></div>
                  <div class="text-body-2">Level: <strong>{{ profile.level }}</strong></div>
                </div>
              </v-col>

              <v-col cols="12" md="6" class="brand-primary text-left">
                <v-row>
                  <v-col cols="12" sm="6" class="py-2">
                    <div class="text-caption mb-1">Major</div>
                    <div class="text-body-1"><strong>{{ profile.major || '—' }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-2">
                    <div class="text-caption mb-1">Minor</div>
                    <div class="text-body-1"><strong>{{ profile.minor || '—' }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-2">
                    <div class="text-caption mb-1">Expected Graduation</div>
                    <div class="text-body-1"><strong>{{ profile.gradTerm }}</strong></div>
                  </v-col>
                  <v-col cols="12" sm="6" class="py-2">
                    <div class="text-caption mb-1">Academic Standing</div>
                    <div class="text-body-1"><strong>{{ profile.standing }}</strong></div>
                  </v-col>
                </v-row>
              </v-col>

              <v-col cols="12" md="3">
                <v-row>
                  <v-col cols="12" class="py-1 text-right brand-primary">
                    <div><strong>Total Credits:</strong> {{ stats.totalCredits }}</div>
                    <div><strong>Cumulative GPA:</strong> {{ Number(stats.gpa).toFixed(2) }}</div>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" class="py-1 d-flex justify-end">
                    <v-progress-circular :model-value="progressPercent" size="84" width="10">
                      {{ Math.round(progressPercent) }}%
                    </v-progress-circular>
                  </v-col>
                  <v-col cols="12" class="pt-0 text-right brand-primary">
                    <div class="text-caption">Degree Progress</div>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card>

          <!-- Quick Info -->
          <v-row class="mb-5" dense>
            <v-col cols="12" md="4" class="text-left">
              <v-card class="pa-5 glass-card">
                <div class="section-title mb-3">Contact</div>
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

            <v-col cols="12" md="4" class="text-left">
              <v-card class="pa-5 glass-card">
                <div class="section-title mb-3">Advisor</div>
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

            <v-col cols="12" md="4" class="text-left">
              <v-card class="pa-5 glass-card">
                <div class="section-title mb-3">Tags & Badges</div>
                <div class="d-flex flex-wrap" style="gap:10px;">
                  <v-chip v-for="t in tags" :key="t" variant="outlined" color="#002856">{{ t }}</v-chip>
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- Tabs -->
          <v-card class="pa-2 glass-card">
            <v-tabs v-model="tab" bg-color="transparent" class="px-2 bold-tabs">
              <v-tab value="students"><v-icon start>mdi-arrow-left</v-icon>Students</v-tab>
              <v-tab value="overview"><v-icon start>mdi-view-dashboard</v-icon>Overview</v-tab>
              <v-tab value="academics"><v-icon start>mdi-school</v-icon>Academics</v-tab>
              <v-tab value="involvement"><v-icon start>mdi-account-group</v-icon>Involvement</v-tab>
              <v-tab value="documents"><v-icon start>mdi-file-document</v-icon>Documents</v-tab>
            </v-tabs>

            <v-window v-model="tab">
              <!-- Overview -->
              <v-window-item value="overview" class="brand-primary text-left">
                <v-card flat class="pa-5">
                  <div class="section-title mb-3">Recent Activity</div>
                  <v-timeline align="start" density="compact">
                    <v-timeline-item
                      v-for="item in activity"
                      :key="item.id"
                      :dot-color="item.color"
                      :icon="item.icon"
                    >
                      <div class="mb-1"><strong>{{ item.title }}</strong></div>
                      <div class="text-caption">{{ item.when }}</div>
                    </v-timeline-item>
                  </v-timeline>
                </v-card>
              </v-window-item>

              <!-- Academics -->
              <v-window-item value="academics" class="brand-primary text-left">
                <v-card flat class="pa-5">
                  <div class="section-title mb-3">Current & Recent Courses</div>
                  <v-data-table
                    :headers="courseHeaders"
                    :items="recentCourses"
                    item-key="id"
                    class="elevation-0 bigger-table"
                    density="comfortable"
                  >
                    <template #item.points="{ item }">
                      <span>{{ (item.credits * gradePoint(item.grade)).toFixed(2) }}</span>
                    </template>
                  </v-data-table>
                </v-card>
              </v-window-item>

              <!-- Involvement -->
              <v-window-item value="involvement">
                <v-card flat class="pa-5 brand-primary text-left">
                  <div class="section-title mb-3">Organizations & Roles</div>
                  <v-list lines="two">
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
              <v-window-item value="documents" class="brand-primary text-left">
                <v-card flat class="pa-5">
                  <div class="section-title mb-3">Files</div>
                  <v-data-table
                    :headers="docHeaders"
                    :items="documents"
                    item-key="id"
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

          <!-- Footer -->
          <div class="text-center mt-6 brand-primary" style="color:#002856;">
            © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Edit Dialog -->
    <v-dialog v-model="openEdit" max-width="880">
      <v-card>
        <v-card-title class="brand-primary">Edit Profile</v-card-title>
        <v-card-text>
          <v-form ref="editForm" v-model="editValid" @submit.prevent="saveEdit">
            <!-- Identity -->
            <v-row>
              <v-col cols="12" class="pb-0">
                <div class="section-sub">Identity</div>
                <v-divider class="mb-3" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.firstName" label="First name" :rules="[rules.required]" prepend-inner-icon="mdi-account" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.lastName" label="Last name" :rules="[rules.required]" prepend-inner-icon="mdi-account" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.studentID" label="Student ID" :rules="[rules.required]" prepend-inner-icon="mdi-card-account-details" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select v-model="editable.level" :items="['Undergraduate','Graduate','Post-bacc']" label="Level" :rules="[rules.required]" prepend-inner-icon="mdi-school" />
              </v-col>
            </v-row>

            <!-- Academics -->
            <v-row>
              <v-col cols="12" class="pb-0">
                <div class="section-sub">Academics</div>
                <v-divider class="mb-3" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.major" label="Major" prepend-inner-icon="mdi-book-education" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.minor" label="Minor" prepend-inner-icon="mdi-book" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.gradTerm" label="Expected Graduation (e.g., Spring 2026)" prepend-inner-icon="mdi-calendar" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select v-model="editable.standing" :items="['Good Standing','Probation','Warning']" label="Academic Standing" prepend-inner-icon="mdi-scale-balance" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model.number="editable.totalCredits" type="number" label="Total Credits" prepend-inner-icon="mdi-counter" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model.number="editable.gpa" type="number" step="0.01" min="0" max="4" label="Cumulative GPA" prepend-inner-icon="mdi-chart-line" />
              </v-col>
            </v-row>

            <!-- Contact -->
            <v-row>
              <v-col cols="12" class="pb-0">
                <div class="section-sub">Contact</div>
                <v-divider class="mb-3" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.email" label="Email" type="email" :rules="[rules.required, rules.email]" prepend-inner-icon="mdi-email" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.phone" label="Phone" prepend-inner-icon="mdi-phone" />
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="editable.address" label="Address" prepend-inner-icon="mdi-map-marker" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editable.pronouns" label="Pronouns" prepend-inner-icon="mdi-account" />
              </v-col>
            </v-row>

            <!-- Tags -->
            <v-row>
              <v-col cols="12" class="pb-0">
                <div class="section-sub">Tags & Badges</div>
                <v-divider class="mb-3" />
              </v-col>
              <v-col cols="12">
                <v-combobox
                  v-model="editable.tags"
                  :items="tagOptions"
                  label="Tags"
                  multiple
                  chips
                  closable-chips
                  prepend-inner-icon="mdi-tag"
                  hint="Press Enter to add a custom tag"
                  persistent-hint
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="openEdit=false">Cancel</v-btn>
          <v-btn color="#0032A0" class="text-on-dark" :disabled="!editValid" @click="saveEdit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Save feedback -->
    <v-snackbar v-model="snack.show" :color="snack.color" timeout="2500">
      {{ snack.message }}
    </v-snackbar>
  </v-container>
</template>
