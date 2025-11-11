<script setup>
import { ref, watch, defineProps, computed, onMounted } from 'vue'
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
const currentAdvisor = ref(null)

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

async function save() {
  try {
    let studentid = null
    if (props.student) {
      studentid = props.student.studentid
      await StudentAPI.updateStudent(studentid, form.value)
      
    } else {
      form.value.role = 'student'
      form.value.dateadvised = '2025-01-01' // should be empty
      const response = await AdminAPI.addStudent(form.value)

      studentid = response.data.studentid ?? null;

      console.log('AddStudent response:', response);
    }

    if (selectedAdvisor.value) {
      await AdminAPI.addStudentToAdvisor(selectedAdvisor.value, studentid)
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
    dateadvised: '' // needs to be null until set
  }
}

async function removeAdvisor() {
  if (!props.student || !currentAdvisor.value) return
  try {
    await AdminAPI.removeStudentFromAdvisor(props.student.studentid, currentAdvisor.value.userid)
    currentAdvisor.value = null
    selectedAdvisor.value = null
  } catch (err) {
    console.error('Remove Advisor Error:', err)
    alert('Failed to remove advisor.')
  }
}

function close() {
  localVisible.value = false
  emits('close')
}

watch(() => props.visible, (newVal) => {
  localVisible.value = newVal
})
watch(localVisible, (val) => {
  emits('update:visible', val)
})
watch(() => props.student, async (newStudent) => {
  if (!newStudent) {
    resetForm()
    currentAdvisor.value = null
    selectedAdvisor.value = null
    return
  }

  Object.assign(form.value, newStudent)
  
  try {
    const response = await AdvisorAPI.getAdvisorByStudent(newStudent.studentid)
    const advisor = response || null

    if (advisor) {
      currentAdvisor.value = advisor
      selectedAdvisor.value = advisor.userid
      console.log("current advisor : " + currentAdvisor.value.firstname + " " + currentAdvisor.value.lastname)
    } else {
      currentAdvisor.value = null
      selectedAdvisor.value = null
    }
  } catch (err) {
    console.error('Error fetching student advisor:', err)
    currentAdvisor.value = null
  }
}, { immediate: true })

onMounted(async () => {
  try {
    const response = await AdvisorAPI.getAllAdvisors()
    advisors.value = response.map(a => ({
      fullname: a.firstname + ' ' + a.lastname,
      userid: a.userid
    }))
  } catch (err) {
    console.error('Failed to load advisors:', err)
  }
})
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

            <v-spacer></v-spacer>
          </v-row>

          <v-row>
            <v-col>
              <v-select
                v-model="selectedAdvisor"
                :items="advisors"
                item-title="fullname"
                item-value="userid"
                label="Advisor"
                placeholder="Select Advisor"
                persistent-placeholder
              />
            </v-col>
          </v-row>

          <v-row v-if="currentAdvisor" class="text-right" no-gutters>
            <v-col cols="12">
              <v-btn color="error" text small @click="removeAdvisor">Remove</v-btn>
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
