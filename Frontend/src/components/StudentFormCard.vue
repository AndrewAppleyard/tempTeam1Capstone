<script setup>
import { ref, watch, defineProps, computed } from 'vue'
import AdminAPI from '../apis/AdminAPI.js'
import AdvisorAPI from '../apis/AdvisorAPI.js'
import StudentAPI from '../apis/StudentAPI.js'
import Popups from '../components/Popups.vue'

const props = defineProps({
  student: { type: Object, default: null }, 
  visible: { type: Boolean, default: false }
})

const emits = defineEmits(['update:visible', 'close', 'saved'])

const localVisible = ref(props.visible)
const advisors = ref([])
const selectedAdvisor = ref(null)

const emailRule = value => {
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(value) || 'Please enter a valid email';
}

const form = ref({
  firstname: '',
  lastname: '',
  email: '',
  phonenumber: '',
  school: '',
  gpa: '',
  major: '',
  majorconcentration: '',
  minor: '',
  classstanding: '',
  financialhold: false,
  advisinghold: false,
  academichold: false,
  registrationstatus: false,
  advisingstatus: false,
  activestatus: true,
  dateadvised: '' // needs to be null at first 
})

async function fetchAdvisors() {
  try {
    const response = await AdvisorAPI.getAllAdvisors()
    const list = response?.data ?? response ?? []

    advisors.value = (Array.isArray(list) ? list : []).map(a => ({
      advisorid: Number(a.advisorid ?? a.id ?? 0),
      fullname: `${a.firstname ?? ''} ${a.lastname ?? ''}`.trim()
    }))

    if (props.student?.advisorid) {
      selectedAdvisor.value = Number(props.student.advisorid)
    } else {
      selectedAdvisor.value = null
    }
  } catch (err) {
    console.error('Error fetching advisors:', err)
    advisors.value = []
  }
}

async function assignAdvisor(studentid) {
  if (!selectedAdvisor.value || !studentid) return
  try {
    const advisorid = selectedAdvisor.value
    await AdminAPI.addStudentToAdvisor(advisorid, studentid)
    console.log('Adding studentid=' + studentid + ' to advisorid=' + advisorid)
    alert('Advisor assigned successfully!')
  } catch (err) {
    console.error('Failed to assign advisor', err)
    alert('Failed to assign advisor')
  }
}

async function removeAdvisor() {
  const studentid = props.student?.studentid
  const advisorid = selectedAdvisor.value
  if (!studentid || !advisorid) return
  try {
    await AdminAPI.removeStudentFromAdvisor(studentid, advisorid)
    console.log('Removing studentid=' + studentid + ' from advisorid=' + advisorid)
    alert('Advisor removed successfully.')
    selectedAdvisor.value = null
    await fetchAdvisors()
  } catch (err) {
    console.error('Failed to remove advisor', err)
    alert('Failed to remove advisor')
  }
}

async function save() {
  try {
    const studentid = props.student?.studentid
    if (props.student) {
      console.log('Updating student ID:', studentid)
      const userRole = 'admin' // hardcoding for now
      await StudentAPI.updateStudent(studentid, userRole, form.value)
    } else {
      form.value.role = 'student'
      form.value.dateadvised = '2025-01-01' // should be empty
      await AdminAPI.addStudent(form.value)
      studentid = response?.data?.studentid ?? response?.studentid ?? null
    }

    if (studentid && selectedAdvisor.value) {
      await assignAdvisor(studentid)
    }

    emits('saved')
    localVisible.value = false
    resetForm()
  } catch (err) {
    console.error('Save Error:', err)
    alert('Failed to save student.')
  }
}

function resetForm() { // need to reset id
  form.value = {
    firstname: '',
    lastname: '',
    email: '',
    phonenumber: '',
    school: '',
    gpa: '',
    major: '',
    majorconcentration: '',
    minor: '',
    classstanding: '',
    financialhold: false,
    advisinghold: false,
    academichold: false,
    registrationstatus: false,
    advisingstatus: false,
    activestatus: true,
    dateadvised: '' // needs to be null at first 
  }
}

function close() {
  localVisible.value = false
  emits('close')
}

watch(() => props.visible, async (newVal) => {
  localVisible.value = newVal
  if (newVal) {
    await fetchAdvisors()
    if (props.student?.advisorid) {
      selectedAdvisor.value = props.student.advisorid
    } else {
      selectedAdvisor.value = null
    }
  }
})
watch(localVisible, (val) => {
  emits('update:visible', val)
})
watch(() => props.student, (newStudent) => {
  if (newStudent) {
    Object.assign(form.value, newStudent)
    selectedAdvisor.value = newStudent.advisorid ?? null
  } else {
    resetForm()
  }
}, { immediate: true })
</script>

<template>
  <v-dialog v-model="localVisible" persistent max-width="600px">
    <v-card>
      <v-card-title class="headline">
        {{ props.student ? 'Update Student' : 'Add Student' }}
      </v-card-title>

      <v-card-text>
        <v-container>

          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.firstname" label="First Name" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.lastname" label="Last Name" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.email" label="Email" :rules="[emailRule]" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.phonenumber" label="Phone Number" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.school" label="School" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.gpa" label="GPA" type="number" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.major" label="Major" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.majorconcentration" label="Major Concentration" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.minor" label="Minor" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.classstanding" label="Class Standing" />
            </v-col>
          </v-row>

           <v-row>
            <v-col cols="12">
              <v-select
                v-model="selectedAdvisor"
                :items="advisors"
                item-title="fullname"
                item-value="advisorid"
                label="Advisor"
                placeholder="Select Advisor"
                persistent-placeholder 
                clearable 
                hide-details 
                :menu-props="{ closeOnContentClick: true }"
              ></v-select>
            </v-col>
          </v-row>
          <v-row v-if="props.student && selectedAdvisor != null">
            <v-col cols="12" class="d-flex justify-end">
              <v-btn color="red" text @click="removeAdvisor">
                Remove Advisor
              </v-btn>
            </v-col>
          </v-row>

        </v-container>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey" text @click="close">Cancel</v-btn>
        <v-btn color="primary" @click="save">{{ props.student ? 'Update' : 'Add' }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>