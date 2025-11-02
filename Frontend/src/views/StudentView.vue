<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

/* =========================================================
   1. DEGREE PLAN SOURCE (CS degree plan)
========================================================= */
interface DegreePlanCourse {
  term: string
  code: string
  title: string
}

const DEGREE_PLAN: DegreePlanCourse[] = [
  // Year 1
  { term: 'Fall Y1', code: 'CSCE 10903', title: 'Computer Science Concepts' },
  { term: 'Fall Y1', code: 'MATH 24004', title: 'Calculus I' },
  { term: 'Fall Y1', code: 'UNIV 10041', title: 'College Prep for STEM Majors' },
  { term: 'Fall Y1', code: 'ENGL 1203', title: 'English Composition I' },
  { term: 'Fall Y1', code: 'Gen Ed Elective', title: 'FA / HUM / SS' },

  { term: 'Spring Y1', code: 'CSCE 10104', title: 'Foundations of Programming I' },
  { term: 'Spring Y1', code: 'CSCE 10404', title: 'Foundations of Networking' },
  { term: 'Spring Y1', code: 'MATH 25004', title: 'Calculus II' },
  { term: 'Spring Y1', code: 'ENGL 1213', title: 'English Composition II' },

  // Year 2
  { term: 'Fall Y2', code: 'CSCE 10204', title: 'Foundations of Programming II' },
  { term: 'Fall Y2', code: 'CSCE 20503', title: 'Foundations of Cybersecurity' },
  { term: 'Fall Y2', code: 'FINN 15201', title: 'Personal Finance Applications' },
  { term: 'Fall Y2', code: 'CSCE xxxx (LL)', title: 'Lower-Level CS Elective' },
  { term: 'Fall Y2', code: 'Lab Science I', title: 'Approved Lab Science' },

  { term: 'Spring Y2', code: 'CSCE 20003', title: 'Data Structures' },
  { term: 'Spring Y2', code: 'CSCE 20303', title: 'Web Systems' },
  { term: 'Spring Y2', code: 'MATH 26103', title: 'Discrete Mathematics I' },
  { term: 'Spring Y2', code: 'SPCH 10003', title: 'Intro to Speech Communication' },
  { term: 'Spring Y2', code: 'Lab Science II', title: 'Approved Lab Science' },

  // Year 3
  { term: 'Fall Y3', code: 'CSCE 30303', title: 'Computer Architecture' },
  { term: 'Fall Y3', code: 'CSCE 30403', title: 'Database Systems' },
  { term: 'Fall Y3', code: 'CSCE 31003', title: 'Algorithms' },
  { term: 'Fall Y3', code: 'MATH 33073', title: 'Discrete Mathematics II' },
  { term: 'Fall Y3', code: 'Conc/Elective 1', title: 'Concentration / CS/MATH/STAT' },

  { term: 'Spring Y3', code: 'CSCE 30003', title: 'Distributed Systems' },
  { term: 'Spring Y3', code: 'CSCE 30503', title: 'Operating Systems' },
  { term: 'Spring Y3', code: 'CSCE 31103', title: 'Artificial Intelligence' },
  { term: 'Spring Y3', code: 'Conc/Elective 2', title: 'Concentration / CS/MATH/STAT' },
  { term: 'Spring Y3', code: 'Gen Ed Elective', title: 'FA / HUM / SS' },

  // Year 4
  { term: 'Fall Y4', code: 'CSCE 40003', title: 'Software Engineering' },
  { term: 'Fall Y4', code: 'CSCE 40303', title: 'Ethics and Professional Practice' },
  { term: 'Fall Y4', code: 'Conc/Elective 3', title: 'Concentration / CS/MATH/STAT' },
  { term: 'Fall Y4', code: 'History / Government', title: 'US History / Gov' },
  { term: 'Fall Y4', code: 'Gen Ed Elective', title: 'FA / HUM / SS' },

  { term: 'Spring Y4', code: 'CSCE 40203', title: 'Senior Capstone' },
  { term: 'Spring Y4', code: 'CSCE 40433', title: 'Formal Languages' },
  { term: 'Spring Y4', code: 'Conc/Elective 4', title: 'Concentration / CS/MATH/STAT' },
  { term: 'Spring Y4', code: 'MATH/STAT UL', title: 'UL Math/Stat Elective' },
  { term: 'Spring Y4', code: 'Gen Ed Elective', title: 'FA / HUM / SS' }
]

/* =========================================================
   2. STUDENT NAME (flattened – no nested ref)
========================================================= */
const studentName = ref('')

const greetingName = computed(() =>
  studentName.value.trim() ? studentName.value : '[Student Name]'
)

/* =========================================================
   3. CURRENT SEMESTER
========================================================= */
interface CurrentRow {
  number: string
  name: string
}

interface CurrentPopupRow {
  number: string
  course: string
  time: string
  location: string
  professor: string
  availability: string
  waitlist: string
}

const currentDialog = ref(false)

const currentSchedule = ref<CurrentRow[]>([
  { number: 'CS 4303',  name: 'Cybersecurity Fundamentals' },
  { number: 'CS 4403',  name: 'Artificial Intelligence' },
  { number: 'CS 4983',  name: 'Senior Capstone I' },
  { number: 'COMM 1303',name: 'Oral Communication' },
  { number: '—',        name: '—' },
  { number: '—',        name: '—' },
])

const currentPopupRows = ref<CurrentPopupRow[]>([
  { number: 'CS 4303',   course: 'Cybersecurity Fundamentals', time: 'TBA', location: 'Baldor TBA', professor: 'TBA', availability: 'Open',     waitlist: '0' },
  { number: 'CS 4403',   course: 'Artificial Intelligence',    time: 'TBA', location: 'Baldor TBA', professor: 'TBA', availability: 'Open',     waitlist: '0' },
  { number: 'CS 4983',   course: 'Senior Capstone I',          time: 'TBA', location: 'Baldor TBA', professor: 'TBA', availability: 'By Permit', waitlist: '—' },
  { number: 'COMM 1303', course: 'Oral Communication',         time: 'TBA', location: 'Campus TBA', professor: 'TBA', availability: 'Open',     waitlist: '0' },
  { number: '',          course: '',                           time: '',    location: '',            professor: '',   availability: '',         waitlist: '' },
])

/* =========================================================
   4. NEXT SEMESTER (editable + saved)
========================================================= */
interface NextCardRow {
  number: string
  name: string
}

interface NextPopupRow {
  number: string
  course: string
  time: string
  location: string
  professor: string
  availability: string
  waitlist: string
}

const nextDialog = ref(false)

// terms available from degree plan
const degreePlanTerms = Array.from(new Set(DEGREE_PLAN.map(c => c.term)))

// default: you're planning the very last term
const nextTerm = ref<string>('Spring Y4')

// localStorage key
const STORAGE_KEY = 'uafs-cs-next-semester-schedule'

// main card (6 rows)
const nextSchedule = ref<NextCardRow[]>([
  { number: 'CSCE 40203',  name: 'Senior Capstone' },
  { number: 'CSCE 40433',  name: 'Formal Languages' },
  { number: 'Conc/Elective 4', name: 'Concentration / CS/MATH/STAT' },
  { number: 'MATH/STAT UL',    name: 'Upper-Level Math/Stat' },
  { number: '—',               name: '—' },
  { number: '—',               name: '—' },
])

// dialog rows (detailed)
const nextPopupRows = ref<NextPopupRow[]>([
  { number: 'CSCE 40203',  course: 'Senior Capstone',          time: 'TBA', location: 'Baldor TBA', professor: 'TBA', availability: 'By Permit', waitlist: '—' },
  { number: 'CSCE 40433',  course: 'Formal Languages',         time: 'TBA', location: 'Baldor TBA', professor: 'TBA', availability: 'Open',      waitlist: '0' },
  { number: 'Conc/Elective 4',  course: 'Concentration / CS/MATH/STAT', time: 'TBA', location: 'Baldor TBA', professor: 'TBA', availability: 'Open',      waitlist: '0' },
  { number: 'MATH/STAT UL',  course: 'Upper-Level Math/Stat',  time: 'TBA', location: 'Campus TBA', professor: 'TBA', availability: 'Open',      waitlist: '0' },
  { number: '',            course: '',                          time: '',    location: '',            professor: '',   availability: '',          waitlist: '' },
])

// for the v-select in the dialog
const selectedDegreeCourse = ref<string | null>(null)

const filteredDegreeOptions = computed(() =>
  DEGREE_PLAN
    .filter(c => c.term === nextTerm.value)
    .map(c => ({
      label: `${c.code} — ${c.title}`,
      value: c.code
    }))
)

/* =========================================================
   5. LOCALSTORAGE (load/save)
========================================================= */
onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (!saved) return
  try {
    const parsed = JSON.parse(saved)
    if (parsed.nextSchedule) nextSchedule.value = parsed.nextSchedule
    if (parsed.nextPopupRows) nextPopupRows.value = parsed.nextPopupRows
    if (parsed.nextTerm) nextTerm.value = parsed.nextTerm
  } catch (e) {
    // ignore bad save
  }
  // make sure card view matches dialog after load
  syncNextCardFromPopup()
})

watch(
  [nextSchedule, nextPopupRows, nextTerm],
  () => {
    const payload = {
      nextSchedule: nextSchedule.value,
      nextPopupRows: nextPopupRows.value,
      nextTerm: nextTerm.value
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  },
  { deep: true }
)

/* =========================================================
   6. NEXT SEMESTER ACTIONS
========================================================= */
function syncNextCardFromPopup() {
  const nonEmpty = nextPopupRows.value.filter(r => r.number && r.course).slice(0, 6)
  while (nonEmpty.length < 6) {
    nonEmpty.push({ number: '—', name: '—' } as unknown as NextPopupRow)
  }
  nextSchedule.value = nonEmpty.map(r => ({
    number: r.number,
    name: r.course || r.number
  }))
}

function addNextCourseFromPlan() {
  if (!selectedDegreeCourse.value) return

  const course = DEGREE_PLAN.find(
    c => c.term === nextTerm.value && c.code === selectedDegreeCourse.value
  )
  if (!course) return

  const newRow: NextPopupRow = {
    number: course.code,
    course: course.title,
    time: 'TBA',
    location: 'Baldor TBA',
    professor: 'TBA',
    availability: 'Open',
    waitlist: '0'
  }

  const emptyIdx = nextPopupRows.value.findIndex(r => !r.number)
  if (emptyIdx !== -1) {
    nextPopupRows.value[emptyIdx] = newRow
  } else {
    nextPopupRows.value.push(newRow)
  }

  syncNextCardFromPopup()
  selectedDegreeCourse.value = null
}

function removeNextRow(index: number) {
  nextPopupRows.value.splice(index, 1)
  // keep 5 rows for layout
  while (nextPopupRows.value.length < 5) {
    nextPopupRows.value.push({
      number: '',
      course: '',
      time: '',
      location: '',
      professor: '',
      availability: '',
      waitlist: ''
    })
  }
  syncNextCardFromPopup()
}
</script>

<template>
  <v-container
    fluid
    class="pa-4"
    style="max-width:1500px; background-color: #BDD5E7; border-radius:12px; border: 1px solid #002856;"
  >
    <!-- small greeting so greetingName is actually used -->
    <div class="mb-4" style="color:#002856; font-weight:600;">
      Welcome, {{ greetingName }}!
    </div>

    <v-row dense>
      <!-- CURRENT SEMESTER -->
      <v-col cols="12" md="6" class="pa-3">
        <v-card
          class="pa-0"
          style="background-color:#ffffff; border:1px solid #002856; border-radius:12px;"
        >
          <v-card-title
            class="py-3 px-4"
            style="color:#002856; border-bottom:1px solid #002856;"
          >
            CURRENT SEMESTER SCHEDULE
          </v-card-title>

          <v-card-text class="pa-0">
            <div class="table-wrap">
              <v-table aria-label="Current Semester Schedule">
                <thead>
                  <tr>
                    <th style="width:160px; border-bottom:1px solid #002856;">Course No.</th>
                    <th style="border-left:1px solid #002856; border-bottom:1px solid #002856;">Course</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, i) in currentSchedule" :key="'cur-'+i">
                    <td>{{ row.number }}</td>
                    <td style="border-left:1px solid #002856;">{{ row.name }}</td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </v-card-text>

          <div class="card-fab" style="position:absolute; bottom:22px;">
            <v-btn
              icon
              color="#002856"
              class="elevate-fab"
              aria-label="Add current course"
              @click="currentDialog = true"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>
        </v-card>
      </v-col>

      <!-- NEXT SEMESTER -->
      <v-col cols="12" md="6" class="pa-3">
        <v-card
          class="pa-0"
          style="background-color:#ffffff; border:1px solid #002856; border-radius:12px;"
        >
          <v-card-title
            class="py-3 px-4 d-flex justify-space-between align-center"
            style="color:#002856; border-bottom:1px solid #002856;"
          >
            <span>NEXT SEMESTER SCHEDULE</span>
            <v-chip size="small" color="#002856" variant="flat">
              {{ nextTerm }}
            </v-chip>
          </v-card-title>

          <v-card-text class="pa-0">
            <div class="table-wrap">
              <v-table aria-label="Next semester schedule">
                <thead>
                  <tr>
                    <th style="width:160px; border-bottom:1px solid #002856;">Course No.</th>
                    <th style="border-left:1px solid #002856; border-bottom:1px solid #002856;">Course</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, i) in nextSchedule" :key="'next-'+i">
                    <td>{{ row.number }}</td>
                    <td style="border-left:1px solid #002856;">{{ row.name }}</td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </v-card-text>

          <div class="card-fab" style="position:absolute; bottom:22px;">
            <v-btn
              icon
              color="#002856"
              class="elevate-fab"
              aria-label="Edit next course"
              @click="nextDialog = true"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
          </div>
        </v-card>
      </v-col>

      <!-- ADVISOR -->
      <v-col cols="12" md="6" class="pa-3">
        <v-card
          class="pa-0"
          style="background-color: #F3F8FD; border:1px solid #002856; border-radius:12px;"
        >
          <v-card-title class="pa-3" style="color: #002856; border-bottom: 1px solid #002856;">
            ADVISOR INFORMATION
          </v-card-title>
          <v-list
            density="comfortable"
            style="padding-left: 5px; text-align: left; background-color: transparent"
          >
            <v-list-item>
              <v-list-item-title>
                <strong>Name:</strong> Dr. Dave Stevens
              </v-list-item-title>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>
                <strong>Email:</strong> <a href="mailto:dsteve@uafs.edu">dsteve@uafs.edu</a>
              </v-list-item-title>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>
                <strong>Phone:</strong> (555) 123-4567
              </v-list-item-title>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>
                <strong>Office:</strong> Campus Center 201
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <!-- CURRENT: Dialog -->
    <v-dialog v-model="currentDialog" width="900" aria-label="Current Course Schedule Dialog">
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <span class="text-subtitle-1">Current Course Schedule</span>
          <v-btn icon variant="text" aria-label="Close" @click="currentDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-0">
          <v-table aria-label="Current courses grid">
            <thead>
              <tr>
                <th>Course No.</th>
                <th>Course Name</th>
                <th>Time</th>
                <th>Location</th>
                <th>Professor</th>
                <th>Availability</th>
                <th>Waitlist</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in currentPopupRows" :key="'c-pop-'+i">
                <td>{{ row.number }}</td>
                <td>{{ row.course }}</td>
                <td>{{ row.time }}</td>
                <td>{{ row.location }}</td>
                <td>{{ row.professor }}</td>
                <td>{{ row.availability }}</td>
                <td>{{ row.waitlist }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="currentDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- NEXT: Dialog -->
    <v-dialog v-model="nextDialog" width="1050" aria-label="Next Semester Course Schedule Dialog">
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <span class="text-subtitle-1">Next Semester Course Schedule</span>
          <v-btn icon variant="text" aria-label="Close" @click="nextDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-divider />

        <v-card-text>
          <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="12" md="4">
              <v-select
                v-model="nextTerm"
                :items="degreePlanTerms"
                label="Term (from degree plan)"
                density="comfortable"
              />
            </v-col>
            <v-col cols="12" md="5">
              <v-select
                v-model="selectedDegreeCourse"
                :items="filteredDegreeOptions"
                item-title="label"
                item-value="value"
                label="Choose course from degree plan"
                density="comfortable"
                clearable
              />
            </v-col>
            <v-col cols="12" md="3" class="d-flex justify-end">
              <v-btn color="primary" @click="addNextCourseFromPlan">
                <v-icon start>mdi-plus</v-icon>
                Add to schedule
              </v-btn>
            </v-col>
          </v-row>

          <v-table aria-label="Next semester editable courses grid">
            <thead>
              <tr>
                <th style="width: 115px;">Course No.</th>
                <th>Course Name</th>
                <th style="width: 85px;">Time</th>
                <th style="width: 120px;">Location</th>
                <th style="width: 130px;">Professor</th>
                <th style="width: 110px;">Availability</th>
                <th style="width: 70px;">Waitlist</th>
                <th style="width: 50px;"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in nextPopupRows" :key="'n-pop-'+i">
                <td>{{ row.number }}</td>
                <td>{{ row.course }}</td>
                <td>{{ row.time }}</td>
                <td>{{ row.location }}</td>
                <td>{{ row.professor }}</td>
                <td>{{ row.availability }}</td>
                <td>{{ row.waitlist }}</td>
                <td>
                  <v-btn
                    v-if="row.number"
                    icon
                    size="small"
                    variant="text"
                    color="error"
                    @click="removeNextRow(i)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="nextDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.table-wrap {
  overflow-x: auto;
}

.card-fab {
  position: relative;
  width: 100%;
  height: 0;
}
.card-fab .v-btn {
  position: absolute;
  right: 12px;
  top: -28px;
  border: 1px solid #002856;
  background-color: #ffffff;
}

.student-card {
  transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.12s ease;
  cursor: pointer;
}
.student-card:hover {
  background-color: #D1E5F4;
  border-color: #0050a0;
  transform: translateY(-1px);
}
</style>
