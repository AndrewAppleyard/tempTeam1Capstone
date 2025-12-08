<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../store/user.js'
import StudentAPI from '../apis/StudentAPI.js'
import AdvisorAPI from '../apis/AdvisorAPI.js'
import AppointmentCard from '../components/AppointmentCard.vue'

const route = useRoute()
const userStore = useUserStore()

/* =========================================================
   THEME 
========================================================= */
const COLOR_PRIMARY = '#002856'   // deep navy
const COLOR_SURFACE = '#ffffff'   // white surface
const COLOR_ACCENT_BG = '#BDD5E7' // soft blue page background
const COLOR_PANEL_BG  = '#F3F8FD' // very light blue for info panels

/* =========================================================
   2) STUDENT / ADVISOR INFO
========================================================= */
const advisorId = ref<number | null>(null)
const advisorName = ref('TBA')
const advisorEmail = ref('TBA')
const advisorPhone = ref('TBA')
const studentName = ref('')

const welcomeGreeting = computed(() => {
  if (studentName.value) {
    return `Welcome, ${studentName.value}!`
  } else {
    return 'Welcome, Student!'
  }
})

/** student ID from route OR store */
const studentId = computed<number | null>(() => {
  // route params: support both :id and :studentid
  const routeParam = (route.params.id ?? route.params.studentid) as string | string[] | undefined
  const firstParam = Array.isArray(routeParam) ? routeParam[0] : routeParam
  const routeId = firstParam != null ? Number(firstParam) : NaN
  if (!Number.isNaN(routeId)) return routeId

  const storeId = userStore.userID ? Number(userStore.userID) : NaN
  return Number.isNaN(storeId) ? null : storeId
})

const hasStudentId = computed(() => studentId.value !== null)

interface SemesterData { coursemap: any; courses: TranscriptCourse[] }

function formatPhoneNumber(rawNumber: string | null | undefined): string {
  if (!rawNumber) return 'N/A'
  const cleaned = ('' + rawNumber).replace(/\D/g, '')
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`
  }
  return rawNumber
}

function emptyNextRow(): NextPopupRow {
  return {
    number: '—',
    course: '—',
    time: '',
    location: '',
    professor: '',
    availability: '',
    deliverymode: ''
  }
}

interface SchedulePreferences {
  preferredCreditHours: number | null
  preferredDays: string[]
  timeOfDay: string
  modality: string
  earliestStart: string
  latestEnd: string
  avoidBackToBack: boolean
}

const preferenceDefaults: SchedulePreferences = {
  preferredCreditHours: null,
  preferredDays: [],
  timeOfDay: 'No preference',
  modality: 'No preference',
  earliestStart: '08:00',
  latestEnd: '17:30',
  avoidBackToBack: false
}

const dayOptions = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const timeOfDayOptions = ['Morning', 'Afternoon', 'Evening', 'No preference']
const modalityOptions = ['In-person', 'Online', 'Hybrid', 'No preference']
const timeOptions = [
  { label: '7:00 AM', value: '07:00' },
  { label: '7:30 AM', value: '07:30' },
  { label: '8:00 AM', value: '08:00' },
  { label: '8:30 AM', value: '08:30' },
  { label: '9:00 AM', value: '09:00' },
  { label: '9:30 AM', value: '09:30' },
  { label: '10:00 AM', value: '10:00' },
  { label: '10:30 AM', value: '10:30' },
  { label: '11:00 AM', value: '11:00' },
  { label: '11:30 AM', value: '11:30' },
  { label: '12:00 PM', value: '12:00' },
  { label: '12:30 PM', value: '12:30' },
  { label: '1:00 PM', value: '13:00' },
  { label: '1:30 PM', value: '13:30' },
  { label: '2:00 PM', value: '14:00' },
  { label: '2:30 PM', value: '14:30' },
  { label: '3:00 PM', value: '15:00' },
  { label: '3:30 PM', value: '15:30' },
  { label: '4:00 PM', value: '16:00' },
  { label: '4:30 PM', value: '16:30' },
  { label: '5:00 PM', value: '17:00' },
  { label: '5:30 PM', value: '17:30' },
  { label: '6:00 PM', value: '18:00' },
  { label: '6:30 PM', value: '18:30' },
  { label: '7:00 PM', value: '19:00' },
  { label: '7:30 PM', value: '19:30' },
  { label: '8:00 PM', value: '20:00' },
  { label: '8:30 PM', value: '20:30' },
  { label: '9:00 PM', value: '21:00' }
]
const timeOptionValues = timeOptions.map(t => t.value)
const timeLabelByValue = Object.fromEntries(timeOptions.map(t => [t.value, t.label]))
const timeValueByLabel = Object.fromEntries(timeOptions.map(t => [t.label.toLowerCase(), t.value]))

const preferencesDialog = ref(false)
const preferenceForm = ref<SchedulePreferences>({ ...preferenceDefaults })
const preferencesLoaded = ref(false)
const loadingPreferences = ref(false)
const savingPreferences = ref(false)
const preferenceLoadError = ref('')
const preferenceSnackbar = ref(false)
const preferenceSnackbarColor = ref<'success' | 'error' | 'info'>('success')
const preferenceSnackbarMessage = ref('')
const preferenceSnackbarTimeout = ref(3000)

/* =========================================================
   3) CURRENT SEMESTER DATA
========================================================= */
interface CurrentRow { number: string; name: string }
interface CurrentPopupRow {
  number: string
  course: string
  time: string
  location: string
  professor: string
}

interface TranscriptCourse {
  code: string;
  title: string;
}

const currentDialog = ref(false)
const currentSchedule = ref<CurrentRow[]>([])
const currentPopupRows = ref<CurrentPopupRow[]>([])

/* =========================================================
   4) NEXT SEMESTER DATA (editable + saved)
========================================================= */
interface NextCardRow { number: string; name: string }
interface NextPopupRow {
  number: string
  course: string
  time: string
  location: string
  professor: string
  availability: string
  deliverymode: string
}
interface StoredClass {
  number: string
  name: string
  meetingpattern?: string
  courselocation?: string
  instructor?: string
  courseavailability?: string
  deliverymode?: string
}

const nextDialog = ref(false)
const STORAGE_KEY = 'uafs-cs-next-semester-schedule'

const nextSchedule = ref<NextCardRow[]>([])
const nextPopupRows = ref<NextPopupRow[]>([])

function showPreferenceSnackbar(message: string, color: 'success' | 'error' | 'info' = 'success', duration = 3000) {
  preferenceSnackbarMessage.value = message
  preferenceSnackbarColor.value = color
  preferenceSnackbarTimeout.value = duration
  preferenceSnackbar.value = true
}

function normalizeTime(value: any, fallback: string) {
  if (typeof value !== 'string') return fallback
  if (timeOptionValues.includes(value)) return value
  const mapped = timeValueByLabel[value.toLowerCase()]
  return mapped || fallback
}

function normalizePreferences(raw: any): SchedulePreferences {
  const safe = raw && typeof raw === 'object' ? raw : {}
  return {
    preferredCreditHours: typeof safe.preferredCreditHours === 'number'
      ? safe.preferredCreditHours
      : safe.preferredCreditHours
        ? Number(safe.preferredCreditHours)
        : preferenceDefaults.preferredCreditHours,
    preferredDays: Array.isArray(safe.preferredDays) ? safe.preferredDays : preferenceDefaults.preferredDays,
    timeOfDay: typeof safe.timeOfDay === 'string' ? safe.timeOfDay : preferenceDefaults.timeOfDay,
    modality: typeof safe.modality === 'string' ? safe.modality : preferenceDefaults.modality,
    earliestStart: normalizeTime(safe.earliestStart, preferenceDefaults.earliestStart),
    latestEnd: normalizeTime(safe.latestEnd, preferenceDefaults.latestEnd),
    avoidBackToBack: typeof safe.avoidBackToBack === 'boolean'
      ? safe.avoidBackToBack
      : typeof safe.avoidBackToBack === 'string'
        ? safe.avoidBackToBack.toLowerCase() === 'true'
        : preferenceDefaults.avoidBackToBack
  }
}

async function loadStudentProfile() {
  if (!studentId.value) return
  loadingPreferences.value = true
  preferenceLoadError.value = ''
  try {
    const data = await StudentAPI.getStudentById(studentId.value)
    const student = data?.student

    if (student) {
      const name = [student.firstname, student.lastname].filter(Boolean).join(' ').trim()
      if (name) studentName.value = name
      preferenceForm.value = normalizePreferences(student.preferences)
    } else {
      preferenceForm.value = { ...preferenceDefaults }
    }
    preferencesLoaded.value = true
  } catch (err) {
    console.error('Get Student error: ', err)
    preferenceLoadError.value = 'Unable to load your saved preferences right now.'
  } finally {
    loadingPreferences.value = false
  }
}

function openPreferencesDialog() {
  if (!studentId.value) {
    showPreferenceSnackbar('No student selected to save preferences.', 'error')
    return
  }
  preferencesDialog.value = true
  if (!preferencesLoaded.value && !loadingPreferences.value) {
    loadStudentProfile()
  }
}

async function savePreferences() {
  if (!studentId.value) {
    showPreferenceSnackbar('No student selected to save preferences.', 'error')
    return
  }
  savingPreferences.value = true
  try {
    const preferredHours = preferenceForm.value.preferredCreditHours
    const startValue = normalizeTime(preferenceForm.value.earliestStart, preferenceDefaults.earliestStart)
    const endValue = normalizeTime(preferenceForm.value.latestEnd, preferenceDefaults.latestEnd)
    const payload = {
      ...preferenceForm.value,
      preferredCreditHours: preferredHours === null || Number.isNaN(Number(preferredHours))
        ? null
        : Number(preferredHours),
      earliestStart: timeLabelByValue[startValue] || startValue,
      latestEnd: timeLabelByValue[endValue] || endValue
    }
    await StudentAPI.savePreferences(studentId.value, payload)
    showPreferenceSnackbar('Preferences saved to your student record.', 'success')
    preferencesDialog.value = false
    preferencesLoaded.value = true
  } catch (err) {
    console.error('Save preferences error: ', err)
    showPreferenceSnackbar('Could not save preferences. Please try again.', 'error')
  } finally {
    savingPreferences.value = false
  }
}

/* =========================================================
   5) PROGRAM CHANGE REQUEST FORM
========================================================= */
interface ChangeRequestForm {
  action: string;
  currentMajor: string;
  currentMinor: string;
  requestedMajor: string;
  requestedMinor: string;
  effectiveTerm: string;
  catalogYear: string;
  reason: string;
}

const changeRequestDialog = ref(false)
const changeRequestSubmitting = ref(false)

const changeRequestForm = ref<ChangeRequestForm>({
  action: '',
  currentMajor: '',
  currentMinor: '',
  requestedMajor: '',
  requestedMinor: '',
  effectiveTerm: '',
  catalogYear: '',
  reason: ''
})

const changeRequestErrors = ref<Record<string, string | null>>({})

const changeRequestActionOptions = [
  'Change Major',
  'Change Minor',
  'Add Minor',
  'Drop Minor'
]

function resetChangeRequestForm() {
  changeRequestForm.value = {
    action: '',
    currentMajor: '',
    currentMinor: '',
    requestedMajor: '',
    requestedMinor: '',
    effectiveTerm: '',
    catalogYear: '',
    reason: ''
  }
  changeRequestErrors.value = {}
}

function validateChangeRequest(): boolean {
  const errors: Record<string, string | null> = {}
  const f = changeRequestForm.value

  const requiredFields: (keyof ChangeRequestForm)[] = [
    'action',
    'currentMajor',
    'currentMinor',
    'requestedMajor',
    'requestedMinor',
    'effectiveTerm',
    'catalogYear',
    'reason'
  ]

  requiredFields.forEach(key => {
    const value = (f[key] || '').toString().trim()
    if (!value) {
      errors[key] = 'This field is required.'
    }
  })

  changeRequestErrors.value = errors
  return Object.keys(errors).length === 0
}

async function submitChangeRequest() {
  if (!validateChangeRequest()) return

  changeRequestSubmitting.value = true
  try {
    console.log('Program change request payload:', {
      studentId: studentId.value,
      ...changeRequestForm.value
    })

    alert('Your request has been submitted. Your advisor will review it shortly.')
    changeRequestDialog.value = false
    resetChangeRequestForm()
  } catch (err) {
    console.error('Failed to submit change request:', err)
    alert('We were unable to submit your request. Please try again or contact your advisor.')
  } finally {
    changeRequestSubmitting.value = false
  }
}

/* =========================================================
   6) PERSISTENCE (load / save next-semester)
========================================================= */
function syncNextCardFromPopup() {
  const present = nextPopupRows.value
    .filter(r => r.number && r.number !== '')
    .slice(0, 6)

  while (present.length < 6) {
    present.push(emptyNextRow())
  }

  nextSchedule.value = present.map(r => ({
    number: r.number,
    name: r.course || r.number
  }))

  while (nextPopupRows.value.length < 6) {
    nextPopupRows.value.push(emptyNextRow())
  }
}

function splitCodeTitle(raw: string) {
  const parts = (raw || '').split(' - ')
  if (parts.length >= 2) {
    return { code: parts[0].trim(), title: parts.slice(1).join(' - ').trim() }
  }
  return { code: raw || '—', title: raw || '—' }
}

function deriveCodeAndTitle(cls: any) {
  const candidates = [cls?.section, cls?.name, cls?.title, cls?.number, cls?.code].filter(Boolean)
  for (const cand of candidates) {
    if (typeof cand === 'string' && cand.includes(' - ')) {
      return splitCodeTitle(cand)
    }
  }
  const raw = candidates.find(c => typeof c === 'string') || ''
  return splitCodeTitle(raw)
}

function normalizeClass(cls: any) {
  const { code, title } = deriveCodeAndTitle(cls)
  return {
    number: code || '—',
    name: title || cls?.name || cls?.title || cls?.number || cls?.code || '—'
  }
}

function normalizeClassDetailed(cls: any): StoredClass {
  const base = normalizeClass(cls)
  return {
    ...base,
    meetingpattern: cls?.meetingpattern || cls?.meeting_pattern,
    courselocation: cls?.courselocation || cls?.location,
    instructor: cls?.instructor,
    courseavailability: cls?.courseavailability || cls?.status,
    deliverymode: cls?.deliverymode || cls?.delivery_mode
  }
}

function populateClassesFromStudent(userData: any) {
  let fetchedClasses: StoredClass[] = []

  if (userData && Array.isArray(userData.classes)) {
    fetchedClasses = userData.classes.map((cls: any) => normalizeClassDetailed(cls))
  }
  if (userData && typeof userData.classes === 'string') {
    try {
      const parsedClasses = JSON.parse(userData.classes)
      if (Array.isArray(parsedClasses)) {
        fetchedClasses = parsedClasses.map((cls: any) => normalizeClassDetailed(cls))
      }
    } catch (e) {
      console.error('Failed to parse student classes JSON string:', e)
    }
  }

  const classesForCard = fetchedClasses.slice(0, 6)

  if (classesForCard.length > 0 && classesForCard.some(c => c.number !== '—')) {
    while (classesForCard.length < 6) {
      classesForCard.push({ number: '—', name: '—' })
    }
    nextSchedule.value = classesForCard.map(c => ({ number: c.number, name: c.name }))

    nextPopupRows.value = fetchedClasses.map((cls: StoredClass) => ({
      number: cls.number,
      course: cls.name,
      time: cls.meetingpattern || 'TBA',
      location: cls.courselocation || 'TBA',
      professor: cls.instructor || 'TBA',
      availability: cls.courseavailability || 'Open',
      deliverymode: cls.deliverymode || 'TBA'
    }))
  }

  return fetchedClasses
}


/* =========================================================
   7) DATA LOAD (student, transcripts, advisor)
========================================================= */
onMounted(async () => {
  // --- Student + next-schedule data
  if (studentId.value) await loadStudentProfile()

  if (!nextPopupRows.value.length || nextPopupRows.value.every(r => !r.number)) {
    nextPopupRows.value = Array(6).fill(null).map(emptyNextRow)
    syncNextCardFromPopup()
  }

  if (studentId.value) {
    loadStudentProfile()
  }

  // --- Student data (for name + next schedule seed)
  try {
    if (studentId.value) {
      const response = await StudentAPI.getStudentById(studentId.value)
      const userData = response.student

      if (userData && userData.firstname && userData.lastname) {
        studentName.value = `${userData.firstname} ${userData.lastname}`
      } else if (userData && userData.firstname) {
        studentName.value = userData.firstname
      }
      populateClassesFromStudent(userData)
    }
  } catch (err) {
    console.error('Failed to fetch student data:', err)
  }

  // --- Transcripts -> current schedule
  try {
    if (studentId.value) {
      const transcripts = await StudentAPI.getTranscripts(studentId.value)

      let semesterCourses: SemesterData[] = []

      if (transcripts.length > 0) {
        transcripts.sort((a: any, b: any) => b.year - a.year)
        const mostRecentTranscript = transcripts[0]

        if (mostRecentTranscript.coursemap) {
          let coursemapData = mostRecentTranscript.coursemap

          if (Array.isArray(coursemapData)) {
            semesterCourses = coursemapData
          } else if (typeof coursemapData === 'string') {
            try {
              semesterCourses = JSON.parse(coursemapData)
            } catch (e) {
              console.error('Error parsing coursemap string:', e)
            }
          }

          if (!Array.isArray(semesterCourses)) {
            semesterCourses = []
          }
        }

        const lastSemester = semesterCourses[semesterCourses.length - 1]

        const semesterOnlyCourses: TranscriptCourse[] = Array.isArray(lastSemester?.courses)
          ? lastSemester.courses
          : []

        const allCourses: TranscriptCourse[] = semesterCourses.flatMap(
          (s: any) => Array.isArray(s.courses) ? s.courses : []
        )

        const cardCourses: CurrentRow[] = semesterOnlyCourses.map(c => ({
          number: c.code || '—',
          name: c.title || '—'
        }))

        while (cardCourses.length < 6) {
          cardCourses.push({ number: '—', name: '—' })
        }
        currentSchedule.value = cardCourses

        currentPopupRows.value = semesterOnlyCourses.map(c => ({
          number: c.code || '—',
          course: c.title || '—',
          time: 'N/A (Completed)',
          location: mostRecentTranscript.institution || 'N/A',
          professor: 'N/A'
        }))

        while (currentPopupRows.value.length < 5) {
          currentPopupRows.value.push({
            number: '',
            course: '',
            time: '',
            location: '',
            professor: ''
          })
        }
      } else {
        const emptyCardCourses: CurrentRow[] = []
        while (emptyCardCourses.length < 6) {
          emptyCardCourses.push({ number: '—', name: '—' })
        }
        currentSchedule.value = emptyCardCourses
        currentPopupRows.value = []
      }
    } else {
      const emptyCardCourses: CurrentRow[] = []
      while (emptyCardCourses.length < 6) {
        emptyCardCourses.push({ number: '—', name: '—' })
      }
      currentSchedule.value = emptyCardCourses
      currentPopupRows.value = []
    }
  } catch (e) {
    console.error('Failed to load or process transcripts for current schedule:', e)
    const emptyCardCourses: CurrentRow[] = []
    while (emptyCardCourses.length < 6) {
      emptyCardCourses.push({ number: '—', name: '—' })
    }
    currentSchedule.value = emptyCardCourses
  }

  // --- Advisor data
  try {
    if (studentId.value) {
      const advisorData = await AdvisorAPI.getAdvisorByStudent(studentId.value)
      if (advisorData) {
        advisorName.value = `${advisorData.firstname} ${advisorData.lastname}`
        advisorEmail.value = advisorData.email || 'N/A'
        advisorPhone.value = advisorData.phonenumber || 'N/A'

        advisorId.value = advisorData.userid || null
      }
    }
  } catch (err) {
    console.error('Failed to fetch advisor data:', err)
  }
})

watch(studentId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    preferencesLoaded.value = false
    preferenceLoadError.value = ''
    loadStudentProfile()
  }
})

async function generateSchedule() {
  if (!studentId.value) {
    showPreferenceSnackbar('No student selected to generate a schedule.', 'error')
    return
  }
  try {
    await StudentAPI.addSchedule(studentId.value)
    showPreferenceSnackbar('Schedule generation submitted.', 'info')
    // refresh classes if user is on this screen
    const refreshed = await StudentAPI.getStudentById(studentId.value)
    if (refreshed?.student) {
      populateClassesFromStudent(refreshed.student)
    }
  } catch (err) {
    console.error('Generate Schedule error: ', err)
    alert('Failed to generate schedule.')
  }
}

async function runHoldCheck() {
  if (!studentId.value) {
    showPreferenceSnackbar('No student selected to check advising holds.', 'error')
    return
  }
  try {
    const response = await StudentAPI.checkAdvisingHold(studentId.value);
    const result = response?.result || {}
    const lifted = !!result.lift_advising_hold
    const reason = result.reason || 'No reason provided.'
    if (lifted) {
      showPreferenceSnackbar(`Advising hold lifted: ${reason}`, 'success', 10000)
    } else {
      showPreferenceSnackbar(`Advising hold remains: ${reason}`, 'error', 10000)
    }
  } catch (err) {
    console.error(err);
    showPreferenceSnackbar('Error checking advising hold.', 'error', 10000)
  }
}
</script>

<template>
  <v-container
    fluid
    class="pa-6 respectful-shell"
    :style="{
      maxWidth: '1500px',
      backgroundColor: COLOR_ACCENT_BG,
      borderRadius: '16px',
      border: `1px solid ${COLOR_PRIMARY}`
    }"
  >
    <!-- Header: Degree Planner LEFT, Welcome center, Actions RIGHT -->
    <header class="mb-4 layout-head">
      <v-row align="center" class="header-grid">
        <v-col cols="12" md="4" class="text-left">
          <div class="planner-left" :style="{ color: COLOR_PRIMARY }">
            Degree Planner
          </div>
        </v-col>

        <v-col cols="12" md="4" class="text-center">
          <h1 class="welcome-center" :style="{ color: COLOR_PRIMARY }">
           {{ welcomeGreeting }}
          </h1>
        </v-col>

        <v-col
          cols="12"
          md="4"
          class="text-right d-flex flex-column align-end header-actions"
        >
          <v-btn
            class="request-btn mb-2"
            variant="outlined"
            :style="{
              borderColor: COLOR_PRIMARY,
              color: COLOR_PRIMARY
            }"
            @click="changeRequestDialog = true"
          >
            <v-icon start>mdi-file-document-edit-outline</v-icon>
            Request Major / Minor Change
          </v-btn>

          <div class="d-flex flex-wrap justify-end" style="gap:8px;">
            <v-btn :disabled="!hasStudentId" color="primary" @click="generateSchedule">
              <v-icon start>mdi-calendar-refresh</v-icon>
              Generate Schedule
            </v-btn>
            <v-btn :disabled="!hasStudentId" color="primary" variant="tonal" @click="runHoldCheck">
              <v-icon start>mdi-shield-check-outline</v-icon>
              Check Advising Hold
            </v-btn>
            <v-btn :disabled="!hasStudentId" variant="outlined" color="#002856" @click="openPreferencesDialog">
              <v-icon start>mdi-clipboard-text</v-icon>
              Schedule Preferences
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </header>

    <v-row dense>
      <!-- CURRENT SEMESTER -->
      <v-col cols="12" md="6" class="pa-3">
        <v-card class="panel-card ensure-fab-visibility">
          <v-card-title class="panel-title">
            <v-icon size="20" class="mr-2">mdi-calendar-month</v-icon>
            Current Semester
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-0">
            <div class="table-wrap">
              <v-table
                density="comfortable"
                class="zebra sticky-head align-left with-divider"
                aria-label="Current Semester Schedule"
              >
                <thead>
                  <tr>
                    <th class="th-narrow">Course No.</th>
                    <th>Course</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, i) in currentSchedule" :key="`cur-${i}`">
                    <td>{{ row.number }}</td>
                    <td>{{ row.name }}</td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </v-card-text>
          <div class="card-fab">
            <v-tooltip text="View details">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  class="fab-btn"
                  :color="COLOR_PRIMARY"
                  aria-label="Open current schedule details"
                  @click="currentDialog = true"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-tooltip>
          </div>
        </v-card>
      </v-col>

      <!-- NEXT SEMESTER -->
      <v-col cols="12" md="6" class="pa-3">
        <v-card class="panel-card ensure-fab-visibility">
          <v-card-title class="panel-title">
            <v-icon size="20" class="mr-2">mdi-calendar-edit</v-icon>
            Next Semester
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-0">
            <div class="table-wrap">
              <v-table
                density="comfortable"
                class="zebra sticky-head align-left with-divider"
                aria-label="Next semester schedule"
              >
                <thead>
                  <tr>
                    <th class="th-narrow">Course No.</th>
                    <th>Course</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, i) in nextSchedule" :key="`next-${i}`">
                    <td>{{ row.number }}</td>
                    <td>{{ row.name }}</td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </v-card-text>
          <div class="card-fab">
            <v-tooltip text="View next semester">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  class="fab-btn"
                  :color="COLOR_PRIMARY"
                  aria-label="View next semester schedule"
                  @click="nextDialog = true"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-tooltip>
          </div>
        </v-card>
      </v-col>

      <!-- ADVISOR INFO -->
      <!-- <v-col cols="12" md="6" class="pa-3" style="text-align: left;">
        <v-card class="panel-card" :style="{ backgroundColor: COLOR_PANEL_BG }">
          <v-card-title class="panel-title">
            <v-icon size="20" class="mr-2">mdi-account-tie</v-icon>
            Advisor Information
          </v-card-title>
          <v-divider />
          <v-list density="comfortable" class="info-list">
            <v-list-item class="info-item">
              <strong>Name:</strong> {{ advisorName }}
            </v-list-item>
            <v-list-item class="info-item">
              <strong>Email: </strong>
              <a
                :href="'mailto:' + advisorEmail"
                v-if="advisorEmail !== 'TBA' && advisorEmail !== 'N/A'"
              >
                {{ advisorEmail }}
              </a>
              <span v-else>{{ advisorEmail }}</span>
            </v-list-item>
            <v-list-item class="info-item">
              <strong>Phone:</strong> {{ formatPhoneNumber(advisorPhone) }}
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row> -->
    <v-col cols="12" md="6" class="pa-3" style="text-align: left;">
    <AppointmentCard
          :advisor-id="advisorId"
          :advisor-name="advisorName"
          :advisor-email="advisorEmail"
          :advisor-phone="advisorPhone"
          :student-id="studentId"
          :has-student-id="hasStudentId"
          :format-phone-number="formatPhoneNumber"
        />
    </v-col>
  </v-row dense>
      

    <!-- CURRENT: Dialog -->
    <v-dialog
      v-model="currentDialog"
      width="900"
      aria-label="Current Course Schedule Dialog"
    >
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon size="18" class="mr-2">mdi-calendar-month-outline</v-icon>
          Current Course Schedule
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-0">
          <v-table class="zebra align-left with-divider">
            <thead>
              <tr>
                <th>Course No.</th>
                <th>Course Name</th>
                <th>Time</th>
                <th>Location</th>
                <th>Professor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in currentPopupRows" :key="`c-pop-${i}`">
                <td>{{ row.number }}</td>
                <td>{{ row.course }}</td>
                <td>{{ row.time }}</td>
                <td>{{ row.location }}</td>
                <td>{{ row.professor }}</td>
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
    <v-dialog
      v-model="nextDialog"
      width="1200"
      aria-label="Next Semester Course Schedule Dialog"
    >
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          Next Semester Course Schedule
        </v-card-title>
        <v-divider />

        <v-card-text>
          <v-table class="zebra align-left with-divider next-popup-table">
            <thead>
              <tr>
                <th style="width: 115px;">Course No.</th>
                <th>Course Name</th>
                <th style="width: 85px;">Time</th>
                <th style="width: 120px;">Location</th>
                <th style="width: 130px;">Professor</th>
                <th style="width: 110px;">Availability</th>
                <th style="width: 110px;">Delivery</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in nextPopupRows" :key="`n-pop-${i}`">
                <td>{{ row.number }}</td>
                <td>{{ row.course }}</td>
                <td>{{ row.time }}</td>
                <td>{{ row.location }}</td>
                <td>{{ row.professor }}</td>
                <td>{{ row.availability }}</td>
                <td>{{ row.deliverymode }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="nextDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- PREFERENCES: Dialog -->
    <v-dialog v-model="preferencesDialog" width="780" aria-label="Schedule Preferences Dialog">
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          Schedule Preferences
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-alert
            v-if="preferenceLoadError"
            type="error"
            density="comfortable"
            class="mb-3"
            variant="tonal"
          >
            {{ preferenceLoadError }}
          </v-alert>
          <v-progress-linear
            v-if="loadingPreferences"
            color="primary"
            indeterminate
            class="mb-3"
          />
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model.number="preferenceForm.preferredCreditHours"
                type="number"
                min="1"
                max="21"
                step="1"
                label="Preferred credit hours"
                density="comfortable"
                :disabled="loadingPreferences"
                hint="Total hours you want to carry next term"
                persistent-hint
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="preferenceForm.preferredDays"
                :items="dayOptions"
                label="Days you prefer on campus"
                multiple
                chips
                closable-chips
                density="comfortable"
                :disabled="loadingPreferences"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="preferenceForm.timeOfDay"
                :items="timeOfDayOptions"
                label="Time of day"
                density="comfortable"
                :disabled="loadingPreferences"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="preferenceForm.modality"
                :items="modalityOptions"
                label="Course modality"
                density="comfortable"
                :disabled="loadingPreferences"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="preferenceForm.earliestStart"
                :items="timeOptions"
                item-title="label"
                item-value="value"
                label="Earliest start time"
                density="comfortable"
                :disabled="loadingPreferences"
                clearable
                hint="Pick a start time"
                persistent-hint
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="preferenceForm.latestEnd"
                :items="timeOptions"
                item-title="label"
                item-value="value"
                label="Latest end time"
                density="comfortable"
                :disabled="loadingPreferences"
                clearable
                hint="Pick an end time"
                persistent-hint
              />
            </v-col>
            <v-col cols="12">
              <v-checkbox
                v-model="preferenceForm.avoidBackToBack"
                label="Try to avoid back-to-back classes"
                density="comfortable"
                :disabled="loadingPreferences"
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="preferencesDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="savingPreferences"
            :disabled="savingPreferences || loadingPreferences || !hasStudentId"
            @click="savePreferences"
          >
            Save preferences
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="preferenceSnackbar"
      :color="preferenceSnackbarColor"
      location="bottom right"
      :timeout="preferenceSnackbarTimeout"
    >
      {{ preferenceSnackbarMessage }}
      <template #actions>
        <v-btn icon variant="text" @click="preferenceSnackbar = false">
          <v-icon size="18">mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>

    <!-- PROGRAM CHANGE REQUEST: Dialog -->
    <v-dialog
      v-model="changeRequestDialog"
      width="800"
      aria-label="Major / Minor Change Request Form Dialog"
    >
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon size="18" class="mr-2">mdi-file-document-edit-outline</v-icon>
          Major / Minor Change Request
        </v-card-title>
        <v-divider />
        <v-card-text>
          <p class="mb-4 text-body-2" style="color:#002856;">
            Please complete all fields below to request a change of major or
            minor. Your advisor will review your request and follow up with you
            using your UAFS contact information.
          </p>

          <v-form @submit.prevent="submitChangeRequest">
            <v-row dense>
              <v-col cols="12" md="6">
                <v-select
                  v-model="changeRequestForm.action"
                  :items="changeRequestActionOptions"
                  label="Request type"
                  density="comfortable"
                  required
                  :error-messages="changeRequestErrors.action ? [changeRequestErrors.action] : []"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="changeRequestForm.effectiveTerm"
                  label="Requested effective term (e.g., Fall 2026)"
                  density="comfortable"
                  required
                  :error-messages="changeRequestErrors.effectiveTerm ? [changeRequestErrors.effectiveTerm] : []"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="changeRequestForm.currentMajor"
                  label="Current major"
                  density="comfortable"
                  required
                  :error-messages="changeRequestErrors.currentMajor ? [changeRequestErrors.currentMajor] : []"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="changeRequestForm.currentMinor"
                  label="Current minor(s)"
                  density="comfortable"
                  required
                  :error-messages="changeRequestErrors.currentMinor ? [changeRequestErrors.currentMinor] : []"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="changeRequestForm.requestedMajor"
                  label="Requested major"
                  density="comfortable"
                  required
                  :error-messages="changeRequestErrors.requestedMajor ? [changeRequestErrors.requestedMajor] : []"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="changeRequestForm.requestedMinor"
                  label="Requested minor (or N/A)"
                  density="comfortable"
                  required
                  :error-messages="changeRequestErrors.requestedMinor ? [changeRequestErrors.requestedMinor] : []"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="changeRequestForm.catalogYear"
                  label="Catalog year (e.g., 2024–2025)"
                  density="comfortable"
                  required
                  :error-messages="changeRequestErrors.catalogYear ? [changeRequestErrors.catalogYear] : []"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="changeRequestForm.reason"
                  label="Briefly explain the reason for this change"
                  density="comfortable"
                  rows="3"
                  auto-grow
                  required
                  :error-messages="changeRequestErrors.reason ? [changeRequestErrors.reason] : []"
                />
              </v-col>
            </v-row>

            <div class="d-flex justify-end mt-4">
              <v-btn
                variant="text"
                class="mr-2"
                @click="changeRequestDialog = false"
              >
                Cancel
              </v-btn>
              <v-btn
                type="submit"
                color="primary"
                :loading="changeRequestSubmitting"
                :disabled="changeRequestSubmitting"
              >
                <v-icon start>mdi-send</v-icon>
                Submit Request
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>

  </v-container>

  <v-container fluid class="pa-2" style="background-color: transparent;">
    <div class="text-center mt-6 brand-primary">
      © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
    </div>
  </v-container>
</template>

<style scoped>
/* =========================================================
   BASE IMPROVEMENTS — subtle, respectful, not flashy
========================================================= */
.respectful-shell {
  box-shadow: 0 1px 0 rgba(0,0,0,0.05) inset;
}

/* Header layout */
.planner-left {
  font-size: 2.0rem;
  font-weight: 800;
  letter-spacing: .02em;
}
.welcome-center {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 800;
}
.header-actions {
  gap: 4px;
}

.request-btn {
  font-weight: 600;
}

.panel-card {
  background-color: #ffffff;
  border: 1px solid #002856;
  border-radius: 12px;
  position: relative;
  overflow: visible;
  padding-bottom: 16px;
}
.panel-title {
  color: #002856;
  padding: 12px 16px;
  font-weight: 700;
}

.dialog-card {
  border: 1px solid #002856;
  border-radius: 12px;
}
.dialog-title {
  color: #002856;
  padding: 10px 16px;
  font-weight: 700;
  text-align: center;
}

.table-wrap { overflow-x: auto; }

.sticky-head thead th {
  position: sticky;
  top: 0;
  background: #ffffff;
  z-index: 1;
}

.zebra tbody tr:nth-child(odd) { background: #f7fbff; }

.align-left th,
.align-left td {
  text-align: left;
}

/* vertical divider between first and second columns */
.with-divider th:first-child,
.with-divider td:first-child {
  border-right: 1px solid #c7d9ea;
}

.next-popup-table th,
.next-popup-table td {
  padding: 10px 12px;
  font-size: 14px;
}
.next-popup-table th {
  background: #eef5fb;
  font-weight: 700;
}

/* narrow first column */
.th-narrow { width: 160px; }

/* FAB button placement */
.card-fab { position: absolute; right: 12px; bottom: 12px; }
.fab-btn {
  border: 1px solid #002856;
  background-color: #ffffff;
  box-shadow: 0 2px 6px rgba(0,0,0,.08);
}

/* Info list spacing */
.info-list { padding-left: 6px; background: transparent; }
.info-item { padding-left: 0; }

/* Hover affordance */
.student-card {
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    transform 0.12s ease;
  cursor: pointer;
}
.student-card:hover {
  background-color: #D1E5F4;
  border-color: #0050a0;
  transform: translateY(-1px);
}
</style>
