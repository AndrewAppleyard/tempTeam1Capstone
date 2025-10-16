<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Provided state (kept and lightly extended for greeting)
const studentList = ref({
  name: ref("")
})

const students = [
  { studentID: 1, firstName: 'Yash', lastName: 'Patel' },
  { studentID: 2, firstName: 'Andrew', lastName: 'Appleyard' },
  { studentID: 3, firstName: 'Robert', lastName: 'Farrar' },
  { studentID: 4, firstName: 'Christopher', lastName: 'Monterroza' },
  { studentID: 5, firstName: 'Sophia', lastName: 'Praphan' }
]

function goToStudent(studentID) {
  // router.push(`/student/${studentID}`)
}

// ===== Local UI state =====
const userMenu = ref(false)
const currentDialog = ref(false)
const nextDialog = ref(false)

// Example data placeholders (6 rows)
const currentSchedule = ref(
  Array.from({ length: 6 }, () => ({ number: '', name: '' }))
)
const nextSchedule = ref(
  Array.from({ length: 6 }, () => ({ number: '', name: '' }))
)

const currentPopupRows = ref(
  Array.from({ length: 5 }, () => ({
    number: '', course: '', time: '', location: '', professor: '',
    availability: '', waitlist: ''
  }))
)
const nextPopupRows = ref(
  Array.from({ length: 5 }, () => ({
    number: '', course: '', time: '', location: '', professor: '',
    availability: '', waitlist: ''
  }))
)

// Greeting
const greetingName = computed(() =>
  studentList.value?.name?.value?.trim()
    ? studentList.value.name.value
    : '[Student Name]'
)
</script>

<template>
  <v-container fluid class="pa-4" style="max-width:1500px; background-color: #BDD5E7; border-radius:12px; border: 1px solid #002856;">
    
    <!-- Content -->
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
                <v-table class="schedule-table" aria-label="Current Semester Schedule">
                  <thead>
                    <tr>
                      <th class="text-left" style="width: 160px; border-bottom:1px solid #002856;">Course No.</th>
                      <th class="text-left" style="border-left: 1px solid #002856; border-bottom: 1px solid #002856;">Course</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, i) in currentSchedule" :key="'cur-'+i">
                      <td>{{ row.number }}</td>
                      <td style="border-left: 1px solid #002856;">{{ row.name }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </div>
            </v-card-text>

            <div class="card-fab" style="position: absolute; bottom: 22px;">
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
              class="py-3 px-4"
              style="color:#002856; border-bottom:1px solid #002856;"
            >
              NEXT SEMESTER SCHEDULE
            </v-card-title>

            <v-card-text class="pa-0">
              <div class="table-wrap">
                <v-table class="schedule-table" aria-label="Next semester schedule">
                  <thead>
                    <tr>
                      <th class="text-left" style="width: 160px; border-bottom:1px solid #002856;">Course No.</th>
                      <th class="text-left" style="border-left: 1px solid #002856; border-bottom:1px solid #002856;">Course</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, i) in nextSchedule" :key="'next-'+i">
                      <td>{{ row.number }}</td>
                      <td style="border-left: 1px solid #002856;">{{ row.name }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </div>
            </v-card-text>

            <div class="card-fab" style="position: absolute; bottom: 22px;">
              <v-btn
                icon
                color="#002856"
                class="elevate-fab"
                aria-label="Add next course"
                @click="nextDialog = true"
              >
                <v-icon>mdi-plus</v-icon>
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
            <v-card-title class="pa-3" style="color: #002856; border-bottom: 1px solid #002856;">ADVISOR INFORMATION</v-card-title>
            <v-list density="comfortable" style="padding-left: 5px; text-align: left; background-color: transparent">
              <v-list-item>
                <v-list-item-title>
                  <strong>Name:</strong> Dr. Andrew Mackey<!-- {{ advisor info grabbed from student }} -->
                </v-list-item-title>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>
                  <strong>Email:</strong>
                  <a href="mailto:amackey@uafs.edu"> amackey@uafs.edu</a> <!-- change this -->
                </v-list-item-title>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>
                  <strong>Phone:</strong> (555) 123-4567
                </v-list-item-title>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>
                  <strong>Office:</strong> Baldor 201
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
          <v-table aria-label="Add courses grid (6 rows by 7 columns)">
            <thead>
              <tr>
                <th>Course No.</th>
                <th>Course Name</th>
                <th>Time</th>
                <th>Location</th>
                <th>Professor Name</th>
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
          <v-btn variant="text" @click="currentDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="currentDialog = false">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- NEXT: Dialog -->
    <v-dialog v-model="nextDialog" width="900" aria-label="Next Semester Course Schedule Dialog">
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <span class="text-subtitle-1">Next Semester Course Schedule</span>
          <v-btn icon variant="text" aria-label="Close" @click="nextDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-0">
          <v-table aria-label="Add courses grid (6 rows by 7 columns)">
            <thead>
              <tr>
                <th>Course No.</th>
                <th>Course Name</th>
                <th>Time</th>
                <th>Location</th>
                <th>Professor Name</th>
                <th>Availability</th>
                <th>Waitlist</th>
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
              </tr>
            </tbody>
          </v-table>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="nextDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="nextDialog = false">Save</v-btn>
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