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
  termLabel: string 
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
      const safeTermLabel = termLabel ? String(termLabel) : "";
      const cleanedTermLabel = safeTermLabel.replace(/^(st|nd|rd|th)/i, '').trim();

      (courses as any[]).forEach((c, index) => {
        rows.push({
          id: `${cleanedTermLabel}-${index}-${c.code}`,
          code: c.code || "TBD",
          title: c.title || "Untitled Course",
          credits: c.hours ?? 0,
          type: c.type || "Other", 
          prereqs: c.prereqs || [],
          coreqs: c.coreqs || [],
          description: c.description || "",
          termLabel: cleanedTermLabel, 
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
      status: t.status === 'Completed' ? 'Completed' : t.status
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
  
  const transcriptMap = new Map<string, TranscriptCourse>()
  transcriptCourses.value.forEach(t => {
      const courseKey = t.code.toUpperCase()
      const existing = transcriptMap.get(courseKey)
      
      const isPassing = t.grade && PASSING_GRADES.includes(t.grade.toUpperCase())

      if (isPassing) {
          transcriptMap.set(courseKey, t) 
      } else if (!existing || existing.status !== 'Completed') {
          transcriptMap.set(courseKey, t) 
      }
  })

  catalogCourses.value.forEach(catalog => {
    const progress: ProgressCourse = { ...catalog, status: 'Required' }
    const courseCode = catalog.code.toUpperCase()
    const trans = transcriptMap.get(courseCode)

    if (trans) {
        if (trans.status === 'Completed' && trans.grade && PASSING_GRADES.includes(trans.grade.toUpperCase())) {
            progress.status = 'Complete'
            progress.completedGrade = trans.grade
            progress.completedTerm = trans.term
        } else if (trans.status === 'In Progress') {
            progress.status = 'In Progress'
            progress.completedTerm = trans.term
        }
        // track nonmatched courses (electives/transfer)
        // transcriptMap.delete(courseCode) 
    } 

    merged.push(progress)
  })
  
  // 'Planned' courses here (student.classes)

  progressCourses.value = merged
}


/* ======== FILTERING & DISPLAY LOGIC (Inherited from DegreePlan) ======== */
const typeOptions: RowType[] = ['Major', 'Minor', 'Gen Ed', 'Concentration/Elective', 'Other']
type TypeOption = 'All' | RowType

const statusOptions = ['All', 'Complete', 'In Progress', 'Required'] as const
type StatusOption = typeof statusOptions[number]

function chipColor(type: RowType, status?: string): string {
  if (status === 'Complete') return 'success' 
  if (status === 'In Progress') return 'warning' 
  
  switch (type) {
    case 'Major': return '#002856'
    case 'Minor': return 'indigo-darken-1'
    case 'Gen Ed': return 'teal-darken-1'
    case 'Concentration/Elective': return 'purple-darken-1'
    case 'Other': return 'grey'
    default: return 'grey'
  }
}

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

interface ProgressTermGroup {
    termLabel: string;
    courses: ProgressCourse[];
    status: 'Completed' | 'In Progress' | 'Required' | 'Unscheduled';
}

const groupedProgress = computed(() => {
    const groups: Record<string, ProgressCourse[]> = {}
    
    progressCourses.value.forEach(course => {
        const term = course.termLabel || 'UNSCHEDULED'
        if (!groups[term]) {
            groups[term] = []
        }
        groups[term].push(course)
    })

    const termGroups: ProgressTermGroup[] = Object.keys(groups).map(termLabel => {
        const courses = groups[termLabel]
        let status: ProgressTermGroup['status'] = 'Completed'

        if (termLabel.toUpperCase() === 'UNSCHEDULED') {
            status = 'Unscheduled'
        } else if (courses.some(c => c.status === 'In Progress')) {
            status = 'In Progress'
        } else if (courses.some(c => c.status === 'Required')) {
            status = 'Required'
        }
        
        return {
            termLabel,
            courses: courses.sort((a, b) => a.code.localeCompare(b.code)),
            status,
        }
    })
    
    const statusOrder: Record<ProgressTermGroup['status'], number> = {
        'In Progress': 1,
        'Completed': 2,
        'Required': 3,
        'Unscheduled': 4,
    }

    termGroups.sort((a, b) => {
        const statusDiff = statusOrder[a.status] - statusOrder[b.status]
        if (statusDiff !== 0) return statusDiff

        if (a.status === 'Unscheduled' && b.status === 'Unscheduled') {
            return a.termLabel.localeCompare(b.termLabel)
        }

        const aYearMatch = a.termLabel.match(/\d{4}/)
        const bYearMatch = b.termLabel.match(/\d{4}/)
        
        const aYear = aYearMatch ? parseInt(aYearMatch[0]) : 0
        const bYear = bYearMatch ? parseInt(bYearMatch[0]) : 0

        if (aYear !== bYear) return bYear - aYear

        // Semester sort (Fall is "later" than Spring in descending order)
        if (a.termLabel.includes('Fall') && b.termLabel.includes('Spring')) return -1 
        if (a.termLabel.includes('Spring') && b.termLabel.includes('Fall')) return 1
        
        return 0
    })

    return termGroups
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
  
  const inProgressCredits = progressCourses.value
    .filter(c => c.status === 'In Progress')
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
    completeCredits, inProgressCredits, totalCredits, overallPercent,
    categories
  }
})

/* ======== TABLE CONFIG ======== */
const headers = [
  { title: 'Status', key: 'status', sortable: true, width: '10%' },
  { title: 'Code', key: 'code', sortable: true, width: '15%' },
  { title: 'Course Title', key: 'title', sortable: false },
  { title: 'Type', key: 'type', sortable: true, width: '15%' },
  { title: 'Cr', key: 'credits', sortable: true, align: 'end', width: '5%' },
  { title: 'Grade', key: 'completedGrade', sortable: true, width: '10%' },
  { title: 'Term Taken', key: 'completedTerm', sortable: true, width: '10%' }
]

const termHeaders = [
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Course Title', key: 'title', sortable: true },
  { title: 'Type', key: 'type', sortable: true },
  { title: 'Cr', key: 'credits', sortable: true, align: 'end' },
  { title: 'Grade', key: 'completedGrade', sortable: true },
  { title: 'Term Taken', key: 'completedTerm', sortable: true }
]

function getTermColor(termLabel: string) {
    const baseColor = 'rgba(0, 40, 86,' 
    if (termLabel.includes('Fall')) return baseColor + ' 0.9)'
    if (termLabel.includes('Spring')) return baseColor + ' 0.75)' 
    if (termLabel.toUpperCase() === 'UNSCHEDULED') return 'grey-darken-2'
    return baseColor + ' 0.9)' 
}

const nextPlannedTermLabel = computed(() => {
    const hasInProgress = progressCourses.value.some(c => c.status === 'In Progress')
    
    for (const group of groupedProgress.value) {
        const isFullyComplete = group.courses.every(c => c.status === 'Complete')
        const hasRequired = group.courses.some(c => c.status === 'Required')

        if (!isFullyComplete && hasRequired) {
            if (group.courses.some(c => c.status === 'In Progress')) {
                continue
            }
            return group.termLabel
        }
    }
    return null
})

function isCurrentOrNextTerm(termLabel: string, progressCourses: ProgressCourse[]): 'Current' | 'Next' | null {
    const isCurrent = progressCourses.some(c => 
        c.status === 'In Progress' && 
        c.completedTerm && 
        termLabel.toUpperCase().includes(c.completedTerm.toUpperCase().split(' ').pop() || termLabel.toUpperCase()) 
    );

    if (isCurrent) {
      return 'Current';
    }

    if (termLabel === nextPlannedTermLabel.value) {
        return 'Next';
    }
        
    return null
}

const showFutureDivider = computed(() => {
    if (!groupedProgress.value.length) return false
    
    const firstRequiredIndex = groupedProgress.value.findIndex(g => g.status === 'Required')
    
    return firstRequiredIndex > 0
})

const firstFutureTerm = computed(() => {
    return groupedProgress.value.find(g => g.status === 'Required')
})
</script>

<style scoped>

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
                  class="py-2 px-3 text-h6"
                  style="color:#002856;border:1px solid #002856;border-radius:8px;font-weight:700;letter-spacing:.25px;"
                >
                  {{ schoolName }} • {{ major || 'Loading Major...' }} • DEGREE AUDIT
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
            style="background-color:rgba(255,255,255,.9);border:1px solid #002856;text-align:left;border-radius:12px;"
          >
            <div class="text-h5 mb-3" style="color:#002856; font-weight:700;">
              Overall Degree Completion
            </div>
            
            <v-progress-linear
              :model-value="progressSummary.overallPercent"
              height="25"
              rounded
              color="#002856"
              class="mb-4"
            >
              <template #default="{ value }">
                <strong style="color:white; font-size: 1.1em;">{{ Math.ceil(value) }}% COMPLETE</strong>
              </template>
            </v-progress-linear>

            <v-row dense class="text-body-1 font-weight-medium">
              <v-col cols="12" sm="3">
                <strong>Total Req. Credits:</strong> 
                <span style="color:#002856;">{{ progressSummary.totalCredits }}</span>
              </v-col>
              <v-col cols="12" sm="3">
                <strong>Completed Credits:</strong> 
                <span class="text-success">{{ progressSummary.completeCredits }}</span>
              </v-col>
              <v-col cols="12" sm="3">
                <strong>In Progress Credits:</strong> 
                <span class="text-warning">{{ progressSummary.inProgressCredits }}</span>
              </v-col>
              <v-col cols="12" sm="3">
                <strong>Remaining Credits:</strong> 
                <span class="text-error">{{ progressSummary.totalCredits - progressSummary.completeCredits - progressSummary.inProgressCredits }}</span>
              </v-col>
            </v-row>
          </v-card>
          
          <v-card
            class="pa-4 mb-6"
            style="background-color:rgba(255,255,255,.9);border:1px solid #002856;text-align:left;border-radius:12px;"
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
                    color="success"
                  >
                    <template #default="{ value }">
                      <span class="text-white text-caption">{{ Math.ceil(value) }}%</span>
                    </template>
                  </v-progress-linear>
                  <div class="text-caption text-right mt-1 font-weight-medium">
                    {{ cat.creditsComplete }} / {{ cat.creditsTotal }} credits
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card>


          <v-row v-if="loading">
              <v-col cols="12">
                  <v-progress-linear indeterminate color="#002856"></v-progress-linear>
                  <div class="text-center mt-3 text-body-1">Loading degree plan and transcript data...</div>
              </v-col>
          </v-row>
          <v-row v-else>
            <v-col cols="12">
              <div class="text-h6 mb-3" style="color:#002856; font-weight:700;">
                Degree Requirements by Recommended Semester
              </div>
            </v-col>
            
            <v-col 
              v-for="(group, index) in groupedProgress" 
              :key="group.termLabel" 
              cols="12"
            >
              <template v-if="showFutureDivider && index === groupedProgress.findIndex(g => g.status === 'Required')">
                  <v-divider class="my-6" color="black" thickness="3"></v-divider>
                  <v-card 
                      flat 
                      color="transparent" 
                      class="text-center pa-4 mb-4"
                  >
                      <div class="text-h6 font-weight-bold text-error">
                          FUTURE SEMESTERS & REQUIRED COURSES
                      </div>
                      <div class="text-subtitle-1 text-grey-darken-2">
                          These terms contain courses you are currently **Required** to take.
                      </div>
                  </v-card>
                  <v-divider class="mb-6" color="black" thickness="3"></v-divider>
              </template>


              <v-card 
                class="pa-4 mb-4" 
                :color="getTermColor(group.termLabel)"
                
                >
                <div class="d-flex justify-space-between align-center">
                  <div class="text-h5 font-weight-bold text-white"> 
                    {{ group.termLabel.toUpperCase() }}
                  </div>
                  
                  <v-chip 
                    v-if="group.status === 'In Progress'"
                    color="warning"
                    variant="flat"
                    class="font-weight-bold"
                  >
                    IN PROGRESS (CURRENT/RECENT)
                  </v-chip>
                  <v-chip 
                    v-else-if="group.status === 'Required'"
                    color="error"
                    variant="flat"
                    class="font-weight-bold"
                  >
                    REQUIRED
                  </v-chip>
                  <v-chip 
                    v-else-if="group.status === 'Completed'"
                    color="success"
                    variant="flat"
                    class="font-weight-bold"
                  >
                    COMPLETED
                  </v-chip>
                  <v-chip 
                    v-else-if="group.status === 'Unscheduled'"
                    color="grey"
                    variant="flat"
                    class="font-weight-bold"
                  >
                    UNSCHEDULED
                  </v-chip>
                </div>
                
                <v-data-table
                  :headers="termHeaders"
                  :items="group.courses"
                  :items-per-page="-1"
                  item-key="id"
                  class="mt-3 elevation-2"
                  show-expand
                  style="border-radius:8px;"
                >
                  <template #item.status="{ item }">
                    <v-chip 
                      size="small" 
                      :color="statusStyle(item.status).color" 
                      variant="flat"
                      :prepend-icon="statusStyle(item.status).icon"
                      class="font-weight-medium"
                    >
                      {{ item.status }}
                    </v-chip>
                  </template>
                  
                  <template #item.type="{ item }">
                    <v-chip size="small" :color="chipColor(item.type)" variant="flat" class="font-weight-medium">{{ item.type }}</v-chip>
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

                  </v-data-table>
              </v-card>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <v-container fluid class="pa-2" style="background-color: transparent;">
    <div class="text-center mt-6 brand-primary">
      © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
    </div>
  </v-container>
</template>