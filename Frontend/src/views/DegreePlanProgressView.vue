<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DegreePlanAPI from '../apis/DegreePlanAPI.js'
import StudentAPI from '../apis/StudentAPI.js'
import { useUserStore } from '../store/user.js'


type Semester = 'Fall' | 'Spring'
type RowType = 'Major' | 'Minor' | 'Gen Ed' | 'Concentration/Elective' | 'Other'

interface CatalogCourse {
  id: string
  code: string
  title: string
  credits: number
  type: RowType
  prereqs: string[]
  coreqs: string[]
  description: string
}

interface TranscriptCourse {
  code: string
  grade: string
  credits: number
  term: string
  status: 'Completed' | 'In Progress' | 'Planned'
}

interface ProgressCourse extends CatalogCourse {
  status: 'Complete' | 'In Progress' | 'Planned' | 'Required'
  completedGrade?: string
  completedTerm?: string
  // For tracking which required courses have been met by an equivalent/substitute course
  metBy?: string 
}

// --- Component Setup ---

const route = useRoute()
const userStore = useUserStore()

const studentId = computed<number | null>(() => {
  const routeId = Number(route.params.id)
  if (!Number.isNaN(routeId)) return routeId
  const storeId = userStore.userID ? Number(userStore.userID) : NaN
  return Number.isNaN(storeId) ? null : storeId
})

const hasStudentId = computed(() => !!studentId.value)
const major = ref<string | null>(null)
const schoolName = ref('UAFS')
const loading = ref(true)

const catalogCourses = ref<CatalogCourse[]>([])
const transcriptCourses = ref<TranscriptCourse[]>([])
const progressCourses = ref<ProgressCourse[]>([])


const PASSING_GRADES = ['A', 'B', 'C', 'D'] 

/*======== DATA PULL & MERGE =========*/
onMounted(async () => {
  loading.value = true
  try {
    if (!hasStudentId.value) {
      console.warn("No student ID found")
      return
    }

    const studentData = await StudentAPI.getStudentById(studentId.value)
    major.value = studentData.student.major
    if (!major.value) {
      console.warn('No major found, cannot load degree plan.')
      return
    }

    const resPlan = await DegreePlanAPI.view_degree_plans_by_degree(major.value)
    const degree = resPlan.data
    const rows: CatalogCourse[] = []
    
    Object.entries(degree.corecourses || {}).forEach(([termLabel, courses]) => {
      (courses as any[]).forEach((c, index) => {
        rows.push({
          id: `${termLabel}-${index}-${c.code}`,
          code: c.code || "TBD",
          title: c.title || "Untitled Course",
          credits: c.hours ?? 0,
          type: c.type || "Other", 
          prereqs: c.prereqs || [],
          coreqs: c.coreqs || [],
          description: c.description || ""
        })
      })
    })
    catalogCourses.value = rows

    const resTranscript = await StudentAPI.getTranscripts(studentId.value)
    
    transcriptCourses.value = (resTranscript.data || []).map((t: any) => ({
      code: t.courseCode,
      grade: t.grade,
      credits: t.hours,
      term: t.term,
      status: t.status // 'Completed' is the primary status for progress
    }))

    mergeData()

  } catch (err) {
    console.error("Failed to load progress data", err)
  } finally {
    loading.value = false
  }
})


function mergeData() {
  const merged: ProgressCourse[] = []
  const completedCourses = new Set(
    transcriptCourses.value
      .filter(t => PASSING_GRADES.includes(t.grade.toUpperCase()))
      .map(t => t.code.toUpperCase())
  )
  
  const transcriptMap = new Map<string, TranscriptCourse>()
  transcriptCourses.value.forEach(t => {
      if (t.grade && PASSING_GRADES.includes(t.grade.toUpperCase())) {
          transcriptMap.set(t.code.toUpperCase(), t)
      } else if (!transcriptMap.has(t.code.toUpperCase())) {
          transcriptMap.set(t.code.toUpperCase(), t)
      }
  })

  catalogCourses.value.forEach(catalog => {
    const progress: ProgressCourse = { ...catalog, status: 'Required' }
    const courseCode = catalog.code.toUpperCase()

    if (completedCourses.has(courseCode)) {
      const trans = transcriptMap.get(courseCode)
      if (trans) {
        progress.status = 'Complete'
        progress.completedGrade = trans.grade
        progress.completedTerm = trans.term
        transcriptMap.delete(courseCode) 
      }
    } 
    // Add logic here for 'In Progress' (e.g., if a matching course code is in the transcript with status 'In Progress')
    // else if (transcriptMap.has(courseCode) && transcriptMap.get(courseCode)!.status === 'In Progress') {
    //   progress.status = 'In Progress'
    //   // ...
    // }

    merged.push(progress)
  })

  // Optionally, handle transcript courses that *don't* match a required course (e.g., electives/transfer)
  // For simplicity, we skip this step in the progress view for now, as the focus is on required courses.

  progressCourses.value = merged
  console.log("Progress Data Merged:", merged)
}


/* ======== FILTERING & DISPLAY LOGIC (Inherited from DegreePlan) ======== */
const typeOptions: RowType[] = ['Major', 'Minor', 'Gen Ed', 'Concentration/Elective', 'Other']
type TypeOption = 'All' | RowType

const statusOptions = ['All', 'Complete', 'In Progress', 'Required'] as const
type StatusOption = typeof statusOptions[number]

const selectedType = ref<TypeOption>('All')
const selectedStatus = ref<StatusOption>('All')
const search = ref('')

function chipColor(type: RowType, status?: string): string {
  if (status === 'Complete') return '#002856'
  if (status === 'In Progress') return 'orange' 
  
  switch (type) {
    case 'Major': return '#002856' // Using Major for 'CS Major'
    case 'Minor': return 'indigo'
    case 'Gen Ed': return 'teal'
    case 'Concentration/Elective': return 'purple'
    case 'Other': return 'grey'
    default: return 'grey'
  }
}

// Function for progress status colors/icons
function statusStyle(status: string) {
  switch (status) {
    case 'Complete': 
      return { icon: 'mdi-check-circle', color: 'success' }
    case 'In Progress': 
      return { icon: 'mdi-progress-alert', color: 'warning' }
    case 'Required': 
    default:
      return { icon: 'mdi-minus-circle', color: 'error' }
  }
}

/* ======== DERIVED DATA ======== */

const filteredProgress = computed(() => {
  let rows = progressCourses.value

  if (selectedType.value !== 'All') rows = rows.filter(r => r.type === selectedType.value)
  if (selectedStatus.value !== 'All') rows = rows.filter(r => r.status === selectedStatus.value)
  
  if (search.value) {
    const q = search.value.toLowerCase()
    rows = rows.filter(r =>
      r.code.toLowerCase().includes(q) ||
      r.title.toLowerCase().includes(q) ||
      r.description.toLowerCase().includes(q)
    )
  }

  return rows.slice().sort((a, b) => a.code.localeCompare(b.code))
})

// Progress Summary Computations
const progressSummary = computed(() => {
  const total = progressCourses.value.length
  const complete = progressCourses.value.filter(c => c.status === 'Complete').length
  const required = progressCourses.value.filter(c => c.status === 'Required').length
  const inProgress = progressCourses.value.filter(c => c.status === 'In Progress').length

  const completeCredits = progressCourses.value
    .filter(c => c.status === 'Complete')
    .reduce((acc, c) => acc + c.credits, 0)
  
  const totalCredits = progressCourses.value.reduce((acc, c) => acc + c.credits, 0)
  
  const overallPercent = total > 0 ? (complete / total) * 100 : 0
  
  const categories = typeOptions.map(type => {
    const typeCourses = progressCourses.value.filter(c => c.type === type)
    const typeTotal = typeCourses.length
    const typeComplete = typeCourses.filter(c => c.status === 'Complete').length
    const typeCreditsTotal = typeCourses.reduce((acc, c) => acc + c.credits, 0)
    const typeCreditsComplete = typeCourses.filter(c => c.status === 'Complete').reduce((acc, c) => acc + c.credits, 0)
    
    return {
      type,
      total: typeTotal,
      complete: typeComplete,
      percent: typeTotal > 0 ? (typeComplete / typeTotal) * 100 : 0,
      creditsTotal: typeCreditsTotal,
      creditsComplete: typeCreditsComplete,
      creditsPercent: typeCreditsTotal > 0 ? (typeCreditsComplete / typeCreditsTotal) * 100 : 0,
    }
  })
  
  return {
    total, complete, required, inProgress, 
    completeCredits, totalCredits, overallPercent,
    categories
  }
})

/* ======== TABLE CONFIG ======== */
const headers = [
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Type', key: 'type', sortable: true },
  { title: 'Cr', key: 'credits', sortable: true, align: 'end' },
  { title: 'Grade', key: 'completedGrade', sortable: true },
  { title: 'Term Taken', key: 'completedTerm', sortable: true }
]

</script>

<style scoped>
/* Inherited styles */
.font-mono{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
}

@media print{
  .v-btn,.v-select,.v-text-field{ display:none !important; }
  body{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .v-card{ box-shadow:none !important; }
}
</style>

<template>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <v-row>
      <v-col cols="12" class="mx-auto" style="width:95%;">
        <v-card class="pa-5" style="background-color:#BDD5E7;border:1px solid #002856;border-radius:16px;">
          <v-row class="mb-3" align="center" no-gutters>
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title
                  class="py-2 px-3"
                  style="color:#002856;border:1px solid #002856;border-radius:8px;font-weight:700;letter-spacing:.25px;"
                >
                  {{ schoolName }} • {{ major || 'Loading Major...' }} • PROGRESS
                </v-card-title>
              </v-card>
            </v-col>
            <v-col cols="12" md="6" class="d-flex justify-end align-center flex-wrap" style="gap:10px;">
              <v-btn variant="outlined" color="#002856" @click="() => window.print()">
                <v-icon start>mdi-printer</v-icon>
                Print / Save PDF
              </v-btn>
            </v-col>
          </v-row>

          <v-card
            class="pa-4 mb-4"
            style="background-color:rgba(255,255,255,.8);border:1px solid #002856;text-align:left;border-radius:12px;"
          >
            <div class="text-h5 mb-3" style="color:#002856; font-weight:700;">
              Overall Degree Completion
            </div>
            
            <v-progress-linear
              :model-value="progressSummary.overallPercent"
              height="25"
              rounded
              color="#002856"
              class="mb-3"
            >
              <template #default="{ value }">
                <strong style="color:white;">{{ Math.ceil(value) }}% COMPLETE</strong>
              </template>
            </v-progress-linear>

            <v-row dense class="text-body-1">
              <v-col cols="12" sm="4">
                <strong>Total Required Credits:</strong> 
                <span style="color:#002856; font-weight:700;">{{ progressSummary.totalCredits }}</span>
              </v-col>
              <v-col cols="12" sm="4">
                <strong>Completed Credits:</strong> 
                <span class="text-success font-weight-bold">{{ progressSummary.completeCredits }}</span>
              </v-col>
              <v-col cols="12" sm="4">
                <strong>Remaining Credits:</strong> 
                <span class="text-error font-weight-bold">{{ progressSummary.totalCredits - progressSummary.completeCredits }}</span>
              </v-col>
            </v-row>
          </v-card>
          
          <v-card
            class="pa-4 mb-4"
            style="background-color:rgba(255,255,255,.8);border:1px solid #002856;text-align:left;border-radius:12px;"
          >
            <div class="text-h6 mb-3" style="color:#002856; font-weight:600;">
              Progress by Requirement Type (Credit Hours)
            </div>
            <v-row dense>
              <v-col 
                v-for="cat in progressSummary.categories" 
                :key="cat.type" 
                cols="12" 
                sm="6" 
                md="4"
              >
                <v-card class="pa-2" variant="tonal" :color="chipColor(cat.type)">
                  <div class="text-caption font-weight-bold">{{ cat.type }} ({{ cat.creditsTotal }} Cr)</div>
                  <v-progress-linear
                    :model-value="cat.creditsPercent"
                    height="12"
                    rounded
                    :color="chipColor(cat.type, 'Complete')"
                  >
                    <template #default="{ value }">
                      <span class="text-white text-caption">{{ Math.ceil(value) }}%</span>
                    </template>
                  </v-progress-linear>
                  <div class="text-caption text-right mt-1">
                    {{ cat.creditsComplete }} / {{ cat.creditsTotal }} credits
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card>


          <v-row class="mb-3">
            <v-col cols="12" md="3">
              <v-select
                v-model="selectedType"
                :items="['All', ...typeOptions]"
                label="Requirement Type"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="selectedStatus"
                :items="statusOptions"
                label="Completion Status"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="search"
                label="Search (code, title, description)"
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
          </v-row>

          <v-card
            class="pa-2"
            style="background-color:rgba(255,255,255,.6);text-align:left;border:1px solid #002856;border-radius:12px;"
          >
            <v-data-table
              :headers="headers"
              :items="filteredProgress"
              :items-per-page="15"
              item-key="id"
              class="elevation-0"
              show-expand
              :loading="loading"
              loading-text="Loading degree plan and transcript data..."
            >
              
              <template #item.status="{ item }">
                <v-chip 
                  size="small" 
                  :color="statusStyle(item.status).color" 
                  variant="flat"
                  :prepend-icon="statusStyle(item.status).icon"
                >
                  {{ item.status }}
                </v-chip>
              </template>
              
              <template #item.type="{ item }">
                <v-chip size="small" :color="chipColor(item.type)" variant="flat">{{ item.type }}</v-chip>
              </template>
              
              <template #item.completedGrade="{ item }">
                <span :class="{'font-weight-bold': item.status === 'Complete', 'text-success': item.status === 'Complete' && PASSING_GRADES.includes(item.completedGrade?.toUpperCase() ?? ''), 'text-error': item.status === 'Complete' && !PASSING_GRADES.includes(item.completedGrade?.toUpperCase() ?? '')}">
                  {{ item.completedGrade || (item.status === 'Complete' ? 'N/A' : '—') }}
                </span>
              </template>
              
              <template #item.credits="{ item }">
                <span class="font-mono">{{ item.credits }}</span>
              </template>
              
              <template #expanded-row="{ columns, item }">
                <td :colspan="columns.length" class="pa-4" style="background:rgba(0,40,86,.05);">
                  <div class="text-subtitle-2 mb-1" style="color:#002856;">
                    {{ item.code }} • {{ item.title }}
                  </div>
                  <div class="text-body-2">{{ item.description || 'No description available.' }}</div>
                  
                  <div class="d-flex flex-wrap" style="gap:16px; margin-top:8px;">
                    <div>
                      <strong>Prerequisites:</strong>
                      <template v-if="item.prereqs?.length">
                        <v-chip
                          v-for="p in item.prereqs"
                          :key="item.id + '-p-' + p"
                          size="x-small"
                          class="mr-1"
                          variant="outlined"
                          color="#002856"
                        >
                          {{ p }}
                        </v-chip>
                      </template>
                      <span v-else>None</span>
                    </div>
                    <div>
                      <strong>Co-requisites:</strong>
                      <template v-if="item.coreqs?.length">
                        <v-chip
                          v-for="c in item.coreqs"
                          :key="item.id + '-c-' + c"
                          size="x-small"
                          class="mr-1"
                          variant="outlined"
                        >
                          {{ c }}
                        </v-chip>
                      </template>
                      <span v-else>None</span>
                    </div>
                  </div>
                </td>
              </template>

              <template #bottom>
                <div
                  class="d-flex flex-wrap justify-space-between align-center pa-4"
                  style="border-top:1px solid #002856;"
                >
                  <div class="text-body-2">
                    <strong>Showing:</strong> {{ filteredProgress.length }} courses
                    <span v-if="selectedType !== 'All'">• {{ selectedType }}</span>
                    <span v-if="selectedStatus !== 'All'">• {{ selectedStatus }}</span>
                  </div>
                  <div class="text-body-2">
                    <strong>Total Catalog Credits:</strong> {{ progressSummary.totalCredits }}
                    <span class="mx-2">|</span>
                    <strong>Completed Credits:</strong> {{ progressSummary.completeCredits }}
                  </div>
                </div>
              </template>
            </v-data-table>
          </v-card>

          <div class="text-center mt-6 brand-primary" style="color:#002856;">
           <div>
              © {{ new Date().getFullYear() }} — Numa Advising • University of Arkansas – Fort Smith
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>