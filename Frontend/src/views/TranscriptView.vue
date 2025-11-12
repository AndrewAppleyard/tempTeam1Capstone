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
                  style="color:#002856; border:1px solid #002856; border-radius:4px; font-weight:700; letter-spacing:.25px;">
                  TRANSCRIPT VIEW
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
              <v-btn color="#002856" style="color:white" @click="downloadCSV">
                <v-icon start>mdi-file-delimited</v-icon>
                Export CSV
              </v-btn>
            </v-col>
          </v-row>

          <!-- Student Summary Card (same look as degree-plan summary) -->
          <v-card class="pa-3 mb-4"
                  style="background-color:rgba(255,255,255,.6); border:1px solid #002856; text-align:left; border-radius:12px;">
            <v-row>
              <v-col cols="12" md="8">
                <div class="text-h6 mb-2" style="color:#002856;">{{ student.fullName }}</div>
                <div class="d-flex flex-wrap" style="gap:16px;">
                  <div><strong>ID:</strong> {{ student.studentID }}</div>
                  <div><strong>Level:</strong> {{ student.level }}</div>
                  <div><strong>Major:</strong> {{ student.major }}</div>
                  <div v-if="student.minor"><strong>Minor:</strong> {{ student.minor }}</div>
                </div>
              </v-col>
              <v-col cols="12" md="4" class="d-flex align-end justify-end">
                <div class="text-right">
                  <div><strong>Total Credits:</strong> {{ cumulative.credits }}</div>
                  <div><strong>Cumulative GPA:</strong> {{ cumulative.gpa.toFixed(2) }}</div>
                </div>
              </v-col>
            </v-row>
          </v-card>

          <!-- Controls Row (identical layout) -->
          <v-row class="mb-3" text-align="center">
            <v-col cols="12" md="6">
              <v-select
                v-model="selectedTerm"
                :items="termOptions"
                label="Select Term"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="search"
                label="Search courses (code, title, grade)"
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
          </v-row>

          <!-- Courses Table (same shell as degree plan) -->
          <v-card class="pa-2"
                  style="background-color:rgba(255,255,255,.6); text-align:left; border:1px solid #002856; border-radius:12px;">
            <v-data-table
              :headers="headers"
              :items="filteredCourses"
              :items-per-page="10"
              item-key="id"
              class="elevation-0"
              :search="search"
            >
              <template #item.credits="{ item }">
                <span class="font-mono">{{ item.credits }}</span>
              </template>

              <template #item.grade="{ item }">
                <v-chip size="small" :color="gradeColor(item.grade)" variant="flat">
                  {{ item.grade }}
                </v-chip>
              </template>

              <template #item.points="{ item }">
                <span class="font-mono">{{ (item.credits * gradePoint(item.grade)).toFixed(2) }}</span>
              </template>

              <template #bottom>
                <div class="d-flex flex-wrap justify-space-between align-center pa-4" style="border-top:1px solid #002856;">
                  <div class="text-body-2"><strong>Term:</strong> {{ selectedTerm }}</div>
                  <div class="text-body-2">
                    <strong>Term Credits:</strong> {{ termSummary.credits }}
                    <span class="mx-2">|</span>
                    <strong>Term GPA:</strong> {{ termSummary.gpa.toFixed(2) }}
                  </div>
                </div>
              </template>
            </v-data-table>
          </v-card>

          <!-- Footer -->
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
import { useRoute, useRouter } from 'vue-router'

/* ===== GPA scale (4.0) ===== */
const GPA_POINTS: Record<string, number> = {
  'A': 4.0, 'A-': 3.7,
  'B+': 3.3, 'B': 3.0, 'B-': 2.7,
  'C+': 2.3, 'C': 2.0, 'C-': 1.7,
  'D+': 1.3, 'D': 1.0,
  'F': 0.0, 'P': 0.0, 'W': 0.0, 'I': 0.0,
}

/* ===== Routing ===== */
const route = useRoute()
const router = useRouter()
const studentIdParam = route.params.studentID as string | undefined

/* ===== Mock Student (swap with API) ===== */
const students = [
  { studentID: 'S1001', firstName: 'Andrew', lastName: 'Mackey', level: 'Undergraduate', major: 'Computer Science', minor: 'Mathematics' },
  { studentID: 'S1002', firstName: 'Yash', lastName: 'Patel', level: 'Undergraduate', major: 'Mathematics' },
  { studentID: 'S1003', firstName: 'Jay', lastName: 'Patel', level: 'Undergraduate', major: 'Nursing' }
]

const student = computed(() => {
  const s = students.find(s => s.studentID === (studentIdParam || 'S1001')) || students[0]
  return { ...s, fullName: `${s.firstName} ${s.lastName}` }
})

/* ===== Transcript rows (swap with API) ===== */
interface CourseRow {
  id: string
  term: string
  code: string
  title: string
  credits: number
  grade: string
}

const transcript = ref<CourseRow[]>([
  { id: '1', term: 'Fall 2024', code: 'CS 1013',   title: 'Intro to CS',            credits: 3, grade: 'A'  },
  { id: '2', term: 'Fall 2024', code: 'MATH 1404', title: 'Calculus I',             credits: 4, grade: 'A'  },
  { id: '3', term: 'Fall 2024', code: 'ENGL 1213', title: 'Composition I',          credits: 3, grade: 'B'  },
  { id: '4', term: 'Spring 2025', code: 'CS 2023', title: 'Data Structures',        credits: 3, grade: 'A'  },
  { id: '5', term: 'Spring 2025', code: 'MATH 1454', title: 'Calculus II',          credits: 4, grade: 'B'  },
  { id: '6', term: 'Spring 2025', code: 'PHYS 2054', title: 'Physics I',            credits: 4, grade: 'B'  },
  { id: '7', term: 'Fall 2025', code: 'CS 3013',   title: 'Algorithms',             credits: 3, grade: 'A'  },
  { id: '8', term: 'Fall 2025', code: 'STAT 2503', title: 'Statistics',             credits: 3, grade: 'B'  },
  { id: '9', term: 'Fall 2025', code: 'HIST 1113', title: 'US History',             credits: 3, grade: 'A'  },
])

/* ===== Headers (degree-plan style: simple titles) ===== */
const headers = [
  { title: 'Term',    key: 'term',    sortable: true },
  { title: 'Course #', key: 'code',   sortable: true },
  { title: 'Title',    key: 'title',  sortable: true },
  { title: 'Cr',       key: 'credits', sortable: true, align: 'end' },
  { title: 'Grade',    key: 'grade',   sortable: true, align: 'center' },
  { title: 'Points',   key: 'points',  sortable: false, align: 'end' },
]

/* ===== Filters ===== */
const termOptions = computed(() => {
  const set = Array.from(new Set(transcript.value.map(t => t.term)))
  return ['All Terms', ...set]
})
const selectedTerm = ref<string>('All Terms')
const search = ref('')

/* ===== Helpers ===== */
const gradePoint = (g: string) => GPA_POINTS[g] ?? 0
function gradeColor(g: string) {
  if (['A','A-'].includes(g)) return '#2e7d32'    // green-ish
  if (['B+','B','B-'].includes(g)) return '#1565c0' // blue-ish
  if (['C+','C','C-'].includes(g)) return '#6a1b9a' // purple-ish
  if (['D+','D'].includes(g)) return '#ef6c00'      // orange-ish
  return '#b00020'                                  // red for F/others
}

const filteredCourses = computed(() => {
  const base = selectedTerm.value === 'All Terms'
    ? transcript.value
    : transcript.value.filter(t => t.term === selectedTerm.value)

  if (!search.value) return base
  const q = search.value.toLowerCase()
  return base.filter(c =>
    c.term.toLowerCase().includes(q) ||
    c.code.toLowerCase().includes(q) ||
    c.title.toLowerCase().includes(q) ||
    c.grade.toLowerCase().includes(q)
  )
})

function summarize(rows: CourseRow[]) {
  const graded = rows.filter(r => GPA_POINTS[r.grade] !== undefined && !['P','W','I'].includes(r.grade))
  const credits = graded.reduce((acc, r) => acc + r.credits, 0)
  const points  = graded.reduce((acc, r) => acc + r.credits * gradePoint(r.grade), 0)
  const gpa = credits > 0 ? points / credits : 0
  return { credits, points, gpa }
}

const termSummary = computed(() => summarize(filteredCourses.value))
const cumulative  = computed(() => summarize(transcript.value))

/* ===== Actions ===== */
function goBack() {
  if (router && router.currentRoute.value.name !== 'students') {
    router.push({ name: 'students' }).catch(() => window.history.back())
  } else {
    window.history.back()
  }
}

function printPage() { window.print() }

function downloadCSV() {
  const rows = selectedTerm.value === 'All Terms'
    ? transcript.value
    : transcript.value.filter(r => r.term === selectedTerm.value)

  const header = ['Term','Course #','Title','Credits','Grade','Points']
  const data = rows.map(r => [
    r.term, r.code, r.title, r.credits.toString(), r.grade,
    (r.credits * gradePoint(r.grade)).toFixed(2),
  ])
  const csv = [header, ...data]
    .map(r => r.map(v => `"${String(v).replaceAll('"','""')}"`).join(','))
    .join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${student.value.studentID}_transcript_${selectedTerm.value.replaceAll(' ','_')}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

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
