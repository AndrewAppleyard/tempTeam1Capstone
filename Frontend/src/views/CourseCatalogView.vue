<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import CourseCatalogAPI from "../apis/CourseCatalogAPI";

interface DB_Course {
  code: string;
  title: string;
  hours: number;
}

interface DB_CoreBlock {
  year: string;
  courses: DB_Course[];
}

interface DB_Concentration {
  code: string;
  name: string;
  required_hours: number;
  courses: string[];
  notes: string;
}

interface DegreePlan {
  degree: string;
  institution: string;
  major_code: string;
  credit_hours_total: number;
  notes: string[];
  core_courses: DB_CoreBlock[];
  concentrations: DB_Concentration[];
}

//For this info might have to pull from stuffs thats not what our degree plan is doing right now, I don't know whow feasible this is
interface CatalogCourse {
  id: string
  year: number // 1..4
  semester: 'Fall' | 'Spring'
  term: string // e.g., 'UAFS Fall 2025'
  code: string
  title: string
  credits: number
  type: 'CS Core' | 'Math/Science' | 'Gen Ed' | 'Elective'
  prereqs: string[]
  coreqs: string[]
  offered: string // e.g., 'Fall & Spring'
  description: string
}

const catalog = ref<CatalogCourse[]>([])
const degreePlan = ref<DegreePlan | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

//catalog and degree plan overlap is kinda confusing we will probably have to change this one way or another
async function loadCatalog() {
  try {
    const plans = await CourseCatalogAPI.getAllDegreePlans();

    const plan = plans.find(
      (p: any) => p.majorcode?.toLowerCase().includes("cs")
    );

    if (!plan) {
      error.value = "No Computer Science degree plan found.";
      return;
    }

    degreePlan.value = plan;

    const rows: CatalogCourse[] = [];

    for (const block of plan.corecourses) {
      const { year, semester } = parseYearAndSemester(block.year);

      for (const c of block.courses) {
        rows.push({
          id: crypto.randomUUID(),
          year,
          semester,
          term: buildTermLabel(year, semester),
          code: c.code,
          title: c.title,
          credits: c.hours,

          // We don't have these yet, might need to remove or put in a different view idk
          type: guessType(c.code),
          prereqs: [],
          coreqs: [],
          offered: "",
          description: "",
        });
      }
    }

    catalog.value = rows;
  } catch (err) {
    console.error(err);
    error.value = "Unable to load course catalog.";
  } finally {
    loading.value = false;
  }
}


//helpers
function parseYearAndSemester(label: string) {
  const [yearWord, semesterWord] = label.split(" ");

  return {
    year: convertYearWord(yearWord),
    semester: semesterWord as Semester,
  };
}

function convertYearWord(word: string): number {
  switch (word.toLowerCase()) {
    case "freshman": return 1;
    case "sophomore": return 2;
    case "junior": return 3;
    case "senior": return 4;
    default: return 1;
  }
}

function buildTermLabel(year: number, semester: Semester): string {
  const base = 2025 + (year - 1);
  const calendarYear = semester === "Fall" ? base : base + 1;
  return `UAFS ${semester} ${calendarYear}`;
}

function guessType(code: string): RowType {
  if (code.startsWith("CSCE") || code.startsWith("CS ")) return "CS Core";
  if (code.startsWith("MATH") || code.startsWith("PHYS") || code.startsWith("STAT"))
    return "Math/Science";
  if (code.includes("ENGL") || code.includes("HUM") || code.includes("COMM"))
    return "Gen Ed";

  return "Elective";
}

//load
onMounted(() => {
  loadCatalog();
});

/* --- Headers & UI Options --- */
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

/* --- Filters --- */
const selectedTerm = ref<string>('All Terms')
const selectedType = ref<string>('All')
const search = ref('')

/* --- Helpers --- */
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
  // Sort by Year -> Fall before Spring -> Code
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

/* --- Actions --- */
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
  a.download = `UAFS_CS_Catalog_${selectedTerm.value.replaceAll(' ','_')}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <v-container fluid class="pa-1" style="background-color: transparent;">
    <v-row justify="center">
      <v-col cols="12">
        <v-card class="pa-4" style="background-color:#BDD5E7;border:1px solid #002856;border-radius:12px;">
          <!-- Header / Title -->
          <v-row class="mb-3" text-align="center">
            <v-col cols="12" md="6">
              <v-card flat class="elevation-0" style="background: transparent;">
                <v-card-title class="py-2 px-3"
                  style="color:#002856; border: 1px solid #002856; border-radius: 4px; font-weight:700; letter-spacing:.25px;">
                  UAFS • B.S. COMPUTER SCIENCE • 4-YEAR PLAN
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
          <v-card class="pa-3 mb-4" style="background-color:rgba(255,255,255,.6); border:1px solid #002856; text-align:left; border-radius:12px;">
            <v-row>
              <v-col cols="12" md="8">
                <div class="text-h6 mb-1" style="color:#002856;">B.S. in Computer Science</div>
                <div class="d-flex flex-wrap" style="gap:16px;">
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
          <v-card class="pa-2" style="background-color: rgba(255,255,255,.6); text-align: left; border:1px solid #002856; border-radius:12px;">
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
                  <v-chip v-for="p in item.prereqs" :key="item.id + '-' + p" size="x-small" color="#002856" variant="outlined">
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
                  <div class="text-subtitle-2 mb-1" style="color:#002856;">{{ item.code }} • {{ item.title }}</div>
                  <div class="text-body-2">{{ item.description }}</div>
                  <div class="d-flex flex-wrap" style="gap:16px; margin-top:8px;">
                    <div>
                      <strong>Co-requisites:</strong>
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
                <div class="d-flex flex-wrap justify-space-between align-center pa-4" style="border-top:1px solid #002856;">
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

          <div class="text-center mt-6 brand-primary" style="color:#002856;">
            © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; }

@media print {
  .v-btn, .v-select, .v-text-field { display: none !important; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .v-card { box-shadow: none !important; }
}

/* utility */
.gap-2 { gap: .5rem; }
.gap-4 { gap: 1rem; }
</style>
