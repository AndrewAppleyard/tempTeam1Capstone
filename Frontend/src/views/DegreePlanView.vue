<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import DegreePlanAPI from '../apis/DegreePlanAPI.js'
import StudentAPI from '../apis/StudentAPI.js'
import { useUserStore } from '../store/user.js'

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

type Semester = 'Fall' | 'Spring'
type RowType = string

interface CatalogCourse {
  id: string
  year: number              // 1..4 (program year)
  semester: Semester        // 'Fall' | 'Spring'
  term: string              // e.g., 'UAFS FALL 2025'
  code: string
  title: string
  credits: number
  type: RowType
  prereqs: string[]
  coreqs: string[]
  offered: string
  description: string
}

/* ======== TERM LABELS (start UAFS FALL 2025) ======== */
const T = {
  Y1F: 'UAFS FALL 2025',
  Y1S: 'UAFS SPRING 2026',
  Y2F: 'UAFS FALL 2026',
  Y2S: 'UAFS SPRING 2027',
  Y3F: 'UAFS FALL 2027',
  Y3S: 'UAFS SPRING 2028',
  Y4F: 'UAFS FALL 2028',
  Y4S: 'UAFS SPRING 2029'
}


const catalog = ref<CatalogCourse[]>([])
const majorPrefix = ref<string>('CS')
const degreeOptions = ref<string[]>([])
const selectedMajor = ref<string | null>(null)
const concentrations = ref<Record<string, any[]>>({})

function normalizeCode(raw: string) {
  if (!raw) return ''
  const upper = raw.toUpperCase().trim()
  const base = upper.split('-')[0].trim()
  const compact = base.replace(/\s+/g, '')
  const m = compact.match(/^([A-Z]+)(\d{3,6})?/)
  if (!m) return base
  const prefix = m[1]
  const digits = m[2] || ''
  return `${prefix}${digits ? ' ' + digits.slice(0, 4) : ''}`.trim()
}

function computeType(code: string, title: string): RowType {
  const norm = normalizeCode(code)
  const prefix = (norm.match(/^([A-Z]+)/)?.[1] || '').toUpperCase()
  const upperTitle = (title || '').toUpperCase()
  const hasDigits = /\d/.test(norm)

  const isPlaceholder = !norm || norm === 'TBD' || upperTitle.includes('REQUIREMENT') || upperTitle.includes('ELECTIVE')
  const concentrationCue = /CONCENTRATION|ELECTIVE|CS\/MATH\/STAT|UPPER|LOWER/.test(upperTitle)
  const genEdCue = /HUMANITIES|HUMAN|SOCIAL|HISTORY|GOVERNMENT|ENGL|COMM|FINE ARTS|COMPOSITION|WRITING|FINANCE/.test(upperTitle)
  const scienceCue = /LAB|SCIENCE|PHYS|CHEM|BIO/.test(upperTitle)

  if (isPlaceholder && concentrationCue) return 'Elective'
  if (isPlaceholder && scienceCue) return 'STEM'
  if (isPlaceholder && genEdCue) return 'General'

  if (prefix && hasDigits) return prefix
  if (['MATH', 'STAT', 'PHYS', 'BIOL', 'CHEM', 'STEM'].includes(prefix)) return 'STEM'
  if (genEdCue || prefix === '' || norm === 'TBD' || prefix === 'FIN') return 'General'

  return prefix || 'Other'
}


/*======== DATA PULL =========*/
onMounted(async () => {
  try {

     if (!hasStudentId.value) {
    console.warn("No student ID found")
    return
    }
      const studentData = await StudentAPI.getStudentById(studentId.value)
      // major = studentData.student.major
      // console.log('Student major:', major)
      major.value = studentData.student.major
      selectedMajor.value = major.value || null
      console.log('Student major:', major.value)

    // if (!major) {
    //   console.warn('No major found, cannot load degree plan.')
    //   return
    // }
    if (!major.value) {
      console.warn('No major found, cannot load degree plan.')
      return
    }

    await loadDegreeOptions()
    await loadDegreePlan(selectedMajor.value || major.value)
  } catch (err) {
    console.error("Failed to load degree plan", err)
  }
})

async function loadDegreeOptions() {
  try {
    const res = await DegreePlanAPI.view_degree_plans()
    const degrees = res?.data?.degrees || res?.data || []
    const majors = new Set<string>()
    degrees.forEach((d: any) => {
      if (d?.degree) majors.add(d.degree)
    })
    degreeOptions.value = Array.from(majors)
  } catch (err) {
    console.error('Failed to load degree options', err)
  }
}

async function loadDegreePlan(degreeName: string | null) {
  if (!degreeName) return
  try {
    const res = await DegreePlanAPI.view_degree_plans_by_degree(degreeName)
    const degree = res?.data
    if (!degree) return
    major.value = degree.degree || degreeName

    const core = degree.corecourses || {}
    const conc = degree.concentrations || {}
    concentrations.value = Object.fromEntries(
      Object.entries(conc).map(([name, value]) => {
        const arr = Array.isArray(value)
          ? value
          : Array.isArray((value as any)?.courses)
            ? (value as any).courses
            : []
        return [name, arr]
      })
    )
    const firstCode = Object.values(core).flat().map((c: any) => normalizeCode(c.code || '')).find((c: string) => c.startsWith('CS'))
    if (firstCode) majorPrefix.value = (firstCode.match(/^([A-Z]+)/)?.[1] || 'CS').toUpperCase()

    const rows: CatalogCourse[] = []

    const termMap: Record<string, { year: number; semester: Semester; term: string }> = {
      "Freshman Fall":   { year: 1, semester: "Fall", term: "Freshman Fall" },
      "Freshman Spring": { year: 1, semester: "Spring", term: "Freshman Spring" },
      "Sophomore Fall":  { year: 2, semester: "Fall", term: "Sophomore Fall" },
      "Sophomore Spring":{ year: 2, semester: "Spring", term: "Sophomore Spring" },
      "Junior Fall":     { year: 3, semester: "Fall", term: "Junior Fall" },
      "Junior Spring":   { year: 3, semester: "Spring", term: "Junior Spring" },
      "Senior Fall":     { year: 4, semester: "Fall", term: "Senior Fall" },
      "Senior Spring":   { year: 4, semester: "Spring", term: "Senior Spring" },
    }

    Object.entries(core).forEach(([termLabel, courses]) => {
      const t = termMap[termLabel]
      if (!t) return
      ;(courses as any[]).forEach((c, index) => {
        const safeCode = c.code || '-'
        rows.push({
          id: `${termLabel}-${index}`,
          year: t.year,
          semester: t.semester,
          term: t.term,
          code: safeCode,
          title: c.title || "Untitled Course",
          credits: c.hours ?? 0,
          type: computeType(safeCode, c.title || ""),         
          prereqs: Array.isArray(c.prereqs) ? c.prereqs : [],
          coreqs: Array.isArray(c.coreqs) ? c.coreqs : [],
          offered: c.offered || "",
          description: c.description || ""
        })
      })
    })

    catalog.value = rows
  } catch (err) {
    console.error('Failed to load degree plan by degree', err)
  }
}

watch(selectedMajor, (val) => {
  if (val) {
    // reset filters when switching plans
    selectedTerm.value = 'All Terms'
    selectedType.value = 'All'
    search.value = ''
    major.value = val
    loadDegreePlan(val)
  }
})



/* ======== TABLE CONFIG ======== */
const headers = [
  { title: 'Term', key: 'term', sortable: true },
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Type', key: 'type', sortable: true },
  { title: 'Cr', key: 'credits', sortable: true, align: 'end' },
  { title: 'Prereqs', key: 'prereqs', sortable: false }
]

/* ======== FILTERS ======== */
const termOptions = computed(() => {
  const terms = Array.from(new Set(catalog.value.map(c => c.term)))
  return ['All Terms', ...terms]
})

const typeOptions = computed(() => {
  const unique = Array.from(new Set(catalog.value.map(c => c.type))).sort()
  return ['All', ...unique]
})

const selectedType = ref<string>('All')  
const selectedTerm = ref<string>('All Terms')
const search = ref('')                        

function chipColor(type: RowType) {
  const upper = (type || '').toString().toUpperCase()
  // softer, cooler palette
  if (upper === 'CS') return '#4A90E2' // cool blue
  if (['MATH', 'STAT', 'PHYS', 'BIOL', 'CHEM', 'STEM'].includes(upper)) return '#26A69A' // teal
  if (['ENGL', 'COMM', 'HIST', 'GOVT', 'FIN', 'GENERAL', 'GEN ED', 'GEN'].includes(upper)) return '#5C6BC0' // soft indigo
  if (upper === 'ELECTIVE') return '#7E57C2' // muted purple
  return '#78909C' // blue-grey fallback
}

/* ======== DERIVED ======== */
const filteredCourses = computed(() => {
  let rows = catalog.value
  if (selectedTerm.value !== 'All Terms') rows = rows.filter(r => r.term === selectedTerm.value)
  if (selectedType.value !== 'All') rows = rows.filter(r => r.type === selectedType.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    rows = rows.filter(r =>
      r.code.toLowerCase().includes(q) ||
      r.title.toLowerCase().includes(q) ||
      r.prereqs.some(p => p.toLowerCase().includes(q))
    )
  }
  // stable ordering: program year -> semester (Fall before Spring) -> code
  return rows.slice().sort((a, b) => {
    if (a.year !== b.year) return a.year - b.year
    if (a.semester !== b.semester) return a.semester === 'Fall' ? -1 : 1
    return a.code.localeCompare(b.code)
  })
})

const termSummary = computed(() => ({
  credits: filteredCourses.value.reduce((acc, r) => acc + r.credits, 0)
}))

const totalCredits = computed(() =>
  catalog.value.reduce((a, r) => a + r.credits, 0)
)

const typeTotals = computed(() => {
  const totals: Record<string, number> = {}
  catalog.value.forEach(r => {
    totals[r.type] = (totals[r.type] || 0) + r.credits
  })
  return Object.entries(totals)
    .sort((a, b) => b[1] - a[1])
    .map(([type, credits]) => ({ type, credits }))
})

/* ======== ACTIONS ======== */
function printPage() { window.print() }

function downloadCSV() {
  const rows = filteredCourses.value
  const header = ['Term', 'Code', 'Title', 'Type', 'Credits', 'Prereqs']
  const data = rows.map(r => [
    r.term,
    r.code,
    r.title,
    r.type,
    r.credits.toString(),
    r.prereqs.join('; ')
  ])
  const csv = [header, ...data]
    .map(r => r.map(v => `"${String(v).replaceAll('"', '""')}"`).join(','))
    .join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `UAFS_CS_Degree_Plan_${selectedTerm.value.replaceAll(' ', '_')}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.font-mono{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
}

.scroll-table {
  max-height: 600px;
  overflow-y: auto;
  width: 100%;
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
          <!-- Header / Title -->
          <v-row class="mb-3" align="center" no-gutters>
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title
                  class="py-2 px-3"
                  style="color:#002856;border:1px solid #002856;border-radius:8px;font-weight:700;letter-spacing:.25px;"
                >
                  {{ schoolName }} • {{ major || 'Loading Major...' }} • 4-YEAR PLAN
                </v-card-title>
              </v-card>
            </v-col>
            <v-col cols="12" md="6" class="d-flex justify-end align-center flex-wrap" style="gap:10px;">
              <v-btn variant="outlined" color="#002856" @click="printPage">
                <v-icon start>mdi-printer</v-icon>
                Print / Save PDF
              </v-btn>
              <v-btn color="#002856" style="color:white" @click="downloadCSV">
                <v-icon start>mdi-file-delimited</v-icon>
                Export CSV
              </v-btn>
            </v-col>
          </v-row>

          <!-- Program Summary -->
          <v-card
            class="pa-3 mb-4"
            style="background-color:rgba(255,255,255,.6);border:1px solid #002856;text-align:left;border-radius:12px;"
          >
            <v-row>
              <v-col cols="12" md="8">
                <div class="text-h6 mb-1" style="color:#002856;">{{ major }} ({{ schoolName }})</div>
              <div class="d-flex flex-wrap" style="gap:16px;">
                <div><strong>Total Program Hours:</strong> {{ totalCredits }}</div>
                <div
                  v-for="entry in typeTotals"
                  :key="entry.type"
                >
                  <strong>{{ entry.type || 'Other' }}:</strong> {{ entry.credits }} cr
                </div>
              </div>
            </v-col>
              <v-col cols="12" md="4" class="d-flex align-end justify-end">
                <div class="text-right">
                  <div><strong>Credits in View:</strong> {{ termSummary.credits }}</div>
                  <div>
                    <strong>Planned Term:</strong>
                    {{ (selectedTerm === 'All Terms' ? 'All (8 terms)' : selectedTerm) }}
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-card>

          <!-- Controls -->
          <v-row class="mb-3">
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedMajor"
                :items="degreeOptions"
                label="Degree Plan"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedTerm"
                :items="termOptions"
                label="View Term"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedType"
                :items="typeOptions"
                label="Requirement Type"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="12" md="5">
              <v-text-field
                v-model="search"
                label="Search (code, title, prereq)"
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
          </v-row>

          <!-- Courses Table -->
          <v-card
            class="pa-2"
            style="background-color:rgba(255,255,255,.6);text-align:left;border:1px solid #002856;border-radius:12px;"
          >
          <div class="scroll-table">
            <v-data-table
              :headers="headers"
              :items="filteredCourses"
              :items-per-page="-1"
              item-key="id"
              class="elevation-0"
              show-expand
            >
              <template #item.type="{ item }">
                <v-chip size="small" :color="chipColor(item.type)" variant="flat">{{ item.type }}</v-chip>
              </template>

              <template #item.prereqs="{ item }">
                <div class="d-flex flex-wrap" style="gap:6px;">
                  <v-chip
                    v-for="p in item.prereqs"
                    :key="item.id + '-' + p"
                    size="x-small"
                    color="#002856"
                    variant="outlined"
                  >
                    {{ p }}
                  </v-chip>
                  <span v-if="!item.prereqs.length" class="text-disabled">—</span>
                </div>
              </template>

              <template #item.term="{ item }">
                <span class="font-mono">{{ item.term }}</span>
              </template>

              <template #item.credits="{ item }">
                <span class="font-mono">{{ item.credits }}</span>
              </template>

              <template #expanded-row="{ columns, item }">
                <td :colspan="columns.length" class="pa-4" style="background:rgba(0,40,86,.05);">
                  <div class="text-subtitle-2 mb-1" style="color:#002856;">
                    {{ item.code }} • {{ item.title }}
                  </div>
                  <div class="text-body-2">{{ item.description }}</div>
                  <div class="d-flex flex-wrap" style="gap:16px; margin-top:8px;">
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
                    <div><strong>Offered:</strong> {{ item.offered }}</div>
                  </div>
                </td>
              </template>

              <template #bottom>
                <div
                  class="d-flex flex-wrap justify-space-between align-center pa-4"
                  style="border-top:1px solid #002856;"
                >
                  <div class="text-body-2">
                    <strong>Showing:</strong> {{ selectedTerm }}
                    <span v-if="selectedType !== 'All'">• {{ selectedType }}</span>
                  </div>
                  <div class="text-body-2">
                    <strong>Credits in View:</strong> {{ termSummary.credits }}
                    <span class="mx-2">|</span>
                    <strong>Courses:</strong> {{ filteredCourses.length }}
                  </div>
                </div>
              </template>
            </v-data-table>
          </div>
          </v-card>

          <!-- Concentrations helper -->
          <v-card
            class="pa-3 mt-4"
            style="background:rgba(255,255,255,.4);border:1px solid #002856;border-radius:12px;"
          >
            <div class="text-subtitle-1 mb-2" style="color:#002856; text-align:left;">
              Concentrations
            </div>
            <div v-if="Object.keys(concentrations).length" class="text-left">
              <div
                v-for="(courses, name) in concentrations"
                :key="name"
                class="mb-3"
              >
                <div class="font-weight-bold">{{ name }}</div>
                <ul class="pl-6 mb-1">
                  <li
                    v-for="(c, idx) in courses"
                    :key="name + '-' + idx"
                  >
                    <span class="font-mono">{{ c.code || '-' }}</span>
                    <span v-if="c.title"> — {{ c.title }}</span>
                    <span v-if="c.hours || c.credits"> ({{ c.hours ?? c.credits }} cr)</span>
                  </li>
                </ul>
              </div>
            </div>
            <div v-else class="text-body-2 text-disabled">No concentration details available.</div>
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
