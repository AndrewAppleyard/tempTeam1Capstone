<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import CurrentCourseAPI from '../apis/CurrentCourseAPI.js'
import StudentAPI from '../apis/StudentAPI.js'
import { useUserStore } from '../store/user.js'

/* =========================================================
   THEME (matched to Degree Planner)
========================================================= */
const COLOR_PRIMARY = '#002856'   // deep navy
const COLOR_SURFACE = '#ffffff'   // white surface
const COLOR_ACCENT_BG = '#BDD5E7' // soft blue page background
const COLOR_PANEL_BG  = '#F3F8FD' // very light blue for info panels

interface CurrentCourse {
  section: string
  courseavailability: string
  deliverymode: string
  meetingpattern: string
  courselocation: string
  instructor: string
  capacity: string
  enrolled: string
  academicperiod: string
  startdate: string
}

const courses = ref<CurrentCourse[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const termInput = ref('Spring 2026')
const searchText = ref('')
const userStore = useUserStore()

const isStudent = computed(() => userStore.userRole === 'UAFS_STUDENTS')
const studentId = computed(() =>
  userStore.userRole === 'UAFS_STUDENTS'
    ? Number(userStore.roleID)
    : null
)

const colWidths = [
  '12%',  // Section
  '8%',   // Status
  '8%',   // Delivery
  '20%',  // Meeting Pattern
  '10%',  // Location
  '12%',  // Instructor
  '7%',   // Enrolled
  '8%',   // Cap
  '8%',   // Term
  '7%'    // Start Date
]
const headerTitles = [
  'Section',
  'Status',
  'Delivery',
  'Meeting Pattern',
  'Location',
  'Instructor',
  'Enrolled',
  'Cap',
  'Term',
  'Start Date'
]

async function loadCourses() {
  loading.value = true
  error.value = null
  try {
    const data = await CurrentCourseAPI.getCurrentCourses(termInput.value)
    const list = Array.isArray(data) ? data : Array.isArray(data?.courses) ? data.courses : []
    courses.value = list
  } catch (err) {
    console.error('Failed to load current courses:', err)
    error.value = 'Unable to load current course offerings. Please try again.'
    courses.value = []
  } finally {
    loading.value = false
  }
}

const filteredCourses = computed(() => {
  const q = searchText.value.trim().toLowerCase()
  const base = !q ? courses.value : courses.value.filter(c => {
    const fields = [
      c.section,
      c.academicperiod,
      c.courseavailability,
      c.deliverymode,
      c.meetingpattern,
      c.courselocation,
      c.instructor
    ]
    return fields.some(f => (f || '').toLowerCase().includes(q))
  })
  return base
})

const summary = computed(() => ({
  total: filteredCourses.value.length,
  open: filteredCourses.value.filter(c => (c.courseavailability || '').toLowerCase() === 'open').length
}))

const sortKey = ref<string | null>(null)
const sortDir = ref<'asc' | 'desc' | null>(null)
const sortFields = [
  'section',
  'courseavailability',
  'deliverymode',
  'meetingpattern',
  'courselocation',
  'instructor',
  'enrolled',
  'capacity',
  'academicperiod',
  'startdate'
]

const sortedCourses = computed(() => {
  if (!sortKey.value || !sortDir.value) return filteredCourses.value

  const key = sortKey.value as keyof CurrentCourse
  const direction = sortDir.value === 'asc' ? 1 : -1
  const numericKeys = new Set(['capacity', 'enrolled'])

  const list = [...filteredCourses.value].sort((a, b) => {
    const av = (a[key] ?? '').toString()
    const bv = (b[key] ?? '').toString()
    if (numericKeys.has(key as string)) {
      const na = parseFloat(av) || 0
      const nb = parseFloat(bv) || 0
      if (na === nb) return 0
      return na > nb ? direction : -direction
    }
    const la = av.toLowerCase()
    const lb = bv.toLowerCase()
    if (la === lb) return 0
    return la > lb ? direction : -direction
  })

  return list
})

function toggleSort(index: number) {
  const field = sortFields[index]
  if (!field) return
  if (sortKey.value !== field) {
    sortKey.value = field
    sortDir.value = 'asc'
    return
  }
  if (sortDir.value === 'asc') {
    sortDir.value = 'desc'
    return
  }
  // was desc or null, reset
  sortKey.value = null
  sortDir.value = null
}

function sortIndicator(index: number) {
  const field = sortFields[index]
  if (sortKey.value !== field || !sortDir.value) return ''
  return sortDir.value === 'asc' ? 'mdi-menu-up' : 'mdi-menu-down'
}

const selectedSections = ref<Set<string>>(new Set())
type SavedClass = {
  number: string
  name: string
  meetingpattern?: string
  academicperiod?: string
  courseavailability?: string
  deliverymode?: string
  courselocation?: string
  instructor?: string
}

const savedClasses = ref<SavedClass[]>([])
const savingSelection = ref(false)
const saveMessage = ref('')
const saveError = ref('')
const selectionError = ref('')
const showSelectionError = ref(false)
const showSaveMessage = ref(false)
const showSaveError = ref(false)
const advisingHold = ref(false)
const showScheduleDialog = ref(false)
const dayStart = 7 * 60
const dayEnd = 22 * 60
const overlapWarning = ref(false)
const showOverlapSnackbar = ref(false)

onMounted(() => {
  loadCourses()
})

watch(studentId, id => {
  if (id) {
    loadStudentClasses()
  }
}, { immediate: true })

watch(selectionError, val => {
  showSelectionError.value = !!val
})
watch(saveMessage, val => {
  showSaveMessage.value = !!val
})
watch(saveError, val => {
  showSaveError.value = !!val
})

function baseSection(section: string | null | undefined) {
  const raw = section || ''
  const match = raw.match(/^[A-Za-z]+(?:\s*\d{3,5}-\d{3,4})/)
  if (match) return match[0].replace(/\s+/, ' ').trim()
  const beforeDash = raw.split('-')[0]
  return beforeDash.trim() || raw.trim()
}

function normalizeSection(section: string | null | undefined) {
  return baseSection(section).toLowerCase().replace(/[^a-z0-9]/gi, '')
}

function courseKey(section: string, meeting: string | null | undefined) {
  return `${normalizeSection(section)}__${meeting || ''}`
}

function normalizeMeeting(mp: string | null | undefined) {
  return (mp || '').replace(/\s+/g, ' ').trim()
}

async function loadStudentClasses() {
  if (!studentId.value) return
  try {
    const data = await StudentAPI.getStudentById(studentId.value)
    let classes = data?.student?.classes || data?.classes || []
    advisingHold.value = !!(data?.student?.advisinghold ?? data?.advisinghold)
    if (typeof classes === 'string') {
      try {
        classes = JSON.parse(classes)
      } catch (err) {
        classes = []
      }
    }
    if (Array.isArray(classes)) {
      savedClasses.value = classes.map((c: any) => ({
        number: (() => {
          const base = (c.section || c.code || '').trim()
          const title = (c.title || c.name || '').trim()
          const combined = [base, title].filter(Boolean).join(' ')
          return combined || base || title
        })(),
        name: (() => {
          const base = (c.section || c.code || '').trim()
          const title = (c.title || c.name || '').trim()
          const combined = [base, title].filter(Boolean).join(' ')
          return combined || base || title
        })(),
        meetingpattern: normalizeMeeting(c.meetingpattern || c.meeting_pattern || c.meeting || c.time),
        academicperiod: c.academicperiod || c.term || '',
        courseavailability: c.courseavailability || c.status || '',
        deliverymode: c.deliverymode || c.delivery_mode || '',
        courselocation: c.courselocation || c.location || '',
        instructor: c.instructor || ''
      }))
      syncSavedSelections()
    }
  } catch (err) {
    console.error('Failed to load student classes:', err)
  }
}

function toggleSelection(section: string, meetingpattern: string) {
  const key = courseKey(section, normalizeMeeting(meetingpattern))
  const next = new Set(selectedSections.value)
  if (next.has(key)) {
    next.delete(key)
    selectionError.value = ''
  } else {
    if (next.size >= 6) {
      selectionError.value = 'You can only select up to 6 classes.'
      showSelectionError.value = true
      return
    }
    next.add(key)
    selectionError.value = ''
  }
  selectedSections.value = next
}

function buildKeyForSaved(saved: SavedClass) {
  const normalizedMeeting = normalizeMeeting(saved.meetingpattern)
  const savedLabel = normalizeSection(saved.number || saved.name || '')
  const match = courses.value.find(c => {
    const label = normalizeSection(c.section)
    return label === savedLabel || label.includes(savedLabel) || savedLabel.includes(label)
  })
  if (match) {
    return courseKey(match.section, normalizeMeeting(match.meetingpattern))
  }
  return courseKey(savedLabel, normalizedMeeting)
}

function syncSavedSelections() {
  const next = new Set(selectedSections.value)
  savedClasses.value.forEach(sc => next.add(buildKeyForSaved(sc)))
  selectedSections.value = next
}

watch(courses, () => {
  if (savedClasses.value.length) {
    syncSavedSelections()
  }
})

function isRowSelected(section: string, meetingpattern: string) {
  const normalized = normalizeMeeting(meetingpattern)
  const key = courseKey(section, normalized)
  if (selectedSections.value.has(key)) return true
  if (selectedSections.value.has(courseKey(section, meetingpattern))) return true
  // also respect legacy selections stored without meeting pattern
  if (selectedSections.value.has(courseKey(section, ''))) return true
  // fall back: any saved entry with same section regardless of meeting pattern
  return Array.from(selectedSections.value).some(k => k.startsWith(`${section}__`))
}

function meetingDisplay(cls: SavedClass) {
  const mp = (cls.meetingpattern || '').trim()
  if (mp) return mp
  const mode = (cls.deliverymode || '').toLowerCase()
  if (mode.includes('online')) return 'Online'
  return 'N/A'
}

type Slot = {
  day: string
  startMinutes: number
  endMinutes: number
  label: string
}

const dayLabels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const timeTicks = computed(() => {
  const ticks: number[] = []
  for (let t = dayStart; t <= dayEnd; t += 60) {
    ticks.push(t)
  }
  return ticks
})
const dayAliases: Record<string, string> = {
  m: 'Monday',
  mon: 'Monday',
  monday: 'Monday',
  t: 'Tuesday',
  tu: 'Tuesday',
  tue: 'Tuesday',
  tues: 'Tuesday',
  tuesday: 'Tuesday',
  w: 'Wednesday',
  wed: 'Wednesday',
  weds: 'Wednesday',
  wednesday: 'Wednesday',
  th: 'Thursday',
  thu: 'Thursday',
  thur: 'Thursday',
  thurs: 'Thursday',
  thursday: 'Thursday',
  f: 'Friday',
  fri: 'Friday',
  friday: 'Friday',
}

function parseTimeToMinutes(timeStr: string): number | null {
  const match = timeStr.trim().match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i)
  if (!match) return null
  let hour = parseInt(match[1], 10)
  const minute = parseInt(match[2], 10)
  const meridian = match[3].toUpperCase()
  if (meridian === 'PM' && hour !== 12) hour += 12
  if (meridian === 'AM' && hour === 12) hour = 0
  return hour * 60 + minute
}

function formatTime(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  const meridian = h >= 12 ? 'PM' : 'AM'
  const hour12 = h % 12 === 0 ? 12 : h % 12
  const pad = m.toString().padStart(2, '0')
  return `${hour12}:${pad} ${meridian}`
}

function slotStyle(slot: Slot) {
  const range = dayEnd - dayStart
  const start = Math.max(dayStart, Math.min(dayEnd, slot.startMinutes))
  const end = Math.max(dayStart, Math.min(dayEnd, slot.endMinutes))
  const top = ((start - dayStart) / range) * 100
  const height = Math.max(4, ((end - start) / range) * 100)
  return {
    top: `${top}%`,
    height: `${height}%`
  }
}

function hasOverlaps() {
  const byDay = scheduleByDay.value
  for (const day of dayLabels) {
    const slots = byDay[day] || []
    for (let i = 0; i < slots.length; i++) {
      for (let j = i + 1; j < slots.length; j++) {
        const a = slots[i]
        const b = slots[j]
        if (Math.max(a.startMinutes, b.startMinutes) < Math.min(a.endMinutes, b.endMinutes)) {
          return true
        }
      }
    }
  }
  return false
}

function parseMeetingPattern(mp: string | undefined, label: string): Slot[] {
  if (!mp || !mp.trim()) return []
  if (mp.toLowerCase().includes('online')) return []
  const segments = mp.split(';').map(s => s.trim()).filter(Boolean)
  const slots: Slot[] = []

  segments.forEach(seg => {
    const parts = seg.split('|').map(p => p.trim()).filter(Boolean)
    if (parts.length < 2) return
    const daysPart = parts[0]
    const timePart = parts.slice(1).join(' ')
    const [startStr, endStr] = timePart.split('-').map(s => s.trim())
    const start = parseTimeToMinutes(startStr || '')
    const end = parseTimeToMinutes(endStr || '')
    if (start === null || end === null) return
    const rawDays = daysPart.split(/[\/,]/).map(d => d.trim().toLowerCase())
    const days = rawDays
      .map(d => dayAliases[d] || '')
      .filter(Boolean)
    days.forEach(day => {
      slots.push({ day, startMinutes: start, endMinutes: end, label })
    })
  })

  return slots
}

const scheduleByDay = computed(() => {
  const map: Record<string, Slot[]> = {
    Monday: [],
    Tuesday: [],
    Wednesday: [],
    Thursday: [],
    Friday: []
  }
  selectedCoursesList.value.forEach(cls => {
    const slots = parseMeetingPattern(cls.meetingpattern, cls.name || cls.number)
    slots.forEach(slot => {
      if (map[slot.day]) {
        map[slot.day].push(slot)
      }
    })
  })
  dayLabels.forEach(day => {
    map[day] = map[day].sort((a, b) => a.startMinutes - b.startMinutes)
  })
  return map
})

const selectedCoursesList = computed(() => {
  const map = new Map<string, SavedClass>()

  selectedSections.value.forEach(key => {
    const [section, meeting] = key.split('__')
    const course = courses.value.find(c => courseKey(c.section, normalizeMeeting(c.meetingpattern)) === key)
    if (course) {
      map.set(key, {
        number: course.section,
        name: course.section,
        meetingpattern: normalizeMeeting(course.meetingpattern),
        academicperiod: course.academicperiod,
        courseavailability: course.courseavailability,
        deliverymode: course.deliverymode,
        courselocation: course.courselocation,
        instructor: course.instructor
      })
      return
    }
    const saved = savedClasses.value.find(c => courseKey(c.number, c.meetingpattern) === key)
    if (saved) {
      map.set(key, { ...saved, name: saved.name || saved.number })
      return
    }
    map.set(key, { number: section, name: section, meetingpattern: meeting })
  })

  return Array.from(map.values())
})

watch(selectedCoursesList, () => {
  const has = hasOverlaps()
  overlapWarning.value = has
  showOverlapSnackbar.value = has
}, { deep: true, immediate: true })

async function saveSelectedCourses() {
  if (!studentId.value) {
    saveError.value = 'No student ID found.'
    showSaveError.value = true
    return
  }
  if (advisingHold.value) {
    saveError.value = 'You have an advising hold.'
    showSaveError.value = true
    return
  }
  if (hasOverlaps()) {
    saveError.value = 'You have overlapping classes. Please resolve before saving.'
    showSaveError.value = true
    return
  }
  savingSelection.value = true
  saveMessage.value = ''
  saveError.value = ''
  showSaveMessage.value = false
  showSaveError.value = false
  try {
    const payload = selectedCoursesList.value.map(c => ({
      number: c.number,
      name: c.name,
      meetingpattern: c.meetingpattern || '',
      academicperiod: c.academicperiod || '',
      courseavailability: c.courseavailability || '',
      deliverymode: c.deliverymode || '',
      courselocation: c.courselocation || '',
      instructor: c.instructor || ''
    }))
    await StudentAPI.updateStudent(studentId.value, { classes: payload })
    savedClasses.value = payload
    selectedSections.value = new Set(payload.map(c => courseKey(c.number, normalizeMeeting(c.meetingpattern))))
    await loadStudentClasses()
    saveMessage.value = 'Saved to your classes.'
    showSaveMessage.value = true
  } catch (err) {
    console.error('Failed to save classes:', err)
    saveError.value = 'Could not save selection.'
    showSaveError.value = true
  } finally {
    savingSelection.value = false
  }
}
</script>

<template>
  <!-- Shell matches Degree Planner styling -->
  
    <v-row justify="center">
      <v-col cols="12">
        <v-card
          class="panel-card catalog-card"
          :style="{ backgroundColor: COLOR_SURFACE }"
        >
          <!-- Header / Controls -->
          <v-card-title class="catalog-header">
            <v-row class="align-center" no-gutters>
              <v-col cols="12" md="6" class="text-left">
                <h2 class="catalog-title" :style="{ color: COLOR_PRIMARY }">
                  University of Arkansas – Fort Smith • Current Courses
                </h2>
              </v-col>
              <v-col
                cols="12"
                md="6"
                class="d-flex flex-wrap align-center justify-end catalog-controls"
              >
                <v-text-field
                  v-model="termInput"
                  label="Semester / term to fetch"
                  density="comfortable"
                  hide-details
                  class="mr-2 catalog-input"
                />
                <v-text-field
                  v-model="searchText"
                  label="Search (section, term, instructor, etc.)"
                  density="comfortable"
                  hide-details
                  class="mr-2 catalog-input wide"
                />
                <v-btn
                  color="primary"
                  :loading="loading"
                  class="mr-3"
                  @click="loadCourses"
                >
                  <v-icon start>mdi-refresh</v-icon>
                  Refresh
                </v-btn>
                <div class="text-caption catalog-summary" :style="{ color: COLOR_PRIMARY }">
                  Total: {{ summary.total }} • Open: {{ summary.open }}
                </div>
              </v-col>
            </v-row>
          </v-card-title>

          <v-divider />

          <v-card-text>
            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              density="comfortable"
              class="mb-3"
            >
              {{ error }}
            </v-alert>

            <v-progress-linear
              v-if="loading"
              indeterminate
              color="primary"
              class="mb-3"
            />

            <v-row v-if="!loading" dense>
              <!-- COURSE TABLE -->
              <v-col :cols="12" :md="isStudent ? 8 : 12" class="pa-2">
                <div
                  class="sticky-header-bar"
                  :style="{ gridTemplateColumns: colWidths.join(' ') }"
                >
                  <div
                    v-for="(title, i) in headerTitles"
                    :key="i"
                    class="header-cell sortable"
                    @click="toggleSort(i)"
                  >
                    <span>{{ title }}</span>
                    <v-icon
                      v-if="sortIndicator(i)"
                      size="16"
                      class="ml-1 sort-icon"
                    >
                      {{ sortIndicator(i) }}
                    </v-icon>
                  </div>
                </div>

                <div class="table-wrap">
                  <v-table
                    density="comfortable"
                    class="zebra sticky-head align-center with-divider course-table"
                    style="table-layout: fixed; width: 100%;"
                  >
                    <colgroup>
                      <col
                        v-for="(w, i) in colWidths"
                        :key="`col-${i}`"
                        :style="{ width: w }"
                      />
                    </colgroup>
                    <tbody>
                      <tr
                        v-for="(c, i) in sortedCourses"
                        :key="`${c.section}-${i}`"
                        :class="{ 'selected-row': isStudent && isRowSelected(c.section, c.meetingpattern) }"
                        @click="isStudent && toggleSelection(c.section, c.meetingpattern)"
                        :style="isStudent ? 'cursor:pointer;' : ''"
                      >
                        <td>{{ c.section }}</td>
                        <td>{{ c.courseavailability }}</td>
                        <td>{{ c.deliverymode }}</td>
                        <td class="wrap-cell">{{ c.meetingpattern }}</td>
                        <td>{{ c.courselocation }}</td>
                        <td>{{ c.instructor }}</td>
                        <td>{{ c.enrolled }}</td>
                        <td>{{ c.capacity }}</td>
                        <td>{{ c.academicperiod }}</td>
                        <td>{{ c.startdate }}</td>
                      </tr>
                      <tr v-if="!filteredCourses.length">
                        <td
                          colspan="10"
                          class="text-center py-6"
                          :style="{ color: COLOR_PRIMARY }"
                        >
                          No current courses found for this term.
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>
              </v-col>

              <!-- SELECTED CLASSES (Student only) -->
              <v-col v-if="isStudent" cols="12" md="4" class="pa-2">
                <v-card class="panel-card" :style="{ backgroundColor: COLOR_PANEL_BG }">
                  <v-card-title class="panel-title">
                    <v-icon size="20" class="mr-2">mdi-bookmark-check</v-icon>
                    Selected Classes
                  </v-card-title>
                  <v-divider />
                  <v-card-text>
                    <template v-if="selectedCoursesList.length">
                      <div class="d-flex justify-end mb-2">
                        <v-btn
                          size="small"
                          variant="outlined"
                          color="primary"
                          @click="showScheduleDialog = true"
                        >
                          <v-icon start size="18">mdi-calendar-clock</v-icon>
                          View Schedule Times
                        </v-btn>
                      </div>
                      <v-list density="compact" class="selected-list mt-2">
                        <v-list-item
                          v-for="(cls, idx) in selectedCoursesList"
                          :key="`sel-${idx}`"
                          class="selected-list-item"
                        >
                          <v-list-item-title class="selected-content">
                            <div class="selected-title">
                              {{ cls.name || cls.number }}
                            </div>
                            <div class="selected-meeting">
                              Meeting: {{ meetingDisplay(cls) }}
                            </div>
                          </v-list-item-title>
                          <template #append>
                            <v-btn
                              icon
                              size="small"
                              variant="text"
                              class="close-btn"
                              @click.stop="toggleSelection(cls.number, cls.meetingpattern || '')"
                            >
                              <v-icon size="18">mdi-close</v-icon>
                            </v-btn>
                          </template>
                        </v-list-item>
                      </v-list>
                    </template>
                    <div
                      v-else
                      class="text-caption mt-2"
                      :style="{ color: COLOR_PRIMARY }"
                    >
                      No classes selected.
                    </div>
                    <v-btn
                      block
                      class="mt-4 save-btn"
                      color="primary"
                      :loading="savingSelection"
                      :disabled="savingSelection || selectedSections.size === 0 || !studentId"
                      @click="saveSelectedCourses"
                    >
                      Save to My Classes
                    </v-btn>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Snackbars -->
    <v-snackbar
      v-if="isStudent"
      v-model="showSelectionError"
      color="error"
      location="bottom end"
      timeout="3000"
      class="selection-error-snackbar"
      elevation="6"
    >
      <span class="selection-error-text">{{ selectionError }}</span>
    </v-snackbar>

    <v-snackbar
      v-if="isStudent && overlapWarning"
      v-model="showOverlapSnackbar"
      color="warning"
      location="bottom end"
      timeout="5000"
      class="selection-error-snackbar"
      elevation="6"
    >
      <span class="selection-error-text">
        Warning: You have overlapping classes.
      </span>
    </v-snackbar>

    <v-snackbar
      v-if="isStudent"
      v-model="showSaveMessage"
      color="success"
      location="bottom end"
      timeout="3000"
      class="selection-error-snackbar"
      elevation="6"
    >
      <span class="selection-error-text">{{ saveMessage }}</span>
    </v-snackbar>

    <v-snackbar
      v-if="isStudent"
      v-model="showSaveError"
      color="error"
      location="bottom end"
      timeout="3000"
      class="selection-error-snackbar"
      elevation="6"
    >
      <span class="selection-error-text">{{ saveError }}</span>
    </v-snackbar>

    <!-- Weekly schedule dialog -->
    <v-dialog
      v-model="showScheduleDialog"
      max-width="1100"
      persistent
    >
      <v-card class="dialog-card">
        <v-card-title class="dialog-title d-flex align-center justify-space-between">
          <div>Weekly Schedule (Selected Classes)</div>
          <v-btn icon variant="text" @click="showScheduleDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-alert
            v-if="overlapWarning"
            type="warning"
            variant="tonal"
            density="comfortable"
            class="mb-2"
          >
            Warning: Some classes overlap in time.
          </v-alert>
          <div class="schedule-grid-visual">
            <div class="time-axis">
              <div class="time-axis-spacer"></div>
              <div class="time-axis-ticks">
                <div
                  v-for="tick in timeTicks"
                  :key="tick"
                  class="time-tick"
                >
                  {{ formatTime(tick) }}
                </div>
              </div>
            </div>
            <div class="day-columns">
              <div
                v-for="day in dayLabels"
                :key="day"
                class="day-column"
              >
                <div class="day-header">{{ day }}</div>
                <div class="day-track">
                  <div
                    v-for="(slot, idx) in scheduleByDay[day]"
                    :key="`${day}-${idx}`"
                    class="slot-bar"
                    :style="slotStyle(slot)"
                  >
                    <div class="slot-bar-label">{{ slot.label }}</div>
                    <div class="slot-bar-time">
                      {{ formatTime(slot.startMinutes) }} -
                      {{ formatTime(slot.endMinutes) }}
                    </div>
                  </div>
                  <div
                    v-if="!scheduleByDay[day].length"
                    class="no-slot"
                  >
                    No classes
                  </div>
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  

  <v-container fluid class="pa-2" style="background-color: transparent;">
    <div class="text-center mt-6 brand-primary" style="padding-right: 5%;">
      © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
    </div>
  </v-container>
</template>

<style scoped>
/* Match overall shell from Degree Planner */
.respectful-shell {
  box-shadow: 0 1px 0 rgba(0,0,0,0.05) inset;
}
.catalog-shell {
  margin: 0 auto;
}

/* Panel / card look */
.panel-card {
  background-color: #ffffff;
  border: 1px solid #002856;
  border-radius: 12px;
  position: relative;
  overflow: visible;
}
.catalog-card {
  min-height: 70vh;
  width: 97.5vw;
  max-width: none;
  margin-left: calc(50% - 50vw - 0.5vw) !important;
  margin-right: 0 !important;
  padding: 0 !important;
}

/* Header */
.catalog-header {
  padding: 16px 20px 8px;
}
.catalog-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
}
.catalog-controls {
  gap: 8px;
}
.catalog-input {
  max-width: 210px;
}
.catalog-input.wide {
  max-width: 280px;
}
.catalog-summary {
  white-space: nowrap;
}

/* Table and header strip */
.table-wrap {
  max-height: 70vh;
  overflow: auto;
  border: 1px solid #c7d9ea;
  border-radius: 8px;
  background: #ffffff;
  scrollbar-gutter: stable;
}

.sticky-head thead th {
  position: sticky;
  top: 0;
  background: #ffffff;
  z-index: 1;
}

.zebra tbody tr:nth-child(odd) { background: #f7fbff; }

.align-center th {
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.align-center td {
  text-align: center;
  vertical-align: middle;
  white-space: normal;
  word-break: break-word;
}

/* vertical divider between first and second columns */
.with-divider th:first-child,
.with-divider td:first-child {
  border-right: 1px solid #c7d9ea;
}

/* Custom sticky header bar for sortable columns */
.sticky-header-bar {
  position: sticky;
  top: 0;
  z-index: 2;
  display: grid;
  align-items: center;
  justify-items: center;
  gap: 0;
  border: 1px solid #c7d9ea;
  border-radius: 8px;
  background: #e9f2fb;
  padding: 8px;
  box-sizing: border-box;
  margin-bottom: 6px;
}
.header-cell {
  font-weight: 700;
  color: #002856;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 6px 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  user-select: none;
}

.course-table td,
.course-table th {
  border-right: 1px solid #c7d9ea;
}

/* Remove the last column border so it doesn’t double up on the table edge */
.course-table td:last-child,
.course-table th:last-child {
  border-right: none;
}
/* Selected row styling */
.selected-row {
  background-color: #81b1ff !important;
  box-shadow: inset 0 0 0 2px #004492; /* replaces outline */
}

.selected-row th,
.selected-row td {
  background-color: #81b1ff !important; /* inherit row background */
}


/* Selected list (right-hand card) */
.selected-list {
  padding-top: 0;
}
.selected-list-item {
  border: 1px solid #002856;
  background: #e9f2fb;
  border-radius: 16px !important;
  margin-bottom: 8px;
  padding: 10px 14px;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
}
.selected-list-item :deep(.v-list-item__content) {
  padding: 0;
  margin: 0;
  display: block;
  width: 100%;
}
.selected-list-item :deep(.v-list-item__append) {
  position: static;
  width: auto;
  padding: 0;
  margin-left: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.selected-content {
  padding-right: 8px;
  text-align: left;
  flex: 1;
  min-width: 0;
}
.selected-title {
  font-weight: 700;
  color: #002856;
  margin: 0;
  word-break: break-word;
  white-space: normal;
}
.selected-meeting {
  color: #002856;
  font-size: 12px;
  margin: 4px 0 0 0;
  text-align: left;
}
.close-btn {
  color: #002856 !important;
  background: transparent !important;
  border: none !important;
  margin-left: 8px;
  position: relative;
  z-index: 2;
}
.close-btn:hover {
  background: #d5e6f7 !important;
  border: 1px solid #002856 !important;
  color: #002856 !important;
  z-index: 4;
}
.save-btn {
  background: linear-gradient(90deg, #003c81, #005bb5);
  color: #ffffff !important;
  border-radius: 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.save-btn:hover {
  filter: brightness(1.05);
}

/* Snackbars */
.selection-error-snackbar {
  min-width: 260px;
}
.selection-error-text {
  font-size: 12px;
  font-weight: 600;
}

/* Schedule dialog */
.dialog-card {
  border: 1px solid #002856;
  border-radius: 12px;
}
.dialog-title {
  color: #002856;
  padding: 10px 16px;
  font-weight: 700;
}

.schedule-grid-visual {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 12px;
  margin-top: 8px;
}
.time-axis {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 12px;
  color: #002856;
  border-right: 1px solid #c7d9ea;
}
.time-axis-spacer {
  height: 32px;
}
.time-axis-ticks {
  flex: 1;
  height: 720px;
  padding: 8px 4px 8px 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
}
.time-tick {
  transform: translateY(-6px);
}
.day-columns {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}
.day-column {
  display: flex;
  flex-direction: column;
}
.day-header {
  text-align: center;
  font-weight: 700;
  color: #002856;
  margin-bottom: 6px;
}
.day-track {
  position: relative;
  height: 720px;
  border: 1px solid #c7d9ea;
  border-radius: 10px;
  background: linear-gradient(to bottom, #f7fbff 0%, #ffffff 100%);
  overflow: hidden;
}
.day-track::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background-image:
    linear-gradient(to bottom, rgba(0,0,0,0.08) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0,0,0,0.04) 1px, transparent 1px),
    linear-gradient(to right, rgba(0,0,0,0.04) 1px, transparent 1px);
  background-size: 100% 60px, 100% 30px, 20px 100%;
  pointer-events: none;
}
.slot-bar {
  position: absolute;
  left: 8px;
  right: 8px;
  background: rgba(0, 60, 129, 0.12);
  border: 1px solid #003c81;
  border-radius: 8px;
  padding: 6px 8px;
  color: #002856;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: visible;
  word-break: break-word;
  min-height: 64px;
  height: auto;
}
.slot-bar-label {
  font-weight: 700;
  font-size: 11.5px;
  line-height: 1.15;
  white-space: normal;
}
.slot-bar-time {
  font-size: 10.5px;
  white-space: normal;
  word-break: break-word;
}
.no-slot {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #7a8da6;
  font-size: 12px;
}

.wrap-cell {
  white-space: normal !important;
  overflow-wrap: break-word;
  word-break: break-word;
}
</style>
