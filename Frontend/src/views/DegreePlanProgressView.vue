<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import DegreePlanAPI from '../apis/DegreePlanAPI.js'
import StudentAPI from '../apis/StudentAPI.js'
import { useUserStore } from '../store/user.js'


type Semester = 'Fall' | 'Spring'
type RowType = 'Major' | 'Minor' | 'Gen Ed' | 'Concentration/Elective' | 'Other'

interface CatalogCourse {
  id: string
  code: string
  title: string
  credits: number
  type: RowType
  prereqs: string[]
  coreqs: string[]
  description: string
  termLabel: string 
}

interface TranscriptCourse {
  code: string
  title: string
  grade: string
  credits: number
  term: string
  status: 'Completed' | 'In Progress'
}

interface ProgressCourse extends CatalogCourse {
  status: 'Complete' | 'In Progress' | 'Required'
  completedGrade?: string
  completedTerm?: string
  metBy?: string 
}

// --- Component Setup ---

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
const loading = ref(true)

const catalogCourses = ref<CatalogCourse[]>([])
const transcriptCourses = ref<TranscriptCourse[]>([])
const currentCourses = ref<any[]>([])
const progressCourses = ref<ProgressCourse[]>([])
const termOrder = ref<string[]>([])
const expandedPanels = ref<string[]>([])
const studentMinor = ref<string | null>(null)

function extractCourseCodeAndTitle(obj: any) {
  const raw = (obj?.code || obj?.course || obj?.section || obj?.number || obj?.name || '').toString().trim()
  const [codePart, titlePart] = raw.split(' - ', 2)
  const code = normalizeCourseCode(codePart || raw)
  const title = titlePart || obj?.title || raw
  return { code, title }
}

function isPlaceholderText(text: string) {
  const upper = text.toUpperCase()
  return /TBD|REQUIREMENT|ELECTIVE|LAB|FA\/HUM|HUMANITIES|SOCSCI|SCIENCE/.test(upper)
}

function deriveMajorPrefix(catalogs: CatalogCourse[]) {
  const counts: Record<string, number> = {}
  catalogs.forEach(c => {
    const norm = normalizeCourseCode(c.code)
    if (!norm) return
    if (isPlaceholderText(`${c.code} ${c.title}`)) return
    const prefix = (norm.match(/^([A-Z]+)/)?.[1] || '').toUpperCase()
    if (prefix) counts[prefix] = (counts[prefix] || 0) + 1
  })
  if (counts['CS']) return 'CS'
  if (counts['CSCE']) return 'CSCE'
  if (Object.keys(counts).length === 0 && catalogs.length) {
    const firstCode = normalizeCourseCode(catalogs.find(c => normalizeCourseCode(c.code))?.code || '')
    return (firstCode.match(/^([A-Z]+)/)?.[1] || 'CS').toUpperCase()
  }
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'CS'
}

function computeCourseType(course: ProgressCourse | TranscriptCourse | any, majorPrefix: string, catalogSet: Set<string>): RowType {
  const prefix = (course.code?.match?.(/^([A-Z]+)/)?.[1] || '').toUpperCase()
  const text = `${course.code || ''} ${course.title || ''}`.toUpperCase()
  const placeholder = isPlaceholderText(text)
  const placeholderConcentration = /CONCENTRATION|ELECTIVE|CS\/MATH\/STAT|UPPER-LEVEL|LOWER-LEVEL/.test(text)
  const catalogType = (course.type || '').toString().toUpperCase()
  const alliedMajorPrefixes = new Set<string>(['CS', 'MATH', 'STAT', 'STEM'])

  const inCatalog = catalogSet.has(normalizeCourseCode(course.code || ''))

  if (course.type === 'Minor') {
    return studentMinor.value ? 'Minor' : 'Other'
  }

  // If marked as concentration but not in catalog and not major/allied, treat as Gen Ed.
  if (catalogType === 'CONCENTRATION/ELECTIVE' && !inCatalog && !(prefix === majorPrefix || alliedMajorPrefixes.has(prefix))) {
    return 'Gen Ed'
  }

  if (inCatalog) {
    if (prefix === majorPrefix || alliedMajorPrefixes.has(prefix)) {
      return catalogType === 'CONCENTRATION/ELECTIVE' ? 'Concentration/Elective' : 'Major'
    }
    // Non-major catalog entries default to Gen Ed regardless of placeholder text.
    return 'Gen Ed'
  }

  // Major/allied prefix but not in catalog -> treat as Concentration/Elective
  if (prefix && (prefix === majorPrefix || alliedMajorPrefixes.has(prefix))) {
    return 'Concentration/Elective'
  }

  // Placeholder cues
  if (placeholderConcentration) return 'Concentration/Elective'
  if (placeholder) return 'Gen Ed'
  if (course.type === 'Gen Ed') return 'Gen Ed'
  if (course.type === 'Concentration/Elective') return 'Concentration/Elective'

  // Default non-major to Gen Ed; avoid Other unless truly unknown
  return prefix && prefix !== majorPrefix ? 'Gen Ed' : 'Other'
}

function matchScoreForPlaceholder(placeholderText: string, candidatePrefix: string, candidateTitle: string, candidateCode = '') {
  const text = placeholderText.toUpperCase()
  const prefix = candidatePrefix.toUpperCase()
  const title = candidateTitle.toUpperCase()
  const numMatch = candidateCode.match(/\d{3,4}/)
  const num = numMatch ? parseInt(numMatch[0], 10) : null

  const isSocial = /SOCIAL|HUMAN|HUMANITIES|ART|FINE ARTS/.test(text)
  const isLabReq = /LAB SCIENCE REQUIREMENT|SCIENCE REQUIREMENT|LAB SCIENCE/.test(text)
  const isHistGovReq = /HISTORY\/GOVERNMENT|HISTORY REQUIREMENT|GOVERNMENT REQUIREMENT|HISTORY\/GOVERNMENT/.test(text)
  const isConcentrationReq = /CONCENTRATION REQUIREMENT|CS\/MATH\/STAT/.test(text)
  const isLowerLevel = /LOWER[-\\s]?LEVEL|1000-2000/.test(text)
  const scienceCue = (/SCIENCE|PHYS|CHEM|BIO|BIOLOGY|PHYSICS/.test(text) || /LAB/.test(text)) && !isSocial

  if (isConcentrationReq && !(prefix.startsWith('CS') || prefix.startsWith('MATH') || prefix.startsWith('STAT'))) {
    return 0
  }
  if (isHistGovReq && !(prefix.startsWith('HIST') || prefix.startsWith('POLS') || title.includes('HISTORY') || title.includes('GOV'))) {
    return 0
  }

  if (isHistGovReq && (prefix.startsWith('HIST') || title.includes('HISTORY') || title.includes('GOV') || prefix.startsWith('POLS'))) {
    return 10
  }
  if (isLabReq && (prefix.startsWith('PHYS') || title.includes('PHYS') || title.includes('SCIENCE') || title.includes('LAB') || prefix.startsWith('CHEM') || prefix.startsWith('BIO'))) {
    return 10
  }
  if (isLowerLevel && prefix.startsWith('CS') && num !== null && num < 2000) {
    return 9
  }
  if (scienceCue && (prefix.startsWith('PHYS') || title.includes('PHYS') || title.includes('SCIENCE') || title.includes('LAB') || prefix.startsWith('CHEM') || prefix.startsWith('BIO'))) {
    return 8
  }
  if (isSocial && (prefix.startsWith('HIST') || prefix.startsWith('POLS') || prefix.startsWith('COMM') || prefix.startsWith('ENGL') || prefix.startsWith('ART') || prefix.startsWith('MUS') || prefix.startsWith('FA') || prefix.startsWith('HUM') || prefix.startsWith('SOC'))) {
    return 6
  }
  if (/MATH|STAT/.test(text) && (prefix.startsWith('MATH') || prefix.startsWith('STAT'))) {
    return 5
  }
  if (/CONCENTRATION|ELECTIVE|CS\/MATH\/STAT|UPPER-LEVEL|LOWER-LEVEL/.test(text) && (prefix.startsWith('CS') || prefix.startsWith('MATH') || prefix.startsWith('STAT'))) {
    return 4
  }
  if (/ENGL|COMM|HUM|SOC/.test(prefix) || /ENGLISH|COMMUNICATION/.test(title)) {
    return 3
  }
  if (isSocial && (prefix.startsWith('PHYS') || prefix.startsWith('CHEM') || prefix.startsWith('BIO'))) {
    return 0
  }
  return 1
}

const PASSING_GRADES = ['A', 'A+', 'A-', 'B', 'B+', 'B-', 'C', 'C+', 'C-', 'D', 'D+', 'D-'] 

function isPassingGrade(grade?: string) {
  if (!grade) return false
  const g = grade.toUpperCase().trim()
  return /^[ABCD][+-]?$/.test(g)
}

function normalizeCourseCode(raw: string | null | undefined) {
  if (!raw) return ''
  const upper = raw.toUpperCase().trim()
  if (!upper) return ''

  // Drop anything after a space like modality labels
  const base = upper.split('|')[0].split('(')[0].trim()
  const beforeDash = base.split('-')[0].trim()
  const compact = beforeDash.replace(/\s+/g, '')

  const match = compact.match(/^([A-Z]+)(\d{3,6})/)
  if (!match) return beforeDash

  let letters = match[1]
  if (letters.startsWith('CS') && letters !== 'CS') {
    letters = 'CS'
  }
  const digitsRaw = match[2]
  let digits = digitsRaw
  if (digitsRaw.length === 5 && digitsRaw[3] === '0') {
    digits = `${digitsRaw.slice(0, 3)}${digitsRaw.slice(4)}`
  } else if (digitsRaw.length > 4) {
    digits = digitsRaw.slice(0, 4)
  }
  return `${letters} ${digits}`
}

function parseTranscriptCourses(raw: any): TranscriptCourse[] {
  if (!raw) return []

  const list = Array.isArray(raw) ? raw : []
  if (!list.length) return []

  const coursemap = list[0]?.coursemap
  const flattened: TranscriptCourse[] = []

  const pushCourse = (c: any, termLabel?: string) => {
    const codeRaw = (c.code || c.courseCode || c.course || c.section || '').toString().trim()
    const code = normalizeCourseCode(codeRaw)
    if (!code) return
    const title = (c.title || c.name || code).toString()
    const grade = (c.grade || c.finalGrade || '').toString()
    const credits = Number(c.credits ?? c.hours ?? c.creditHours ?? 0) || 0
    const term = termLabel || (c.term || c.semester || c.academic_period || '').toString()
    const statusRaw = (c.status || '').toString()
    let status: TranscriptCourse['status'] = 'Completed'
    if (statusRaw) {
      status = statusRaw === 'In Progress' ? 'In Progress' : 'Completed'
    } else if (!grade) {
      status = 'In Progress'
    }
    flattened.push({ code, title, grade, credits, term, status })
  }

  const ingestArray = (arr: any[]) => {
    arr.forEach(entry => {
      if (entry && Array.isArray(entry.courses)) {
        const termLabel = [entry.semester, entry.year].filter(Boolean).join(' ')
        entry.courses.forEach((c: any) => pushCourse(c, termLabel))
      } else {
        pushCourse(entry)
      }
    })
  }

  if (Array.isArray(coursemap)) {
    ingestArray(coursemap)
  } else if (typeof coursemap === 'string') {
    try {
      const parsed = JSON.parse(coursemap)
      if (Array.isArray(parsed)) ingestArray(parsed)
    } catch (_) { /* ignore parse errors */ }
  } else if (coursemap && typeof coursemap === 'object') {
    ingestArray(Object.values(coursemap))
  }

  return flattened
}

/*======== DATA PULL & MERGE =========*/
onMounted(async () => {
  loading.value = true
  try {
    if (!hasStudentId.value) {
      console.warn("No student ID found")
      return
    }

    const studentData = await StudentAPI.getStudentById(studentId.value)
    major.value = studentData.student.major
    studentMinor.value = studentData.student.minor || null
    currentCourses.value = Array.isArray(studentData.student.classes) ? studentData.student.classes : []
    if (!major.value) {
      console.warn('No major found, cannot load degree plan.')
      return
    }

    const resPlan = await DegreePlanAPI.view_degree_plans_by_degree(major.value)
    const degree = resPlan.data
    const rows: CatalogCourse[] = []
    const termSeen: string[] = []
    
    Object.entries(degree.corecourses || {}).forEach(([termLabel, courses]) => {
      const safeTermLabel = termLabel ? String(termLabel) : "";
      const cleanedTermLabel = safeTermLabel.replace(/^(st|nd|rd|th)/i, '').trim();
      if (cleanedTermLabel && !termSeen.includes(cleanedTermLabel)) {
        termSeen.push(cleanedTermLabel)
      }

      (courses as any[]).forEach((c, index) => {
        rows.push({
          id: `${cleanedTermLabel}-${index}-${c.code}`,
          code: c.code || "TBD",
          title: c.title || "Untitled Course",
          credits: c.hours ?? 0,
          type: c.type || "Other", 
          prereqs: c.prereqs || [],
          coreqs: c.coreqs || [],
          description: c.description || "",
          termLabel: cleanedTermLabel, 
        })
      })
    })
    catalogCourses.value = rows
    termOrder.value = termSeen

    const resTranscript = await StudentAPI.getTranscripts(studentId.value)
    const transcriptPayload = resTranscript?.data ?? resTranscript
    transcriptCourses.value = parseTranscriptCourses(transcriptPayload)

    mergeData()

  } catch (err) {
    console.error("Failed to load progress data", err)
  } finally {
    loading.value = false
  }
})


function mergeData() {
  const merged: ProgressCourse[] = []
  const normalizeCode = (code: string | undefined | null) => normalizeCourseCode(code || '')
  const catalogRequired = new Set<string>()
  catalogCourses.value.forEach(c => {
    const key = normalizeCode(c.code)
    if (key && !isPlaceholderText(`${c.code} ${c.title}`)) {
      catalogRequired.add(key)
    }
  })

  const transcriptMap = new Map<string, TranscriptCourse>()
  transcriptCourses.value.forEach(t => {
      const courseKey = normalizeCode(t.code)
      const existing = transcriptMap.get(courseKey)
      
      const isPassing = t.grade && isPassingGrade(t.grade)

      if (isPassing) {
          transcriptMap.set(courseKey, t) 
      } else if (!existing || existing.status !== 'Completed') {
          transcriptMap.set(courseKey, t) 
      }
  })

  const currentMap = new Map<string, any>()
  currentCourses.value.forEach(c => {
    const { code, title } = extractCourseCodeAndTitle(c)
    if (!code) return
    currentMap.set(code, { ...c, code, title })
  })

  const matchedTranscriptCodes = new Set<string>()
  const matchedCurrentCodes = new Set<string>()
  const majorPrefix = deriveMajorPrefix(catalogCourses.value)

  catalogCourses.value.forEach(catalog => {
    const progress: ProgressCourse = { ...catalog, status: 'Required' }
    progress.type = computeCourseType(progress, majorPrefix, catalogRequired)
    const courseCode = normalizeCode(catalog.code)
    const trans = transcriptMap.get(courseCode)
    const current = currentMap.get(courseCode)

    if (trans) {
        if (trans.status === 'Completed' && trans.grade && isPassingGrade(trans.grade)) {
            progress.status = 'Complete'
            progress.completedGrade = trans.grade
            progress.completedTerm = trans.term
        } else if (trans.status === 'In Progress') {
            progress.status = 'In Progress'
            progress.completedTerm = trans.term
        }
        progress.type = computeCourseType(progress, majorPrefix, catalogRequired)
        matchedTranscriptCodes.add(courseCode)
        // track nonmatched courses (electives/transfer)
        // transcriptMap.delete(courseCode) 
    } 
    
    if (!trans && current) {
      progress.status = 'In Progress'
      progress.title = current.title || progress.title
      progress.completedTerm = current.academic_period || 'Current'
      const creditVal = Number(current.credits ?? current.hours ?? current.creditHours ?? 0)
      if (creditVal > 0) {
        progress.credits = creditVal
      }
      progress.type = computeCourseType(progress, majorPrefix, catalogRequired)
      matchedCurrentCodes.add(courseCode)
    }

    // Force catalog-required codes to remain Major.
    if (catalogRequired.has(courseCode)) {
      progress.type = 'Major'
    }

    merged.push(progress)
  })
  
  // Attempt to map unmet transcript/current courses into elective/requirement placeholders.
  const remainingTranscript: TranscriptCourse[] = []
  transcriptMap.forEach((t, code) => {
    if (matchedTranscriptCodes.has(code)) return
    remainingTranscript.push(t)
  })

  const remainingCurrent: any[] = []
  currentMap.forEach((c, code) => {
    if (matchedCurrentCodes.has(code)) return
    remainingCurrent.push(c)
  })

  merged.forEach(course => {
    if (!isPlaceholderText(`${course.code} ${course.title}`) || course.status !== 'Required') return

    let replacement: TranscriptCourse | any | null = null
    let fromCurrent = false

    const placeholderText = `${course.code} ${course.title}`

    const takeFromList = (list: any[], predicate: (c: any) => boolean) => {
      const idx = list.findIndex(predicate)
      if (idx >= 0) {
        const item = list[idx]
        list.splice(idx, 1)
        return item
      }
      return null
    }

    // Deterministic matching for common buckets
    const isHistGovReq = /HISTORY\/GOVERNMENT|HISTORY REQUIREMENT|GOVERNMENT REQUIREMENT|HISTORY\/GOVERNMENT/.test(placeholderText.toUpperCase())
    const isLabReq = /LAB SCIENCE REQUIREMENT|SCIENCE REQUIREMENT|LAB SCIENCE/.test(placeholderText.toUpperCase())

    if (isHistGovReq) {
      replacement = takeFromList(remainingTranscript, c => {
        const p = (c.code?.match?.(/^([A-Z]+)/)?.[1] || '').toUpperCase()
        const t = (c.title || '').toUpperCase()
        return p.startsWith('HIST') || p.startsWith('POLS') || t.includes('HISTORY') || t.includes('GOV')
      })
      if (!replacement) {
        replacement = takeFromList(remainingCurrent, c => {
          const p = (c.code?.match?.(/^([A-Z]+)/)?.[1] || '').toUpperCase()
          const t = (c.title || '').toUpperCase()
          return p.startsWith('HIST') || p.startsWith('POLS') || t.includes('HISTORY') || t.includes('GOV')
        })
        fromCurrent = !!replacement
      }
    } else if (isLabReq) {
      replacement = takeFromList(remainingTranscript, c => {
        const p = (c.code?.match?.(/^([A-Z]+)/)?.[1] || '').toUpperCase()
        const t = (c.title || '').toUpperCase()
        return p.startsWith('PHYS') || p.startsWith('CHEM') || p.startsWith('BIO') || t.includes('PHYS') || t.includes('SCIENCE') || t.includes('LAB')
      })
      if (!replacement) {
        replacement = takeFromList(remainingCurrent, c => {
          const p = (c.code?.match?.(/^([A-Z]+)/)?.[1] || '').toUpperCase()
          const t = (c.title || '').toUpperCase()
          return p.startsWith('PHYS') || p.startsWith('CHEM') || p.startsWith('BIO') || t.includes('PHYS') || t.includes('SCIENCE') || t.includes('LAB')
        })
        fromCurrent = !!replacement
      }
    }

    if (!replacement && remainingTranscript.length) {
      const scored = remainingTranscript
        .map((c, idx) => {
          const prefix = (c.code?.match?.(/^([A-Z]+)/)?.[1] || '').toUpperCase()
          return { idx, score: matchScoreForPlaceholder(placeholderText, prefix, c.title || '', c.code || ''), course: c }
        })
        .sort((a, b) => b.score - a.score)
      const best = scored[0]
      if (best && best.score >= 2) {
        replacement = best.course
        remainingTranscript.splice(best.idx, 1)
      }
    }

    if (!replacement && remainingCurrent.length) {
      const scored = remainingCurrent
        .map((c, idx) => {
          const prefix = (c.code?.match?.(/^([A-Z]+)/)?.[1] || '').toUpperCase()
          return { idx, score: matchScoreForPlaceholder(placeholderText, prefix, c.title || '', c.code || ''), course: c }
        })
        .sort((a, b) => b.score - a.score)
      const best = scored[0]
      if (best && best.score >= 2) {
        replacement = best.course
        remainingCurrent.splice(best.idx, 1)
        fromCurrent = true
      }
    }

    if (replacement) {
      const repCode = normalizeCode(replacement.code || replacement.course || replacement.section)
      const repTitle = replacement.title || course.title
      course.code = repCode || course.code
      course.title = repTitle
      course.credits = Number(replacement.credits ?? replacement.hours ?? replacement.creditHours ?? course.credits) || course.credits
      course.status = fromCurrent ? 'In Progress' : 'Complete'
      course.completedGrade = fromCurrent ? undefined : replacement.grade
      course.completedTerm = fromCurrent ? (replacement.academic_period || 'Current') : (replacement.term || course.completedTerm)
      course.type = computeCourseType(course, majorPrefix, catalogRequired)
      if (repCode && catalogRequired.has(repCode)) {
        course.type = 'Major'
      }
    }
  })

  // Add any remaining unmatched transcript/current courses as "Other"
  remainingTranscript.forEach(trans => {
    const status = (trans.status === 'Completed' && trans.grade && isPassingGrade(trans.grade))
      ? 'Complete'
      : trans.status === 'In Progress'
        ? 'In Progress'
        : 'Required'

    merged.push({
      id: `extra-${trans.code}`,
      code: trans.code,
      title: trans.title || trans.code,
      credits: trans.credits || 0,
      type: computeCourseType({ code: trans.code, title: trans.title, type: 'Gen Ed' }, majorPrefix, catalogRequired),
      prereqs: [],
      coreqs: [],
      description: 'Added from transcript (not in degree plan).',
      termLabel: trans.term || 'UNSCHEDULED',
      status,
      completedGrade: trans.grade,
      completedTerm: trans.term
    })
  })

  remainingCurrent.forEach(plan => {
    merged.push({
      id: `current-${plan.code}`,
      code: plan.code || 'TBD',
      title: plan.title || plan.code || 'Current Course',
      credits: Number(plan.credits ?? plan.hours ?? plan.creditHours ?? 0) || 0,
      type: computeCourseType({ code: plan.code, title: plan.title, type: 'Major' }, majorPrefix, catalogRequired),
      prereqs: [],
      coreqs: [],
      description: 'Current course (not matched to degree plan).',
      termLabel: plan.academic_period || 'CURRENT',
      status: 'In Progress',
      completedTerm: plan.academic_period || 'Current'
    })
  })

  // Final pass: any course whose normalized code is explicitly in the degree plan catalog should be Major.
  merged.forEach(c => {
    const norm = normalizeCode(c.code)
    if (catalogRequired.has(norm) || norm === 'CS 1093') {
      c.type = 'Major'
    }
  })

  progressCourses.value = merged
}


/* ======== FILTERING & DISPLAY LOGIC (Inherited from DegreePlan) ======== */
const typeOptions: RowType[] = ['Major', 'Minor', 'Gen Ed', 'Concentration/Elective', 'Other']
type TypeOption = 'All' | RowType

const statusOptions = ['All', 'Complete', 'In Progress', 'Required'] as const
type StatusOption = typeof statusOptions[number]

function chipColor(type: RowType, status?: string): string {
  if (status === 'Complete') return 'success' 
  if (status === 'In Progress') return 'warning' 
  
  switch (type) {
    case 'Major': return '#002856'
    case 'Minor': return 'indigo-darken-1'
    case 'Gen Ed': return 'teal-darken-1'
    case 'Concentration/Elective': return 'purple-darken-1'
    case 'Other': return 'grey'
    default: return 'grey'
  }
}

function statusStyle(status: string) {
  switch (status) {
    case 'Complete': 
      return { icon: 'mdi-check-circle', color: 'success' }
    case 'In Progress': 
      return { icon: 'mdi-progress-alert', color: 'warning' }
    case 'Required': 
    default:
      return { icon: 'mdi-minus-circle', color: 'error' }
  }
}

/* ======== DERIVED DATA ======== */

interface ProgressTermGroup {
    termLabel: string;
    courses: ProgressCourse[];
    status: 'Completed' | 'In Progress' | 'Required' | 'Unscheduled';
}

const groupedProgress = computed(() => {
    const groups: Record<string, ProgressCourse[]> = {}
    
    progressCourses.value.forEach(course => {
        const term = course.termLabel || 'UNSCHEDULED'
        if (!groups[term]) {
            groups[term] = []
        }
        groups[term].push(course)
    })

    const termGroups: ProgressTermGroup[] = Object.keys(groups).map(termLabel => {
        const courses = groups[termLabel]
        let status: ProgressTermGroup['status'] = 'Completed'

        if (termLabel.toUpperCase() === 'UNSCHEDULED') {
            status = 'Unscheduled'
        } else if (courses.some(c => c.status === 'In Progress')) {
            status = 'In Progress'
        } else if (courses.some(c => c.status === 'Required')) {
            status = 'Required'
        }
        
        return {
            termLabel,
            courses: courses.sort((a, b) => a.code.localeCompare(b.code)),
            status,
        }
    })

    const standingBuckets = [
        ['FRESHMAN', 'FROSH', 'FIRST YEAR', 'FR', 'FR.'],
        ['SOPHOMORE', 'SOPH', 'SOPHMORE', 'SOPHM', 'SECOND YEAR', 'SO', 'SO.'],
        ['JUNIOR', 'JR', 'JR.'],
        ['SENIOR', 'SR', 'SR.']
    ]
    const baseTermOrder = [
        'FRESHMAN FALL', 'FRESHMAN SPRING',
        'SOPHOMORE FALL', 'SOPHOMORE SPRING',
        'JUNIOR FALL', 'JUNIOR SPRING',
        'SENIOR FALL', 'SENIOR SPRING'
    ]
    const seasonOrder = ['FALL', 'SPRING', 'SUMMER']

    const rankTerm = (label: string) => {
        const base = label.replace(/\d{4}/g, '').trim()
        const upperBase = base.toUpperCase().replace(/\s+/g, ' ')
        const baseIdx = baseTermOrder.indexOf(upperBase)
        if (baseIdx >= 0) return { idx: baseIdx, fallback: baseIdx }

        let standingIdx = -1
        standingBuckets.some((bucket, idx) => {
            if (bucket.some(key => upperBase.includes(key))) {
                standingIdx = idx
                return true
            }
            return false
        })
        const seasonIdx = seasonOrder.findIndex(s => upperBase.includes(s))
        const yearMatch = label.match(/(\d{4})/)
        const year = yearMatch ? parseInt(yearMatch[1]) : 0
        const key = (standingIdx >= 0 ? standingIdx : 99) * 100000 +
                    year * 10 +
                    (seasonIdx >= 0 ? seasonIdx : 9)
        return { idx: Number.MAX_SAFE_INTEGER, fallback: key }
    }

    termGroups.sort((a, b) => {
        const aRank = rankTerm(a.termLabel)
        const bRank = rankTerm(b.termLabel)
        if (aRank.idx !== bRank.idx) return aRank.idx - bRank.idx
        if (aRank.fallback !== bRank.fallback) return aRank.fallback - bRank.fallback
        // push unscheduled last
        if (a.termLabel === 'UNSCHEDULED') return 1
        if (b.termLabel === 'UNSCHEDULED') return -1
        return a.termLabel.localeCompare(b.termLabel)
    })

    return termGroups
})


// Progress Summary Computations
const progressSummary = computed(() => {
  const total = progressCourses.value.length
  const complete = progressCourses.value.filter(c => c.status === 'Complete').length
  const required = progressCourses.value.filter(c => c.status === 'Required').length
  const inProgress = progressCourses.value.filter(c => c.status === 'In Progress').length

  const completeCredits = progressCourses.value
    .filter(c => c.status === 'Complete')
    .reduce((acc, c) => acc + c.credits, 0)
  
  const inProgressCredits = progressCourses.value
    .filter(c => c.status === 'In Progress')
    .reduce((acc, c) => acc + c.credits, 0)
  
  const totalCredits = progressCourses.value.reduce((acc, c) => acc + c.credits, 0)
  
  const overallPercent = total > 0 ? (complete / total) * 100 : 0
  const bucketed: Record<RowType, ProgressCourse[]> = {
    'Major': [],
    'Minor': [],
    'Gen Ed': [],
    'Concentration/Elective': [],
    'Other': []
  }

  progressCourses.value.forEach(c => {
    const bucket = (c.type as RowType) || 'Other'
    bucketed[bucket].push(c)
  })

  const categories = typeOptions.map(type => {
    const typeCourses = bucketed[type]
    const typeTotal = typeCourses.length
    const typeComplete = typeCourses.filter(c => c.status === 'Complete').length
    const typeCreditsTotal = typeCourses.reduce((acc, c) => acc + c.credits, 0)
    const typeCreditsComplete = typeCourses.filter(c => c.status === 'Complete').reduce((acc, c) => acc + c.credits, 0)
    
    return {
      type,
      total: typeTotal,
      complete: typeComplete,
      percent: typeTotal > 0 ? (typeComplete / typeTotal) * 100 : 0,
      creditsTotal: typeCreditsTotal,
      creditsComplete: typeCreditsComplete,
      creditsPercent: typeCreditsTotal > 0 ? (typeCreditsComplete / typeCreditsTotal) * 100 : 0,
    }
  })
  
  // If no minor, zero it out explicitly
  if (!studentMinor.value) {
    const minorCat = categories.find(c => c.type === 'Minor')
    if (minorCat) {
      minorCat.total = 0
      minorCat.complete = 0
      minorCat.percent = 0
      minorCat.creditsTotal = 0
      minorCat.creditsComplete = 0
      minorCat.creditsPercent = 0
    }
  }
  
  return {
    total, complete, required, inProgress, 
    completeCredits, inProgressCredits, totalCredits, overallPercent,
    categories
  }
})

/* ======== TABLE CONFIG ======== */
const headers = [
  { title: 'Status', key: 'status', sortable: true, width: '10%' },
  { title: 'Code', key: 'code', sortable: true, width: '15%' },
  { title: 'Course Title', key: 'title', sortable: false },
  { title: 'Type', key: 'type', sortable: true, width: '15%' },
  { title: 'Cr', key: 'credits', sortable: true, align: 'end', width: '5%' },
  { title: 'Grade', key: 'completedGrade', sortable: true, width: '10%' },
  { title: 'Term Taken', key: 'completedTerm', sortable: true, width: '10%' }
]

const termHeaders = [
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Course Title', key: 'title', sortable: true },
  { title: 'Type', key: 'type', sortable: true },
  { title: 'Cr', key: 'credits', sortable: true, align: 'end' },
  { title: 'Grade', key: 'completedGrade', sortable: true },
  { title: 'Term Taken', key: 'completedTerm', sortable: true }
]

function getTermColor(termLabel: string) {
    const baseColor = 'rgba(0, 40, 86,' 
    if (termLabel.includes('Fall')) return baseColor + ' 0.9)'
    if (termLabel.includes('Spring')) return baseColor + ' 0.75)' 
    if (termLabel.toUpperCase() === 'UNSCHEDULED') return 'grey-darken-2'
    return baseColor + ' 0.9)' 
}

const nextPlannedTermLabel = computed(() => {
    const hasInProgress = progressCourses.value.some(c => c.status === 'In Progress')
    
    for (const group of groupedProgress.value) {
        const isFullyComplete = group.courses.every(c => c.status === 'Complete')
        const hasRequired = group.courses.some(c => c.status === 'Required')

        if (!isFullyComplete && hasRequired) {
            if (group.courses.some(c => c.status === 'In Progress')) {
                continue
            }
            return group.termLabel
        }
    }
    return null
})

function isCurrentOrNextTerm(termLabel: string, progressCourses: ProgressCourse[]): 'Current' | 'Next' | null {
    const isCurrent = progressCourses.some(c => 
        c.status === 'In Progress' && 
        c.completedTerm && 
        termLabel.toUpperCase().includes(c.completedTerm.toUpperCase().split(' ').pop() || termLabel.toUpperCase()) 
    );

    if (isCurrent) {
      return 'Current';
    }

    if (termLabel === nextPlannedTermLabel.value) {
        return 'Next';
    }
        
    return null
}

const showFutureDivider = computed(() => {
    return false
})

const firstFutureTerm = computed(() => {
    return groupedProgress.value.find(g => g.status === 'Required')
})

watch(groupedProgress, (groups) => {
  if (!expandedPanels.value.length && groups.length) {
    expandedPanels.value = [groups[0].termLabel]
  }
})
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
          
          <v-row class="mb-3" align="center" no-gutters>
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title
                  class="py-2 px-3 text-h6"
                  style="color:#002856;border:1px solid #002856;border-radius:8px;font-weight:700;letter-spacing:.25px;"
                >
                  {{ schoolName }} • {{ major || 'Loading Major...' }} • DEGREE AUDIT
                </v-card-title>
              </v-card>
            </v-col>
            <v-col cols="12" md="6" class="d-flex justify-end align-center flex-wrap" style="gap:10px;">
              <v-btn variant="outlined" color="#002856" @click="() => window.print()">
                <v-icon start>mdi-printer</v-icon>
                Print / Save PDF
              </v-btn>
            </v-col>
          </v-row>

          <v-card
            class="pa-4 mb-4"
            style="background-color:rgba(255,255,255,.9);border:1px solid #002856;text-align:left;border-radius:12px;"
          >
            <div class="text-h5 mb-3" style="color:#002856; font-weight:700;">
              Overall Degree Completion
            </div>
            
            <v-progress-linear
              :model-value="progressSummary.overallPercent"
              height="25"
              rounded
              color="#002856"
              class="mb-4"
            >
              <template #default="{ value }">
                <strong style="color:white; font-size: 1.1em;">{{ Math.ceil(value) }}% COMPLETE</strong>
              </template>
            </v-progress-linear>

            <v-row dense class="text-body-1 font-weight-medium">
              <v-col cols="12" sm="3">
                <strong>Total Req. Credits:</strong> 
                <span style="color:#002856;">{{ progressSummary.totalCredits }}</span>
              </v-col>
              <v-col cols="12" sm="3">
                <strong>Completed Credits:</strong> 
                <span class="text-success">{{ progressSummary.completeCredits }}</span>
              </v-col>
              <v-col cols="12" sm="3">
                <strong>In Progress Credits:</strong> 
                <span class="text-warning">{{ progressSummary.inProgressCredits }}</span>
              </v-col>
              <v-col cols="12" sm="3">
                <strong>Remaining Credits:</strong> 
                <span class="text-error">{{ progressSummary.totalCredits - progressSummary.completeCredits - progressSummary.inProgressCredits }}</span>
              </v-col>
            </v-row>
          </v-card>
          
          <v-card
            class="pa-4 mb-6"
            style="background-color:rgba(255,255,255,.9);border:1px solid #002856;text-align:left;border-radius:12px;"
          >
            <div class="text-h6 mb-3" style="color:#002856; font-weight:600;">
              Progress by Requirement Type (Credit Hours)
            </div>
            <v-row dense>
              <v-col 
                v-for="cat in progressSummary.categories" 
                :key="cat.type" 
                cols="12" 
                sm="6" 
                md="4"
              >
                <v-card class="pa-2" variant="tonal" :color="chipColor(cat.type)">
                  <div class="text-caption font-weight-bold">{{ cat.type }} ({{ cat.creditsTotal }} Cr)</div>
                  <v-progress-linear
                    :model-value="cat.creditsPercent"
                    height="12"
                    rounded
                    color="success"
                  >
                    <template #default="{ value }">
                      <span class="text-white text-caption">{{ Math.ceil(value) }}%</span>
                    </template>
                  </v-progress-linear>
                  <div class="text-caption text-right mt-1 font-weight-medium">
                    {{ cat.creditsComplete }} / {{ cat.creditsTotal }} credits
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card>


          <v-row v-if="loading">
              <v-col cols="12">
                  <v-progress-linear indeterminate color="#002856"></v-progress-linear>
                  <div class="text-center mt-3 text-body-1">Loading degree plan and transcript data...</div>
              </v-col>
          </v-row>
          <v-row v-else>
            <v-col cols="12">
              <div class="text-h6 mb-3" style="color:#002856; font-weight:700;">
                Degree Requirements by Recommended Semester
              </div>
            </v-col>

            <v-col cols="12">
              <v-expansion-panels v-model="expandedPanels" multiple>
                <v-expansion-panel
                  v-for="group in groupedProgress"
                  :key="group.termLabel"
                  :value="group.termLabel"
                >
                  <v-expansion-panel-title>
                    <div class="d-flex justify-space-between align-center w-100">
                      <div class="text-h6 font-weight-bold">{{ group.termLabel.toUpperCase() }}</div>
                      <div class="d-flex" style="gap:8px;">
                        <v-chip 
                          v-if="group.status === 'In Progress'"
                          color="warning"
                          variant="flat"
                          class="font-weight-bold"
                        >
                          IN PROGRESS (CURRENT/RECENT)
                        </v-chip>
                        <v-chip 
                          v-else-if="group.status === 'Required'"
                          color="error"
                          variant="flat"
                          class="font-weight-bold"
                        >
                          REQUIRED
                        </v-chip>
                        <v-chip 
                          v-else-if="group.status === 'Completed'"
                          color="success"
                          variant="flat"
                          class="font-weight-bold"
                        >
                          COMPLETED
                        </v-chip>
                        <v-chip 
                          v-else-if="group.status === 'Unscheduled'"
                          color="grey"
                          variant="flat"
                          class="font-weight-bold"
                        >
                          UNSCHEDULED
                        </v-chip>
                      </div>
                    </div>
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-card 
                      class="pa-4 mb-4" 
                      :color="getTermColor(group.termLabel)"
                    >
                      <v-data-table
                        :headers="termHeaders"
                        :items="group.courses"
                        :items-per-page="-1"
                        item-key="id"
                        class="mt-3 elevation-2"
                        show-expand
                        style="border-radius:8px;"
                      >
                        <template #item.status="{ item }">
                          <v-chip 
                            size="small" 
                            :color="statusStyle(item.status).color" 
                            variant="flat"
                            :prepend-icon="statusStyle(item.status).icon"
                            class="font-weight-medium"
                          >
                            {{ item.status }}
                          </v-chip>
                        </template>
                        
                        <template #item.type="{ item }">
                          <v-chip size="small" :color="chipColor(item.type)" variant="flat" class="font-weight-medium">{{ item.type }}</v-chip>
                        </template>
                        
                        <template #item.completedGrade="{ item }">
                          <span :class="{'font-weight-bold': item.status === 'Complete', 'text-success': item.status === 'Complete' && PASSING_GRADES.includes(item.completedGrade?.toUpperCase() ?? ''), 'text-error': item.status === 'Complete' && !PASSING_GRADES.includes(item.completedGrade?.toUpperCase() ?? '')}">
                            {{ item.completedGrade || (item.status === 'Complete' ? 'N/A' : '—') }}
                          </span>
                        </template>
                        
                        <template #item.credits="{ item }">
                          <span class="font-mono">{{ item.credits }}</span>
                        </template>
                        
                        <template #expanded-row="{ columns, item }">
                          <td :colspan="columns.length" class="pa-4" style="background:rgba(0,40,86,.05);">
                            <div class="text-subtitle-2 mb-1" style="color:#002856;">
                              {{ item.code }} • {{ item.title }}
                            </div>
                            <div class="text-body-2">{{ item.description || 'No description available.' }}</div>
                            
                            <div class="d-flex flex-wrap" style="gap:16px; margin-top:8px;">
                              <div>
                                <strong>Prerequisites:</strong>
                                <template v-if="item.prereqs?.length">
                                  <v-chip
                                    v-for="p in item.prereqs"
                                    :key="item.id + '-p-' + p"
                                    size="x-small"
                                    class="mr-1"
                                    variant="outlined"
                                    color="#002856"
                                  >
                                    {{ p }}
                                  </v-chip>
                                </template>
                                <span v-else>None</span>
                              </div>
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
                            </div>
                          </td>
                        </template>

                      </v-data-table>
                    </v-card>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-col>
          </v-row>
          
          <div class="text-center mt-6" style="color:#002856;">
           <div>
              © {{ new Date().getFullYear() }} — Numa Advising • University of Arkansas – Fort Smith
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
