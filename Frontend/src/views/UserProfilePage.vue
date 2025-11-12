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

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

/* GPA map */
const GPA_POINTS: Record<string, number> = {
  'A': 4.0, 'A-': 3.7,
  'B+': 3.3, 'B': 3.0, 'B-': 2.7,
  'C+': 2.3, 'C': 2.0, 'C-': 1.7,
  'D+': 1.3, 'D': 1.0,
  'F': 0.0, 'P': 0.0, 'W': 0.0, 'I': 0.0,
}
const gradePoint = (g: string) => GPA_POINTS[g] ?? 0

/* Routing */
const route = useRoute()
const router = useRouter()
const studentIdParam = route.params.studentID as string | undefined

/* Profile data */
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

/* Stats */
const stats = reactive({
  totalCredits: 86,
  gpa: 3.64,
  degreeCredits: 120,
})
const progressPercent = computed(() => (stats.totalCredits / stats.degreeCredits) * 100)

/* Advisor */
const advisor = reactive({
  name: 'Dr. Dave Stevens',
  title: 'Dean of Students',
  email: 'dave.stevens@uafs.edu',
  nextAppt: 'Nov 4, 2025 • 2:30 PM',
})

/* Tags */
const tags = ref<string[]>(['IFC President', 'Sigma Nu', 'Dean\'s List', 'Senior'])
const tagOptions = ref<string[]>([
  'IFC President','Sigma Nu','Dean\'s List','Senior','Athlete','Honors','Mentor'
])

/* Activity timeline */
const activity = ref([
  { id: 'a1', title: 'Submitted Degree Audit', when: 'Oct 20, 2025', icon: 'mdi-check-circle', color: 'primary' },
  { id: 'a2', title: 'Advising Session Completed', when: 'Oct 14, 2025', icon: 'mdi-account-tie', color: 'primary' },
  { id: 'a3', title: 'Enrolled in Spring 2026', when: 'Oct 10, 2025', icon: 'mdi-calendar-plus', color: 'primary' },
])

/* Recent courses */
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

/* Involvement */
const orgs = ref([
  { id: 'o1', name: 'Interfraternity Council', role: 'President', since: '2025' },
  { id: 'o2', name: 'Sigma Nu', role: 'Member', since: '2023' },
  { id: 'o3', name: 'UAFS AI Society', role: 'Co-founder', since: '2024' },
])

/* Documents */
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

  // Assign back to live state
  profile.studentID = editable.studentID
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

  openEdit.value = false
  snack.show = true
  snack.message = 'Profile updated.'
  snack.color = 'success'
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
