<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AdvisorAPI from '../apis/AdvisorAPI'

/* =========================
   STATE
========================= */
const router = useRouter()
const loading = ref(true)
const error = ref(null)
const students = ref([])

const searchQuery = ref('')

/* =========================
   DATA FETCH
========================= */
async function fetchStudents() {
  loading.value = true
  error.value = null
  try {
    const advisorid = 1 // TODO: replace with real advisor id (from auth/store/route)
    const response = await AdvisorAPI.getAdvisorStudents(advisorid)

    const now = new Date()
    students.value = response.sort((a, b) => {
      const aHold = a.advisinghold || a.academichold || a.financialhold
      const bHold = b.advisinghold || b.academichold || b.financialhold
      if (aHold !== bHold) return bHold - aHold

      const aUpcoming = a.dateadvised && new Date(a.dateadvised) > now
      const bUpcoming = b.dateadvised && new Date(b.dateadvised) > now
      if (aUpcoming !== bUpcoming) return aUpcoming ? -1 : 1

      if (!a.dateadvised && b.dateadvised) return -1
      if (a.dateadvised && !b.dateadvised) return 1

      const aPast = a.dateadvised && new Date(a.dateadvised) < now
      const bPast = b.dateadvised && new Date(b.dateadvised) < now
      if (aPast !== bPast) return aPast ? 1 : -1

      return a.lastname.localeCompare(b.lastname)
    })
  } catch (e) {
    console.error('Error fetching students:', e)
    error.value = 'Failed to load students. Please try again.'
  } finally {
    loading.value = false
  }
}

/* =========================
   DERIVED / FILTERED DATA
========================= */
const filteredStudents = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return students.value

  return students.value.filter((s) => {
    const first = (s.firstname || '').toLowerCase()
    const last = (s.lastname || '').toLowerCase()
    const fullName = `${first} ${last}`.trim()
    const idStr = String(s.studentid || '').toLowerCase()

    return (
      fullName.includes(q) ||
      first.includes(q) ||
      last.includes(q) ||
      idStr.includes(q)
    )
  })
})

/* =========================
   UI HELPERS
========================= */
function goToStudent(studentid) {
  router.push(`/student/${studentid}`)
}

function hasInfo(s) {
  return (
    s.advisinghold ||
    s.academichold ||
    s.financialhold ||
    s.advisingstatus ||
    s.registrationstatus
  )
}

function getCardStyle(s) {
  const hasHold = s.advisinghold || s.academichold || s.financialhold
  const advising = s.advisingstatus
  let bg = 'transparent'
  if (hasHold) bg = '#FF746C'
  else if (advising) bg = '#ADEBB3'
  return {
    backgroundColor: bg,
    border: '1px solid #002856',
    borderRadius: '10px'
  }
}

onMounted(fetchStudents)
</script>

<template>
  <v-container fluid class="pa-2" style="background-color: transparent;">
    <v-row>
      <!-- 95% width shell -->
      <v-col cols="12" class="mx-auto advisor-shell">
        <v-card
          class="pa-5 heavy-page"
          style="background-color:#BDD5E7;border:1px solid #002856;border-radius:16px;"
        >
          <!-- Header -->
          <v-row class="mb-4" align="center" no-gutters>
            <v-col cols="12" md="6" class="d-flex align-center">
              <v-card flat class="elevation-0" style="background:transparent;">
                <v-card-title class="py-2 px-3 title-chip">
                  LIST OF STUDENTS
                </v-card-title>
              </v-card>
            </v-col>

            <v-col
              cols="12"
              md="6"
              class="d-flex justify-end align-center flex-wrap header-actions"
            >
              <v-text-field
                v-model="searchQuery"
                class="search-input"
                variant="outlined"
                density="compact"
                hide-details
                clearable
                :color="'#002856'"
                label="Search students"
                prepend-inner-icon="mdi-magnify"
              />

              <v-btn variant="outlined" color="#002856" @click="fetchStudents">
                <v-icon start>mdi-refresh</v-icon>
                Refresh
              </v-btn>
            </v-col>
          </v-row>

          <!-- Content Card -->
          <v-card class="pa-4 glass-card">
            <!-- Error -->
            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              class="mb-4"
              :border="'start'"
              style="border-left:4px solid #b00020;"
            >
              {{ error }}
            </v-alert>

            <!-- Loading Skeletons -->
            <v-row v-if="loading" dense>
              <v-col v-for="i in 8" :key="i" cols="12" sm="6" md="4" lg="3">
                <v-skeleton-loader
                  type="image, text, text"
                  class="glass-card pa-3"
                />
              </v-col>
            </v-row>

            <!-- Empty State: no students at all -->
            <div
              v-else-if="!students.length"
              class="text-center brand-primary py-10"
            >
              <v-icon size="48" class="mb-2">mdi-account-off</v-icon>
              <div class="text-h6 mb-1">No students found</div>
              <div>Try refreshing or check your advisor assignment.</div>
            </div>

            <!-- No matches for search -->
            <div
              v-else-if="students.length && !filteredStudents.length"
              class="text-center brand-primary py-10"
            >
              <v-icon size="48" class="mb-2">mdi-account-search</v-icon>
              <div class="text-h6 mb-1">No matching students</div>
              <div>
                No students match "<strong>{{ searchQuery }}</strong
                >". Try a different name or ID.
              </div>
            </div>

            <!-- Grid -->
            <v-row v-else dense>
              <v-col
                v-for="s in filteredStudents"
                :key="s.studentid"
                cols="12"
                sm="6"
                md="4"
                lg="3"
              >
                <v-card
                  class="pa-4 text-center student-card"
                  flat
                  :style="getCardStyle(s)"
                  @click="goToStudent(s.studentid)"
                >
                  <div
                    class="d-flex justify-center align-center mb-2"
                    style="gap:8px;"
                  >
                    <span class="user-name">
                      {{ s.firstname }} {{ s.lastname }}
                    </span>
                    <v-tooltip location="top">
                      <template #activator="{ props }">
                        <v-icon
                          v-if="hasInfo(s)"
                          v-bind="props"
                          size="18"
                          color="#002856"
                          class="cursor-pointer"
                        >
                          mdi-information-outline
                        </v-icon>
                      </template>

                      <div style="white-space: pre-line; font-size: 0.9rem;">
                        <strong>Advising Hold:</strong>
                        {{ s.advisinghold ? 'Yes' : 'No' }}\n
                        <strong>Academic Hold:</strong>
                        {{ s.academichold ? 'Yes' : 'No' }}\n
                        <strong>Financial Hold:</strong>
                        {{ s.financialhold ? 'Yes' : 'No' }}\n
                        <strong>Advising Status:</strong>
                        {{ s.advisingstatus || 'N/A' }}\n
                        <strong>Registration Status:</strong>
                        {{ s.registrationstatus || 'N/A' }}
                      </div>
                    </v-tooltip>
                  </div>

                  <v-card-subtitle
                    v-if="s.dateadvised"
                    class="text-caption"
                    style="color:black;"
                  >
                    {{
                      new Date(s.dateadvised) > new Date()
                        ? `Upcoming advising appointment: ${new Date(
                            s.dateadvised
                          ).toLocaleDateString()}`
                        : `Advised on: ${new Date(
                            s.dateadvised
                          ).toLocaleDateString()}`
                    }}
                  </v-card-subtitle>
                </v-card>
              </v-col>
            </v-row>
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

<style scoped>
/* 95% width shell to match other pages */
.advisor-shell {
  width: 95%;
  margin-left: auto;
  margin-right: auto;
}

/* Heavier but not flashy */
.heavy-page {
  font-size: 1.06rem;
  line-height: 1.55;
}

/* Title chip */
.title-chip {
  color: #002856;
  border: 1px solid #002856;
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: 0.25px;
  font-size: 1.15rem;
}

/* Subtle glass card look */
.glass-card {
  background-color: rgba(255, 255, 255, 0.6);
  border: 1px solid #002856;
  border-radius: 12px;
}

/* Brand helpers */
.brand-primary {
  color: #002856;
}

/* Header spacing */
.header-actions > .v-btn {
  margin-left: 10px;
  margin-top: 8px;
}

.search-input {
  min-width: 220px;
  max-width: 260px;
  margin-top: 8px;
}

/* Cards */
.student-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.student-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}
.user-name {
  font-weight: 650;
  font-size: 1.05rem;
}

/* Print */
@media print {
  .v-btn,
  .v-select,
  .v-text-field,
  .v-tabs {
    display: none !important;
  }
  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .v-card {
    box-shadow: none !important;
  }
}
</style>
