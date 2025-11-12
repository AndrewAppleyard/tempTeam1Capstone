<template>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <v-row>
      <!-- 95% width shell to match your other pages -->
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
                  UAFS • B.S. COMPUTER SCIENCE • 4-YEAR PLAN
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
                <div class="text-h6 mb-1" style="color:#002856;">Computer Science, B.S. (UAFS)</div>
                <div class="d-flex flex-wrap" style="gap:16px;">
                  <div><strong>Total Program Hours:</strong> {{ catalogTotals.credits }}</div>
                  <div><strong>CS Major:</strong> {{ catalogTotals.csMajor }} cr</div>
                  <div><strong>Math / Science:</strong> {{ catalogTotals.mathSci }} cr</div>
                  <div><strong>Gen Ed / Core:</strong> {{ catalogTotals.genEd }} cr</div>
                  <div><strong>Concentration / Electives:</strong> {{ catalogTotals.concentration }} cr</div>
                  <div><strong>Other:</strong> {{ catalogTotals.other }} cr</div>
                </div>
              </v-col>
              <v-col cols="12" md="4" class="d-flex align-end justify-end">
                <div class="text-right">
                  <div><strong>Credits in View:</strong> {{ termSummary.credits }}</div>
                  <div>
                    <strong>Planned Term:</strong>
                    {{ selectedTerm === 'All Terms' ? 'All (8 terms)' : selectedTerm }}
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
              :search="search"
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
            © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
          </div>
        </v-card>
        
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

type Semester = 'Fall' | 'Spring'
type RowType = 'CS Major' | 'Math/Science' | 'Gen Ed' | 'Concentration/Elective' | 'Other'

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

/* ======== CATALOG (flattened) ======== */
const catalog = ref<CatalogCourse[]>([
  // YEAR 1 — FALL 2025
  {
    id: 'y1f-csce10903',
    year: 1, semester: 'Fall', term: T.Y1F,
    code: 'CSCE 10903', title: 'Computer Science Concepts', credits: 3, type: 'CS Major',
    prereqs: [], coreqs: [], offered: 'Fall',
    description: 'Introduction to the CS discipline, problem solving, and basic computing tools.'
  },
  {
    id: 'y1f-math24004',
    year: 1, semester: 'Fall', term: T.Y1F,
    code: 'MATH 24004', title: 'Calculus I', credits: 4, type: 'Math/Science',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Limits, derivatives, applications, and intro to integration.'
  },
  {
    id: 'y1f-univ10041',
    year: 1, semester: 'Fall', term: T.Y1F,
    code: 'UNIV 10041', title: 'College Preparation for STEM Majors', credits: 1, type: 'Other',
    prereqs: [], coreqs: [], offered: 'Fall',
    description: 'Orientation / success strategies for STEM students.'
  },
  {
    id: 'y1f-engl1203',
    year: 1, semester: 'Fall', term: T.Y1F,
    code: 'ENGL 1203', title: 'English Composition I (Gen Ed)', credits: 3, type: 'Gen Ed',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Rhetoric and academic writing.'
  },
  {
    id: 'y1f-gened1',
    year: 1, semester: 'Fall', term: T.Y1F,
    code: 'Gen Ed Elective', title: 'Fine Arts / Humanities / Social Sciences', credits: 3, type: 'Gen Ed',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Pick any approved Gen Ed in FA/H/SS.'
  },

  // YEAR 1 — SPRING 2026
  {
    id: 'y1s-csce10104',
    year: 1, semester: 'Spring', term: T.Y1S,
    code: 'CSCE 10104', title: 'Foundations of Programming I', credits: 4, type: 'CS Major',
    prereqs: ['CSCE 10903'], coreqs: [], offered: 'Spring',
    description: 'First programming sequence (likely Python or C#/Java).'
  },
  {
    id: 'y1s-csce10404',
    year: 1, semester: 'Spring', term: T.Y1S,
    code: 'CSCE 10404', title: 'Foundations of Networking', credits: 4, type: 'CS Major',
    prereqs: [], coreqs: [], offered: 'Spring',
    description: 'Basic networking concepts; models, addressing, and practice.'
  },
  {
    id: 'y1s-math25004',
    year: 1, semester: 'Spring', term: T.Y1S,
    code: 'MATH 25004', title: 'Calculus II', credits: 4, type: 'Math/Science',
    prereqs: ['MATH 24004'], coreqs: [], offered: 'Fall & Spring',
    description: 'Integration techniques, series, and applications.'
  },
  {
    id: 'y1s-engl1213',
    year: 1, semester: 'Spring', term: T.Y1S,
    code: 'ENGL 1213', title: 'English Composition II (Gen Ed)', credits: 3, type: 'Gen Ed',
    prereqs: ['ENGL 1203'], coreqs: [], offered: 'Fall & Spring',
    description: 'Research writing and argument.'
  },

  // YEAR 2 — FALL 2026
  {
    id: 'y2f-csce10204',
    year: 2, semester: 'Fall', term: T.Y2F,
    code: 'CSCE 10204', title: 'Foundations of Programming II', credits: 4, type: 'CS Major',
    prereqs: ['CSCE 10104'], coreqs: [], offered: 'Fall',
    description: 'Continuation of programming I; objects, larger programs.'
  },
  {
    id: 'y2f-csce20503',
    year: 2, semester: 'Fall', term: T.Y2F,
    code: 'CSCE 20503', title: 'Foundations of Cybersecurity', credits: 3, type: 'CS Major',
    prereqs: [], coreqs: [], offered: 'Fall',
    description: 'Security principles, threats, and basic protections.'
  },
  {
    id: 'y2f-finn15201',
    year: 2, semester: 'Fall', term: T.Y2F,
    code: 'FINN 15201', title: 'Personal Finance Applications', credits: 1, type: 'Other',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Financial literacy requirement.'
  },
  {
    id: 'y2f-cs-lower',
    year: 2, semester: 'Fall', term: T.Y2F,
    code: 'CSCE xxxx (LL)', title: 'Lower-Level CS Elective (advisor approved)', credits: 3, type: 'Concentration/Elective',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Any lower-level CSCE to broaden foundation.'
  },
  {
    id: 'y2f-lab-sci-1',
    year: 2, semester: 'Fall', term: T.Y2F,
    code: 'Lab Science I', title: 'Approved Lab Science (GEOL/CHEM/PHYS)', credits: 4, type: 'Math/Science',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Pick from approved list in catalog.'
  },

  // YEAR 2 — SPRING 2027
  {
    id: 'y2s-csce20003',
    year: 2, semester: 'Spring', term: T.Y2S,
    code: 'CSCE 20003', title: 'Data Structures', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 10204'], coreqs: [], offered: 'Spring',
    description: 'Lists, trees, maps, algorithmic complexity.'
  },
  {
    id: 'y2s-csce20303',
    year: 2, semester: 'Spring', term: T.Y2S,
    code: 'CSCE 20303', title: 'Web Systems', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 10104'], coreqs: [], offered: 'Spring',
    description: 'HTTP, web tech stack, client/server.'
  },
  {
    id: 'y2s-math26103',
    year: 2, semester: 'Spring', term: T.Y2S,
    code: 'MATH 26103', title: 'Discrete Mathematics I', credits: 3, type: 'Math/Science',
    prereqs: [], coreqs: [], offered: 'Spring',
    description: 'Logic, sets, functions, counting.'
  },
  {
    id: 'y2s-spch10003',
    year: 2, semester: 'Spring', term: T.Y2S,
    code: 'SPCH 10003', title: 'Introduction to Speech Communication', credits: 3, type: 'Gen Ed',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Public speaking / oral communication requirement.'
  },
  {
    id: 'y2s-lab-sci-2',
    year: 2, semester: 'Spring', term: T.Y2S,
    code: 'Lab Science II', title: 'Approved Lab Science (GEOL/CHEM/PHYS)', credits: 4, type: 'Math/Science',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Second lab science from approved list.'
  },

  // YEAR 3 — FALL 2027
  {
    id: 'y3f-csce30303',
    year: 3, semester: 'Fall', term: T.Y3F,
    code: 'CSCE 30303', title: 'Computer Architecture', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 10204'], coreqs: [], offered: 'Fall',
    description: 'Organization, ISA, pipelines, memory.'
  },
  {
    id: 'y3f-csce30403',
    year: 3, semester: 'Fall', term: T.Y3F,
    code: 'CSCE 30403', title: 'Database Systems', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 20003'], coreqs: [], offered: 'Fall',
    description: 'Relational model, SQL, and DB design.'
  },
  {
    id: 'y3f-csce31003',
    year: 3, semester: 'Fall', term: T.Y3F,
    code: 'CSCE 31003', title: 'Algorithms', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 20003', 'MATH 26103'], coreqs: [], offered: 'Fall',
    description: 'Design and analysis of algorithms.'
  },
  {
    id: 'y3f-math33073',
    year: 3, semester: 'Fall', term: T.Y3F,
    code: 'MATH 33073', title: 'Discrete Mathematics II', credits: 3, type: 'Math/Science',
    prereqs: ['MATH 26103'], coreqs: [], offered: 'Fall',
    description: 'Advanced discrete topics to support CS.'
  },
  {
    id: 'y3f-conc1',
    year: 3, semester: 'Fall', term: T.Y3F,
    code: 'Concentration / CS/MATH/STAT Elective 1', title: 'Concentration or CS/MATH/STAT Elective', credits: 3, type: 'Concentration/Elective',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'First of 3 courses in chosen concentration.'
  },

  // YEAR 3 — SPRING 2028
  {
    id: 'y3s-csce30003',
    year: 3, semester: 'Spring', term: T.Y3S,
    code: 'CSCE 30003', title: 'Distributed Systems', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 30403'], coreqs: [], offered: 'Spring',
    description: 'Distributed architectures, communication, consistency.'
  },
  {
    id: 'y3s-csce30503',
    year: 3, semester: 'Spring', term: T.Y3S,
    code: 'CSCE 30503', title: 'Operating Systems', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 30303'], coreqs: [], offered: 'Spring',
    description: 'Processes, threads, memory, file systems.'
  },
  {
    id: 'y3s-csce31103',
    year: 3, semester: 'Spring', term: T.Y3S,
    code: 'CSCE 31103', title: 'Artificial Intelligence', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 31003'], coreqs: [], offered: 'Spring',
    description: 'Search, knowledge, and intelligent agents.'
  },
  {
    id: 'y3s-conc2',
    year: 3, semester: 'Spring', term: T.Y3S,
    code: 'Concentration / CS/MATH/STAT Elective 2', title: 'Concentration or CS/MATH/STAT Elective', credits: 3, type: 'Concentration/Elective',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Second course in chosen concentration.'
  },
  {
    id: 'y3s-gened',
    year: 3, semester: 'Spring', term: T.Y3S,
    code: 'Gen Ed Elective', title: 'Fine Arts / Humanities / Social Sciences', credits: 3, type: 'Gen Ed',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Gen Ed to meet core requirements.'
  },

  // YEAR 4 — FALL 2028
  {
    id: 'y4f-csce40003',
    year: 4, semester: 'Fall', term: T.Y4F,
    code: 'CSCE 40003', title: 'Software Engineering', credits: 3, type: 'CS Major',
    prereqs: ['CSCE 30403'], coreqs: [], offered: 'Fall',
    description: 'Process, requirements, testing, and teamwork.'
  },
  {
    id: 'y4f-csce40303',
    year: 4, semester: 'Fall', term: T.Y4F,
    code: 'CSCE 40303', title: 'Ethics and Professional Practice', credits: 3, type: 'CS Major',
    prereqs: [], coreqs: [], offered: 'Fall',
    description: 'Legal, social, and ethical issues in computing.'
  },
  {
    id: 'y4f-conc3',
    year: 4, semester: 'Fall', term: T.Y4F,
    code: 'Concentration / CS/MATH/STAT Elective 3', title: 'Concentration or CS/MATH/STAT Elective', credits: 3, type: 'Concentration/Elective',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Third course in chosen concentration.'
  },
  {
    id: 'y4f-hist-gov',
    year: 4, semester: 'Fall', term: T.Y4F,
    code: 'History / Government', title: 'U.S. History or Government Requirement', credits: 3, type: 'Gen Ed',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Meets state history/government requirement.'
  },
  {
    id: 'y4f-fa-hum-ss',
    year: 4, semester: 'Fall', term: T.Y4F,
    code: 'Gen Ed Elective', title: 'Fine Arts / Humanities / Social Sciences', credits: 3, type: 'Gen Ed',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Gen Ed to complete core.'
  },

  // YEAR 4 — SPRING 2029
  {
    id: 'y4s-csce40203',
    year: 4, semester: 'Spring', term: T.Y4S,
    code: 'CSCE 40203', title: 'Senior Capstone', credits: 3, type: 'CS Major',
    prereqs: ['Senior standing'], coreqs: [], offered: 'Spring',
    description: 'Culminating project and presentations.'
  },
  {
    id: 'y4s-csce40433',
    year: 4, semester: 'Spring', term: T.Y4S,
    code: 'CSCE 40433', title: 'Formal Languages', credits: 3, type: 'CS Major',
    prereqs: ['MATH 26103'], coreqs: [], offered: 'Spring',
    description: 'Automata, grammars, Turing machines; theory of computation.'
  },
  {
    id: 'y4s-conc4',
    year: 4, semester: 'Spring', term: T.Y4S,
    code: 'Concentration / CS/MATH/STAT Elective 4', title: 'Concentration or CS/MATH/STAT Elective', credits: 3, type: 'Concentration/Elective',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'If your concentration is done, take advisor-approved CS/MATH/STAT.'
  },
  {
    id: 'y4s-math-stat-ul',
    year: 4, semester: 'Spring', term: T.Y4S,
    code: 'MATH/STAT Upper-Level Elective', title: 'Upper-Level Math/Stat Elective (advisor approved)', credits: 3, type: 'Math/Science',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Required UL Math/Stat per catalog.'
  },
  {
    id: 'y4s-fa-hum-ss',
    year: 4, semester: 'Spring', term: T.Y4S,
    code: 'Gen Ed Elective', title: 'Fine Arts / Humanities / Social Sciences', credits: 3, type: 'Gen Ed',
    prereqs: [], coreqs: [], offered: 'Fall & Spring',
    description: 'Final Gen Ed to reach 120 hours total.'
  }
])

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
// keep your RowType as-is elsewhere:
// type RowType = 'CS Major' | 'Math/Science' | 'Gen Ed' | 'Concentration/Elective' | 'Other';

const typeOptions = [
  'All',
  'CS Major',
  'Math/Science',
  'Gen Ed',
  'Concentration/Elective',
  'Other',
] as const

type TypeOption = typeof typeOptions[number] // 'All' | RowType

const selectedType = ref<TypeOption>('All')   // ✅ single source of truth
const selectedTerm = ref<string>('All Terms') // ok to keep string here
const search = ref('')                        // ok

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
