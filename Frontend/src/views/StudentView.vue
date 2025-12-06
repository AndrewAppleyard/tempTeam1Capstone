<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import StudentAPI from '../apis/StudentAPI.js'
import AdvisorAPI from '../apis/AdvisorAPI.js'

const route = useRoute()
const studentid = route.params.id
console.log("THIS IS THE USER ID", studentid)
import { useUserStore } from '../store/user.js'

/* =========================================================
   THEME — same palette, more respectful visuals (centralized)
========================================================= */
const COLOR_PRIMARY = '#002856'   // deep navy
const COLOR_SURFACE = '#ffffff'   // white surface
const COLOR_ACCENT_BG = '#BDD5E7' // soft blue page background
const COLOR_PANEL_BG  = '#F3F8FD' // very light blue for info panels

/* =========================================================
   1) DEGREE PLAN SOURCE (unchanged content)
========================================================= */
interface DegreePlanCourse { term: string; code: string; title: string }

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
   2) STUDENT / ADVISOR INFO
========================================================= */
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
});

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
  { label: '9:00 PM', value: '21:00' },
]
const timeOptionValues = timeOptions.map(t => t.value)

const preferencesDialog = ref(false)
const preferenceForm = ref<SchedulePreferences>({ ...preferenceDefaults })
const preferencesLoaded = ref(false)
const loadingPreferences = ref(false)
const savingPreferences = ref(false)
const preferenceLoadError = ref('')
const preferenceSnackbar = ref(false)
const preferenceSnackbarColor = ref<'success' | 'error' | 'info'>('success')
const preferenceSnackbarMessage = ref('')

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
  availability: string
  waitlist: string
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
  waitlist: string
}

const nextDialog = ref(false)
const degreePlanTerms = computed(() =>
  Array.from(new Set(DEGREE_PLAN.map(c => c.term)))
)
const nextTerm = ref<string>('Spring Y4')

const STORAGE_KEY = 'uafs-cs-next-semester-schedule'

const nextSchedule = ref<NextCardRow[]>([])
const nextPopupRows = ref<NextPopupRow[]>([])

const selectedDegreeCourse = ref<string | null>(null)
const filteredDegreeOptions = computed(() =>
  DEGREE_PLAN
    .filter(c => c.term === nextTerm.value)
    .map(c => ({ label: `${c.code} — ${c.title}`, value: c.code }))
)

const userStore = useUserStore()

// const studentId = computed<number | null>(() => {
//   const routeId = Number(route.params.studentid)
//   if (!Number.isNaN(routeId)) return routeId
//   const storeId = userStore.userID ? Number(userStore.userID) : NaN
//   return Number.isNaN(storeId) ? null : storeId
// })
//const hasStudentId = computed(() => !!studentId.value)

function showPreferenceSnackbar(message: string, color: 'success' | 'error' | 'info' = 'success') {
  preferenceSnackbarMessage.value = message
  preferenceSnackbarColor.value = color
  preferenceSnackbar.value = true
}

function normalizeTime(value: any, fallback: string) {
  if (typeof value !== 'string') return fallback
  return timeOptionValues.includes(value) ? value : fallback
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
  if (!studentid.value) return
  loadingPreferences.value = true
  preferenceLoadError.value = ''
  try {
    const data = await StudentAPI.getStudentById(studentid.value)
    const student = data?.student

    if (student) {
      const name = [student.firstname, student.lastname].filter(Boolean).join(' ').trim()
      if (name) studentName.value = name
      preferenceForm.value = normalizePreferences(student.preferences)

      console.log("student name?:\t" + name)
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
  if (!studentid.value) {
    showPreferenceSnackbar('No student selected to save preferences.', 'error')
    return
  }
  preferencesDialog.value = true
  if (!preferencesLoaded.value && !loadingPreferences.value) {
    loadStudentProfile()
  }
}

async function savePreferences() {
  if (!studentid.value) {
    showPreferenceSnackbar('No student selected to save preferences.', 'error')
    return
  }
  savingPreferences.value = true
  try {
    const preferredHours = preferenceForm.value.preferredCreditHours
    const startValue = typeof preferenceForm.value.earliestStart === 'string' && timeOptionValues.includes(preferenceForm.value.earliestStart)
      ? preferenceForm.value.earliestStart
      : preferenceDefaults.earliestStart
    const endValue = typeof preferenceForm.value.latestEnd === 'string' && timeOptionValues.includes(preferenceForm.value.latestEnd)
      ? preferenceForm.value.latestEnd
      : preferenceDefaults.latestEnd
    const payload = {
      ...preferenceForm.value,
      preferredCreditHours: preferredHours === null || Number.isNaN(Number(preferredHours))
        ? null
        : Number(preferredHours),
      earliestStart: startValue,
      latestEnd: endValue
    }
    await StudentAPI.savePreferences(studentid.value, payload)
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
    // 🔁 Replace this with your real backend call when ready
    // Example:
    // await StudentAPI.requestProgramChange(studentid, changeRequestForm.value)
    console.log('Program change request payload:', {
      studentid,
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
    .filter(r => r.number && r.course)
    .slice(0, 6)

  while (present.length < 6) {
    present.push({
      number: '—',
      course: '—',
      time: '',
      location: '',
      professor: '',
      availability: '',
      waitlist: ''
    })
  }

  nextSchedule.value = present.map(r => ({
    number: r.number,
    name: r.course || r.number
  }))
}

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
   7) DATA LOAD (student, transcripts, advisor)
========================================================= */
onMounted(async () => {
  // --- Student + next-schedule data
  let localStorageHasSchedule = false

  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      
      if (Array.isArray(parsed.nextPopupRows) && parsed.nextPopupRows.some(r => r.number)) {
          nextPopupRows.value = parsed.nextPopupRows
          localStorageHasSchedule = true
      }
      
      if (Array.isArray(parsed.nextSchedule)) nextSchedule.value = parsed.nextSchedule
      if (typeof parsed.nextTerm === 'string') nextTerm.value = parsed.nextTerm
    }
  } catch (e) {
    console.error('Error loading local storage for next schedule:', e)
  }
  
  syncNextCardFromPopup() 
  
  if (studentid.value) loadStudentProfile() 

  try {
    const response = await StudentAPI.getStudentById(studentid)
    const userData = response.student
    console.log(response)
    console.log(userData)
    
    if (userData && userData.firstname && userData.lastname) {
      studentName.value = `${userData.firstname} ${userData.lastname}`
    } else if (userData && userData.firstname) {
      studentName.value = userData.firstname
    }

    if (!localStorageHasSchedule) { 
      let fetchedClasses: { number: string; name: string }[] = []

      console.log("CLASSES:\t" + userData.classes)
      console.log("IS ARRAY?\t" + Array.isArray(userData.classes))

      if (userData && Array.isArray(userData.classes)) {
        fetchedClasses = userData.classes.map(cls => ({ 
          number: cls.number || '—', 
          name: cls.name || '—'
        }))
        console.log("ARRAY PARSE:\t" + fetchedClasses)
      } else if (userData && typeof userData.classes === 'string') {
        try {
          const parsedClasses = JSON.parse(userData.classes)
          if (Array.isArray(parsedClasses)) {
              fetchedClasses = parsedClasses.map(cls => ({ 
                  number: cls.number || '—', 
                  name: cls.name || '—'
              }))
          }
          console.log("STRING PARSE:\t" + fetchedClasses)
        } catch (e) {
          console.error("Failed to parse student classes JSON string:", e)
        }
      }
      
      const classesForCard = fetchedClasses.slice(0, 6) 
      
      if (classesForCard.length > 0 && classesForCard.some(c => c.number !== '—')) { 
        while (classesForCard.length < 6) {
          classesForCard.push({ number: '—', name: '—' })
        }
        nextSchedule.value = classesForCard
        
        nextPopupRows.value = fetchedClasses.map(cls => ({
            number: cls.number,
            course: cls.name,
            time: 'TBA', 
            location: 'TBA',
            professor: 'TBA',
            availability: 'Open',
            waitlist: '0'
        }))
        
        while (nextPopupRows.value.length < 5) {
            nextPopupRows.value.push({ number: '', course: '', time: '', location: '', professor: '', availability: '', waitlist: '' })
        }
      }
    } 
    
  } catch (err) {
    console.error('Failed to fetch student data:', err)
  }

  // --- Transcripts -> current schedule
  try {
    const transcripts = await StudentAPI.getTranscripts(studentid)
    console.log('Transcripts Loaded for Current Schedule:', transcripts)

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

      const allCourses: TranscriptCourse[] = semesterCourses.flatMap(
        (semester: any) => semester.courses || []
      )

      const coursesForCard = allCourses.slice(-6)
      const cardCourses: CurrentRow[] = coursesForCard.map(c => ({
        number: c.code || '—',
        name: c.title || '—'
      }))

      while (cardCourses.length < 6) {
        cardCourses.push({ number: '—', name: '—' })
      }
      currentSchedule.value = cardCourses

      currentPopupRows.value = allCourses.map(c => ({
        number: c.code || '—',
        course: c.title || '—',
        time: 'N/A (Completed)',
        location: mostRecentTranscript.institution || 'N/A',
        professor: 'N/A',
        availability: 'Complete',
        waitlist: '—'
      }))

      while (currentPopupRows.value.length < 5) {
        currentPopupRows.value.push({
          number: '',
          course: '',
          time: '',
          location: '',
          professor: '',
          availability: '',
          waitlist: ''
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
    const advisorData = await AdvisorAPI.getAdvisorByStudent(studentid)
    console.log('Fetched Advisor Data:', advisorData)
    if (advisorData) {
      advisorName.value = `${advisorData.firstname} ${advisorData.lastname}`
      advisorEmail.value = advisorData.email || 'N/A'
      advisorPhone.value = advisorData.phonenumber || 'N/A'
    }
  } catch (err) {
    console.error('Failed to fetch advisor data:', err)
  }
})

watch([nextSchedule, nextPopupRows, nextTerm], () => {
  const payload = { nextSchedule: nextSchedule.value, nextPopupRows: nextPopupRows.value, nextTerm: nextTerm.value }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
}, { deep: true })

watch(studentid, (newId, oldId) => {
  if (newId && newId !== oldId) {
    preferencesLoaded.value = false
    preferenceLoadError.value = ''
    loadStudentProfile()
  }
})

/* =========================================================
   8) ACTION: DEGREE PLAN -> NEXT SCHEDULE
========================================================= */
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
  if (emptyIdx !== -1) nextPopupRows.value[emptyIdx] = newRow
  else nextPopupRows.value.push(newRow)

  syncNextCardFromPopup()
  selectedDegreeCourse.value = null
}

function removeNextRow(index: number) {
  if (index < 0 || index >= nextPopupRows.value.length) return
  nextPopupRows.value.splice(index, 1)
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

async function generateSchedule() {
  if (!studentid.value) {
    showPreferenceSnackbar('No student selected to generate a schedule.', 'error')
    return
  }
  try {
    await StudentAPI.addSchedule(studentid.value)
    showPreferenceSnackbar('Schedule generation submitted.', 'info')
  } catch (err) {
    console.error('Generate Schedule error: ', err)
    alert('Failed to generate schedule.')
  }
}

async function runHoldCheck() {
  if (!studentid.value) {
    showPreferenceSnackbar('No student selected to check advising holds.', 'error')
    return
  }
  try {
    await StudentAPI.checkAdvisingHold(studentid.value);
    showPreferenceSnackbar('Advising hold check submitted.', 'info')
  } catch (err) {
    console.error(err);
    alert("Error checking advising hold.");
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
            <v-btn :disabled="!hasStudentid" color="primary" @click="generateSchedule">
              <v-icon start>mdi-calendar-refresh</v-icon>
              Generate Schedule
            </v-btn>
            <v-btn :disabled="!hasStudentid" color="primary" variant="tonal" @click="runHoldCheck">
              <v-icon start>mdi-shield-check-outline</v-icon>
              Check Advising Hold
            </v-btn>
            <v-btn :disabled="!hasStudentid" variant="outlined" color="#002856" @click="openPreferencesDialog">
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
            <v-tooltip text="Edit next semester">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  class="fab-btn"
                  :color="COLOR_PRIMARY"
                  aria-label="Edit next semester schedule"
                  @click="nextDialog = true"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
              </template>
            </v-tooltip>
          </div>
        </v-card>
      </v-col>

      <!-- ADVISOR INFO -->
      <v-col cols="12" md="6" class="pa-3" style="text-align: left;">
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
    </v-row>

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
                <th>Availability</th>
                <th>Waitlist</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in currentPopupRows" :key="`c-pop-${i}`">
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
    <v-dialog
      v-model="nextDialog"
      width="1050"
      aria-label="Next Semester Course Schedule Dialog"
    >
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          <v-icon size="18" class="mr-2">mdi-calendar-edit</v-icon>
          Next Semester Course Schedule
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
              <v-btn
                color="primary"
                :disabled="!selectedDegreeCourse"
                @click="addNextCourseFromPlan"
              >
                <v-icon start>mdi-plus</v-icon>
                Add to schedule
              </v-btn>
            </v-col>
          </v-row>

          <v-table class="zebra align-left with-divider">
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
              <tr v-for="(row, i) in nextPopupRows" :key="`n-pop-${i}`">
                <td>{{ row.number }}</td>
                <td>{{ row.course }}</td>
                <td>{{ row.time }}</td>
                <td>{{ row.location }}</td>
                <td>{{ row.professor }}</td>
                <td>{{ row.availability }}</td>
                <td>{{ row.waitlist }}</td>
                <td>
                  <v-tooltip text="Remove row">
                    <template #activator="{ props }">
                      <v-btn
                        v-if="row.number"
                        v-bind="props"
                        icon
                        size="small"
                        variant="text"
                        color="error"
                        @click="removeNextRow(i)"
                      >
                        <v-icon>mdi-delete</v-icon>
                      </v-btn>
                    </template>
                  </v-tooltip>
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
            :disabled="savingPreferences || loadingPreferences || !hasStudentid"
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
      :timeout="3000"
    >
      {{ preferenceSnackbarMessage }}
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

    <div class="text-center mt-4" style="color:#002856;">
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
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: .02em;
}
.welcome-center {
  margin: 0;
  font-size: 1.35rem;
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
