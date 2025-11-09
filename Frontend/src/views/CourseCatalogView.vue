<template>
  <v-container fluid class="pa-1" style="background-color: transparent;">
    <v-row justify="center">
      <v-col cols="12">
        <v-card class="pa-4" style="background-color: #BDD5E7; border: 1px solid #002856; border-radius: 12px;">
          <!-- Header / Title -->
          <v-row class="mb-3" text-align="center">
            <v-col cols="12" md="6">
              <v-card flat class="elevation-0" style="background: transparent;">
                <v-card-title class="py-2 px-3"
                  style="color:#002856; border: 1px solid #002856; border-radius: 4px;">
                  CS COURSE CATALOG • 4‑YEAR PLAN
                </v-card-title>
              </v-card>
            </v-col>
            <v-col cols="12" md="6" class="d-flex justify-end align-center gap-2">
              <v-btn variant="outlined" color="#002856" class="mr-2" @click="printPage">
                <v-icon start>mdi-printer</v-icon>
                Print / Save PDF
              </v-btn>
              <v-btn color="#002856" style="color:white" @click="downloadCSV">
                <v-icon start>mdi-file-delimited</v-icon>
                Export CSV
              </v-btn>
            </v-col>
          </v-row>

          <!-- Program Summary Card -->
          <v-card class="pa-3 mb-4" style="background-color: rgba(255,255,255,.6); border: 1px solid #002856; text-align:left;">
            <v-row>
              <v-col cols="12" md="8">
                <div class="text-h6 mb-1" style="color:#002856;">B.S. in Computer Science</div>
                <div class="d-flex flex-wrap gap-4 mt-2">
                  <div><strong>Total Credits (catalog):</strong> {{ catalogTotals.credits }}</div>
                  <div><strong>CS Core:</strong> {{ catalogTotals.core }} cr</div>
                  <div><strong>Math/Science:</strong> {{ catalogTotals.mathSci }} cr</div>
                  <div><strong>Gen Ed:</strong> {{ catalogTotals.genEd }} cr</div>
                  <div><strong>Electives:</strong> {{ catalogTotals.elective }} cr</div>
                </div>
              </v-col>
              <v-col cols="12" md="4" class="d-flex align-end justify-end">
                <div class="text-right">
                  <div><strong>Selected Term Credits:</strong> {{ termSummary.credits }}</div>
                  <div><strong>Planned Terms:</strong> {{ selectedTerm === 'All Terms' ? 'All (8)' : selectedTerm }}</div>
                </div>
              </v-col>
            </v-row>
          </v-card>

          <!-- Controls Row -->
          <v-row class="mb-3" text-align="center">
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedTerm"
                :items="termOptions"
                label="View Term"
                variant="outlined"
                density="comfortable"
                hide-details
                style="--v-theme-primary:#002856"
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
          <v-card class="pa-2" style="background-color: rgba(255,255,255,.6); text-align: left; border: 1px solid #002856;">
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
                <div class="d-flex flex-wrap gap-1">
                  <v-chip v-for="p in item.prereqs" :key="item.id + '-' + p" size="x-small" color="#002856" variant="outlined">{{ p }}</v-chip>
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
                  <div class="text-subtitle-2 mb-1" style="color:#002856;">{{ item.code }} • {{ item.title }}</div>
                  <div class="text-body-2">{{ item.description }}</div>
                  <div class="d-flex flex-wrap gap-4 mt-2">
                    <div><strong>Co-requisites:</strong>
                      <template v-if="item.coreqs.length">
                        <v-chip v-for="c in item.coreqs" :key="item.id + '-c-' + c" size="x-small" class="mr-1" variant="outlined">{{ c }}</v-chip>
                      </template>
                      <span v-else>None</span>
                    </div>
                    <div><strong>Offered:</strong> {{ item.offered }}</div>
                  </div>
                </td>
              </template>

              <template #bottom>
                <div class="d-flex flex-wrap justify-space-between align-center pa-4" style="border-top: 1px solid #002856;">
                  <div class="text-body-2"><strong>Showing:</strong> {{ selectedTerm }} <span v-if="selectedType !== 'All'">• {{ selectedType }}</span></div>
                  <div class="text-body-2">
                    <strong>Credits in View:</strong> {{ termSummary.credits }}
                    <span class="mx-2">|</span>
                    <strong>Courses:</strong> {{ filteredCourses.length }}
                  </div>
                </div>
              </template>
            </v-data-table>
          </v-card>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

// -----------------------------
// Types
// -----------------------------
interface CatalogCourse {
  id: string
  year: number // 1..4
  semester: 'Fall' | 'Spring'
  term: string // e.g., 'Fall Y1'
  code: string
  title: string
  credits: number
  type: 'CS Core' | 'Math/Science' | 'Gen Ed' | 'Elective'
  prereqs: string[]
  coreqs: string[]
  offered: string // e.g., 'Fall & Spring'
  description: string
}

// -----------------------------
// Catalog Data (mock)
// -----------------------------
const catalog = ref<CatalogCourse[]>([
  // Year 1
  { id: 'y1f-cs110', year: 1, semester: 'Fall', term: 'UAFS Fall Y1', code: 'CS 1103', title: 'Intro to CS & Python', credits: 3, type: 'CS Core', prereqs: [], coreqs: [], offered: 'Fall & Spring', description: 'Foundations of computing, problem-solving, Python syntax, and program structure. Includes weekly lab.' },
  { id: 'y1f-math140', year: 1, semester: 'Fall', term: 'UAFS Fall Y1', code: 'MATH 1404', title: 'Calculus I', credits: 4, type: 'Math/Science', prereqs: ['MATH 1203'], coreqs: [], offered: 'Fall & Spring', description: 'Limits, derivatives, applications of differentiation, and introduction to integrals.' },
  { id: 'y1f-en101', year: 1, semester: 'Fall', term: 'UAFS Fall Y1', code: 'ENGL 1213', title: 'Composition I', credits: 3, type: 'Gen Ed', prereqs: [], coreqs: [], offered: 'Fall & Spring', description: 'Academic writing, rhetoric, and research fundamentals.' },
  { id: 'y1f-ge', year: 1, semester: 'Fall', term: 'UAFS Fall Y1', code: 'GE 1003', title: 'First-Year Seminar', credits: 3, type: 'Gen Ed', prereqs: [], coreqs: [], offered: 'Fall', description: 'Transition to university life, study skills, campus engagement.' },

  { id: 'y1s-cs120', year: 1, semester: 'Spring', term: 'UAFS Spring Y1', code: 'CS 1203', title: 'Object-Oriented Programming (Java)', credits: 3, type: 'CS Core', prereqs: ['CS 1103'], coreqs: [], offered: 'Fall & Spring', description: 'Classes, objects, inheritance, interfaces, testing; Java tooling and style.' },
  { id: 'y1s-math145', year: 1, semester: 'Spring', term: 'UAFS Spring Y1', code: 'MATH 1454', title: 'Calculus II', credits: 4, type: 'Math/Science', prereqs: ['MATH 1404'], coreqs: [], offered: 'Fall & Spring', description: 'Techniques of integration, sequences and series, parametric equations.' },
  { id: 'y1s-phys', year: 1, semester: 'Spring', term: 'UAFS Spring Y1', code: 'PHYS 2054', title: 'University Physics I (Calc-based)', credits: 4, type: 'Math/Science', prereqs: ['MATH 1404'], coreqs: [], offered: 'Fall & Spring', description: 'Mechanics, energy, momentum, rotation with lab.' },
  { id: 'y1s-en102', year: 1, semester: 'Spring', term: 'UAFS Spring Y1', code: 'ENGL 1223', title: 'Composition II / Technical Writing', credits: 3, type: 'Gen Ed', prereqs: ['ENGL 1213'], coreqs: [], offered: 'Fall & Spring', description: 'Research writing with emphasis on technical communication.' },

  // Year 2
  { id: 'y2f-ds', year: 2, semester: 'Fall', term: 'UAFS Fall Y2', code: 'CS 2023', title: 'Data Structures', credits: 3, type: 'CS Core', prereqs: ['CS 1203'], coreqs: [], offered: 'Fall & Spring', description: 'Lists, stacks, queues, trees, graphs; asymptotic analysis; generics.' },
  { id: 'y2f-disco', year: 2, semester: 'Fall', term: 'UAFS Fall Y2', code: 'MATH 2103', title: 'Discrete Structures', credits: 3, type: 'Math/Science', prereqs: ['CS 1103'], coreqs: [], offered: 'Fall & Spring', description: 'Logic, sets, relations, functions, counting, graphs; proof techniques.' },
  { id: 'y2f-systems', year: 2, semester: 'Fall', term: 'UAFS Fall Y2', code: 'CS 2303', title: 'Computer Systems & Organization', credits: 3, type: 'CS Core', prereqs: ['CS 1203'], coreqs: [], offered: 'Fall & Spring', description: 'C programming, memory, assembly basics, processes, and the Unix toolchain.' },
  { id: 'y2f-gened', year: 2, semester: 'Fall', term: 'UAFS Fall Y2', code: 'SOC 2003', title: 'Social Science Gen Ed', credits: 3, type: 'Gen Ed', prereqs: [], coreqs: [], offered: 'Fall & Spring', description: 'General education requirement in social sciences (e.g., Sociology or Psychology).' },

  { id: 'y2s-algo', year: 2, semester: 'Spring', term: 'UAFS Spring Y2', code: 'CS 3013', title: 'Algorithms', credits: 3, type: 'CS Core', prereqs: ['CS 2023', 'MATH 2103'], coreqs: [], offered: 'Fall & Spring', description: 'Design and analysis of algorithms, greedy, divide & conquer, DP, NP‑completeness.' },
  { id: 'y2s-prob', year: 2, semester: 'Spring', term: 'UAFS Spring Y2', code: 'STAT 2503', title: 'Probability & Statistics for CS', credits: 3, type: 'Math/Science', prereqs: ['MATH 1454'], coreqs: [], offered: 'Fall & Spring', description: 'Probability, random variables, estimation, regression; computational applications.' },
  { id: 'y2s-db', year: 2, semester: 'Spring', term: 'UAFS Spring Y2', code: 'CS 3203', title: 'Databases', credits: 3, type: 'CS Core', prereqs: ['CS 2023'], coreqs: [], offered: 'Fall & Spring', description: 'Relational model, SQL, normalization, transactions, and ORMs.' },
  { id: 'y2s-genhum', year: 2, semester: 'Spring', term: 'UAFS Spring Y2', code: 'HUM 2003', title: 'Humanities Gen Ed', credits: 3, type: 'Gen Ed', prereqs: [], coreqs: [], offered: 'Fall & Spring', description: 'General education in arts & humanities (e.g., Philosophy, Literature).'},

  // Year 3
  { id: 'y3f-os', year: 3, semester: 'Fall', term: 'UAFS Fall Y3', code: 'CS 3403', title: 'Operating Systems', credits: 3, type: 'CS Core', prereqs: ['CS 2303'], coreqs: [], offered: 'Fall', description: 'Processes, threads, scheduling, synchronization, memory management, file systems.' },
  { id: 'y3f-net', year: 3, semester: 'Fall', term: 'UAFS Fall Y3', code: 'CS 3503', title: 'Computer Networks', credits: 3, type: 'CS Core', prereqs: ['CS 2303'], coreqs: [], offered: 'Fall', description: 'Layered models, TCP/IP, routing, sockets; network programming assignments.' },
  { id: 'y3f-se', year: 3, semester: 'Fall', term: 'UAFS Fall Y3', code: 'CS 3603', title: 'Software Engineering', credits: 3, type: 'CS Core', prereqs: ['CS 2023'], coreqs: [], offered: 'Fall & Spring', description: 'Requirements, design patterns, testing, version control, agile processes.' },
  { id: 'y3f-elect1', year: 3, semester: 'Fall', term: 'UAFS Fall Y3', code: 'CS 3403', title: 'CS Elective I', credits: 3, type: 'Elective', prereqs: ['varies'], coreqs: [], offered: 'Fall & Spring', description: 'Choose from AI, HCI, Cybersecurity, Mobile, etc.' },

  { id: 'y3s-theory', year: 3, semester: 'Spring', term: 'UAFS Spring Y3', code: 'CS 3703', title: 'Theory of Computation', credits: 3, type: 'CS Core', prereqs: ['MATH 2103'], coreqs: [], offered: 'Spring', description: 'Automata, computability, complexity, and formal languages.' },
  { id: 'y3s-pl', year: 3, semester: 'Spring', term: 'UAFS Spring Y3', code: 'CS 3803', title: 'Programming Languages', credits: 3, type: 'CS Core', prereqs: ['CS 2023'], coreqs: [], offered: 'Spring', description: 'Paradigms, type systems, interpreters, functional programming.' },
  { id: 'y3s-phys2', year: 3, semester: 'Spring', term: 'UAFS Spring Y3', code: 'PHYS 2064', title: 'University Physics II', credits: 4, type: 'Math/Science', prereqs: ['PHYS 2054'], coreqs: [], offered: 'Spring', description: 'Electricity & magnetism, optics; includes lab.' },
  { id: 'y3s-elect2', year: 3, semester: 'Spring', term: 'UAFS Spring Y3', code: 'CS 3773', title: 'CS Elective II', credits: 3, type: 'Elective', prereqs: ['varies'], coreqs: [], offered: 'Fall & Spring', description: 'Pick an upper-division elective that deepens your focus area.' },

  // Year 4
  { id: 'y4f-sec', year: 4, semester: 'Fall', term: 'UAFS Fall Y4', code: 'CS 4303', title: 'Cybersecurity Fundamentals', credits: 3, type: 'CS Core', prereqs: ['CS 3503', 'CS 3403'], coreqs: [], offered: 'Fall', description: 'Security principles, crypto basics, secure design, and threat modeling.' },
  { id: 'y4f-ai', year: 4, semester: 'Fall', term: 'UAFS Fall Y4', code: 'CS 4403', title: 'Artificial Intelligence', credits: 3, type: 'Elective', prereqs: ['CS 3013'], coreqs: [], offered: 'Fall', description: 'Search, knowledge representation, probabilistic reasoning, and ML overview.' },
  { id: 'y4f-cap1', year: 4, semester: 'Fall', term: 'UAFS Fall Y4', code: 'CS 4983', title: 'Senior Capstone I', credits: 3, type: 'CS Core', prereqs: ['CS 3603'], coreqs: [], offered: 'Fall', description: 'Project scoping, proposal, design reviews, and professional practice.' },
  { id: 'y4f-gened', year: 4, semester: 'Fall', term: 'UAFS Fall Y4', code: 'COMM 1303', title: 'Oral Communication', credits: 3, type: 'Gen Ed', prereqs: [], coreqs: [], offered: 'Fall & Spring', description: 'Speaking fundamentals, audience analysis, and presentation skills.' },

  { id: 'y4s-cap2', year: 4, semester: 'Spring', term: 'UAFS Spring Y4', code: 'CS 4993', title: 'Senior Capstone II', credits: 3, type: 'CS Core', prereqs: ['CS 4983'], coreqs: [], offered: 'Spring', description: 'Implementation, testing, deployment, and public showcase of the capstone.' },
  { id: 'y4s-ethics', year: 4, semester: 'Spring', term: 'UAFS Spring Y4', code: 'CS 4103', title: 'Computing Ethics & Law', credits: 3, type: 'CS Core', prereqs: ['Junior standing'], coreqs: [], offered: 'Fall & Spring', description: 'Professional ethics, privacy, intellectual property, and policy.' },
  { id: 'y4s-elect3', year: 4, semester: 'Spring', term: 'UAFS Spring Y4', code: 'CS 4040', title: 'CS Elective III', credits: 3, type: 'Elective', prereqs: ['varies'], coreqs: [], offered: 'Fall & Spring', description: 'Advanced elective (e.g., Distributed Systems, Data Mining, Graphics).'},
  { id: 'y4s-gened', year: 4, semester: 'Spring', term: 'UAFS Spring Y4', code: 'FA 1003', title: 'Fine Arts Gen Ed', credits: 3, type: 'Gen Ed', prereqs: [], coreqs: [], offered: 'Fall & Spring', description: 'Fine arts appreciation or practice course meeting Gen Ed requirement.' },
])

// -----------------------------
// Headers & UI Options
// -----------------------------
const headers = [
  { title: 'Term', key: 'term', sortable: true },
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Type', key: 'type', sortable: true },
  { title: 'Cr', key: 'credits', sortable: true, align: 'end' },
  { title: 'Prereqs', key: 'prereqs', sortable: false },
]

const termOptions = computed(() => {
  const terms = Array.from(new Set(catalog.value.map(c => c.term)))
  return ['All Terms', ...terms]
})

const typeOptions = ['All', 'CS Core', 'Math/Science', 'Gen Ed', 'Elective']

// -----------------------------
// Filters
// -----------------------------
const selectedTerm = ref<string>('All Terms')
const selectedType = ref<string>('All')
const search = ref('')

// -----------------------------
// Helpers
// -----------------------------
function chipColor(type: CatalogCourse['type']) {
  switch (type) {
    case 'CS Core': return '#002856'
    case 'Math/Science': return 'teal'
    case 'Gen Ed': return 'indigo'
    case 'Elective': return 'purple'
  }
}

const filteredCourses = computed(() => {
  let rows = catalog.value
  if (selectedTerm.value !== 'All Terms') {
    rows = rows.filter(r => r.term === selectedTerm.value)
  }
  if (selectedType.value !== 'All') {
    rows = rows.filter(r => r.type === selectedType.value)
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    rows = rows.filter(r =>
      r.code.toLowerCase().includes(q) ||
      r.title.toLowerCase().includes(q) ||
      r.prereqs.some(p => p.toLowerCase().includes(q))
    )
  }
  // Sort by Year then semester then code
  return rows.slice().sort((a, b) => {
    if (a.year !== b.year) return a.year - b.year
    if (a.semester !== b.semester) return a.semester === 'Fall' ? -1 : 1
    return a.code.localeCompare(b.code)
  })
})

const termSummary = computed(() => ({
  credits: filteredCourses.value.reduce((acc, r) => acc + r.credits, 0),
}))

const catalogTotals = computed(() => {
  const credits = catalog.value.reduce((a, r) => a + r.credits, 0)
  const core = catalog.value.filter(r => r.type === 'CS Core').reduce((a, r) => a + r.credits, 0)
  const mathSci = catalog.value.filter(r => r.type === 'Math/Science').reduce((a, r) => a + r.credits, 0)
  const genEd = catalog.value.filter(r => r.type === 'Gen Ed').reduce((a, r) => a + r.credits, 0)
  const elective = catalog.value.filter(r => r.type === 'Elective').reduce((a, r) => a + r.credits, 0)
  return { credits, core, mathSci, genEd, elective }
})

// -----------------------------
// Actions
// -----------------------------
function printPage() { window.print() }

function downloadCSV() {
  const rows = filteredCourses.value
  const header = ['Term','Code','Title','Type','Credits','Prereqs']
  const data = rows.map(r => [r.term, r.code, r.title, r.type, r.credits.toString(), r.prereqs.join('; ')])
  const csv = [header, ...data].map(r => r.map(v => `"${String(v).replaceAll('"','""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `CS_Course_Catalog_${selectedTerm.value.replaceAll(' ','_')}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.student-card { cursor: pointer; transition: transform .15s ease, box-shadow .15s ease; }
.student-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,.15); }

.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

@media print {
  .v-btn, .v-select, .v-text-field { display: none !important; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .v-card { box-shadow: none !important; }
}

/* utility */
.gap-2 { gap: .5rem; }
.gap-4 { gap: 1rem; }
</style>
