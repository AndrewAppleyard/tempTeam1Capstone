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

// let major = null

type Semester = 'Fall' | 'Spring'
type RowType = 'Major' | 'Minor' | 'Gen Ed' | 'Concentration/Elective' | 'Other'

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
      console.log('Student major:', major.value)

    // if (!major) {
    //   console.warn('No major found, cannot load degree plan.')
    //   return
    // }
    if (!major.value) {
      console.warn('No major found, cannot load degree plan.')
      return
    }
    // const res = await DegreePlanAPI.view_degree_plans_by_degree(major)
    const res = await DegreePlanAPI.view_degree_plans_by_degree(major.value)
    console.log('Degree Plan data:', res)
    const degree = res.data

    if (!degree) {
      console.warn('No degree plan returned from backend.')
      return
    }

    const core = degree.corecourses   // object: { "Freshman Fall": [...], ... }
    const rows: CatalogCourse[] = []

    const termMap: Record<string, { year: number; semester: Semester; term: string }> = {
      "Freshman Fall":   { year: 1, semester: "Fall", term: "UAFS FALL 2025" },
      "Freshman Spring": { year: 1, semester: "Spring", term: "UAFS SPRING 2026" },
      "Sophomore Fall":  { year: 2, semester: "Fall", term: "UAFS FALL 2026" },
      "Sophomore Spring":{ year: 2, semester: "Spring", term: "UAFS SPRING 2027" },
      "Junior Fall":     { year: 3, semester: "Fall", term: "UAFS FALL 2027" },
      "Junior Spring":   { year: 3, semester: "Spring", term: "UAFS SPRING 2028" },
      "Senior Fall":     { year: 4, semester: "Fall", term: "UAFS FALL 2028" },
      "Senior Spring":   { year: 4, semester: "Spring", term: "UAFS SPRING 2029" },
    }

    // Flatten the corecourses object into catalog rows
    Object.entries(core).forEach(([termLabel, courses]) => {
      const t = termMap[termLabel]
      if (!t) {
        console.warn("Unknown term label:", termLabel)
        return
      }

      courses.forEach((c, index) => {
        rows.push({
          id: `${termLabel}-${index}`,
          year: t.year,
          semester: t.semester,
          term: t.term,
          code: c.code || "TBD",
          title: c.title || "Untitled Course",
          credits: c.hours ?? 0,
          type: "Other",         
          prereqs: [],           
          coreqs: [],
          offered: "",
          description: ""
        })
      })
    })

    catalog.value = rows
    console.log("Loaded dynamic degree plan:", rows)
  } catch (err) {
    console.error("Failed to load degree plan", err)
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

// type RowType = 'CS Major' | 'Math/Science' | 'Gen Ed' | 'Concentration/Elective' | 'Other';

const typeOptions = [
  'All',
  'CS Major',
  'Math/Science',
  'Gen Ed',
  'Concentration/Elective',
  'Other',
] as const

type TypeOption = typeof typeOptions[number] 

const selectedType = ref<TypeOption>('All')  
const selectedTerm = ref<string>('All Terms')
const search = ref('')                        

function chipColor(type: RowType) {
  switch (type) {
    case 'CS Major': return '#002856'
    case 'Math/Science': return 'teal'
    case 'Gen Ed': return 'indigo'
    case 'Concentration/Elective': return 'purple'
    case 'Other': return 'orange'
  }
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

const catalogTotals = computed(() => {
  const credits = catalog.value.reduce((a, r) => a + r.credits, 0)
  const csMajor = catalog.value.filter(r => r.type === 'CS Major').reduce((a, r) => a + r.credits, 0)
  const mathSci = catalog.value.filter(r => r.type === 'Math/Science').reduce((a, r) => a + r.credits, 0)
  const genEd = catalog.value.filter(r => r.type === 'Gen Ed').reduce((a, r) => a + r.credits, 0)
  const concentration = catalog.value.filter(r => r.type === 'Concentration/Elective').reduce((a, r) => a + r.credits, 0)
  const other = catalog.value.filter(r => r.type === 'Other').reduce((a, r) => a + r.credits, 0)
  return { credits, csMajor, mathSci, genEd, concentration, other }
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
                  <div><strong>Total Program Hours:</strong> {{ catalogTotals.credits }}</div>
                  <div><strong>Major:</strong> {{ catalogTotals.csMajor }} cr</div>
                  <div><strong>Minor:</strong> {{ catalogTotals.mathSci }} 0 cr</div>
                  <div><strong>Gen Ed / Core:</strong> {{ catalogTotals.genEd + catalogTotals.mathSci }} cr</div>
                  <div><strong>Concentration / Electives:</strong> {{ catalogTotals.concentration }} cr</div>
                  <div><strong>Other:</strong> {{ catalogTotals.other }} cr</div>
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
                v-model="selectedTerm"
                :items="termOptions"
                label="View Term"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="12" md="3">
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
            <v-data-table
              :headers="headers"
              :items="filteredCourses"
              :items-per-page="12"
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
          </v-card>

          <!-- Concentrations helper -->
          <v-card
            class="pa-3 mt-4"
            style="background:rgba(255,255,255,.4);border:1px solid #002856;border-radius:12px;"
          >
            <div class="text-subtitle-1 mb-2" style="color:#002856; text-align:left;">
              Concentrations (pick ONE set of 9 hours)
            </div>
            <ul class="pl-6 mb-1" style="text-align:left;">
              <li><strong>Cybersecurity</strong>: Applied Cryptography, Computer Forensics, Identity Mgmt, CyberOps, Cyber Crimes (choose 3)</li>
              <li><strong>Data Science & AI</strong>: Big Data, Deep Learning, Data Analytics, Machine Learning, NLP, IoT Dev, Info Retrieval (choose 3)</li>
              <li><strong>General</strong>: any 3 upper-level CSCE with advisor approval</li>
            </ul>
            <div class="text-body-2 text-disabled">
              These map to the “Concentration / CS/MATH/STAT elective” rows in years 3–4.
            </div>
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
