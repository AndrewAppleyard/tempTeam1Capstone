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

const datePickerVisible = ref(false)
const tempDate = ref(null)
const displayDate = ref('')

//For select fields
const holdsOptions = [
  { text: 'No Hold', value: false },
  { text: 'Active Hold', value: true }
]

const registrationStatusOptions = [
  { text: 'Not Registered', value: false },
  { text: 'Registered', value: true}
]

const advisingStatusOptions = [
  { text: 'Needs Advising', value: false},
  { text: 'Advised', value: true}
]

const activeStatusOptions = [
  { text: 'Inactive', value: false},
  { text: 'Active', value: true}
]

const emailRule = value => {
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(value) || 'Please enter a valid email';
}

const requiredRule = value => (value !== null && value !== undefined && value !== '') || 'This field is required'

const charRule = (value, maxLength = 5, type = "string") => {
  
  if (value === null || value === undefined || value === '') return true

  if (value.length > maxLength) return `Max ${maxLength} characters allowed`

  const intPattern = /^\d+$/             
  const decimalPattern = /^\d+(\.\d+)?$/ 

  if (type === 'decimal') {
    if (!decimalPattern.test(value)) return 'Must be a number (integer or decimal)'
  } else if (type === 'int') {
    if (!intPattern.test(value)) return 'Must consist of only whole numbers'
  }

  return true
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
  financialhold: null,
  advisinghold: null,
  academichold: null,
  registrationstatus: null,
  advisingstatus: null,
  activestatus: null,
  dateadvised: null // needs to be null at first 
})

const requiredFields = [
  'firstname',
  'lastname',
  'email',
  'phonenumber',
  'school',
  'gpa',
  'major',
  'majorconcentration',
  'classstanding',
  'financialhold',
  'advisinghold',
  'academichold',
  'registrationstatus',
  'advisingstatus',
  'activestatus',
]

const isFormValid = computed(() => {
  return requiredFields.every(field => {
    const value = form.value[field]

    if (value === false || value === true) return true

    if (value === null || value === '' || value === undefined) return false

    if (field === 'gpa') {
      if (charRule(value, 10, 'decimal') !== true) return false
    } else if (field === 'phonenumber') {
      if (charRule(value, 10, 'int') !== true) return false
    } else if (field === 'email') {
      if (emailRule(value) !== true || charRule(value, 50, 'string') !== true) return false
    }
    else {
      if (charRule(value, 50, 'string') !== true) return false
    }

    return true
  })
})

async function save() {
  try {
    let studentid = null
    const payload = { ...form.value }

    if(!payload.dateadvised) {
      delete payload.dateadvised
    }

    if (props.student) {
      studentid = props.student.studentid
// <<<<<<< dev
//       await StudentAPI.updateStudent(studentid, payload)
//       //await StudentAPI.updateStudent(studentid, form.value)
      
//     } else {
//       form.value.role = 'student'
//       //form.value.dateadvised = '2025-01-01' 
//       const response = await AdminAPI.addStudent(payload)

//       console.log('AddStudent response:', response);
// =======
      await StudentAPI.updateStudent(studentid, form.value)
      alert('Successfully updated student!')
    } else {
      form.value.role = 'student'
      form.value.dateadvised = '2025-01-01' // should be empty
      await AdminAPI.addStudent(form.value)
      // studentid = response.data
      alert('Successfully added student!')
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
    financialhold: null,
    advisinghold: null,
    academichold: null,
    registrationstatus: null,
    advisingstatus: null,
    activestatus: null,
    dateadvised: null // needs to be null until set
  }
}

function convertToYDM(date) {
  if (!date) {

    return null
  }
  const [y, m, d] = date.split('-')
  return `${y}-${d}-${m}`
}

function onDateSelect(value) {
  if (value) {
    displayDate.value = value
    form.value.dateadvised = convertToYDM(value)
  } else {
    displayDate.value = ''
    form.value.dateadvised = null
  }

  tempDate.value = value || null
  datePickerVisible.value = false
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
  datePickerVisible.value = false
  resetForm()
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
              <v-text-field v-model="form.firstname" label="First Name" :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.lastname" label="Last Name" :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.email" label="Email" :rules="[requiredRule, emailRule, value => charRule(value, 50, 'string')]" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.phonenumber" label="Phone Number" :rules="[requiredRule, value => charRule(value, 10, 'int')]" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.school" label="School" :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.gpa" label="GPA" type="number" :rules="[requiredRule, value => charRule(value, 10, 'decimal')]" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.major" label="Major" :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.majorconcentration" label="Major Concentration" :rules="[requiredRule, value => charRule(value, 50, 'string')]"/>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.minor" label="Minor" :rules="[value => charRule(value, 50, 'string')]"/>
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.classstanding" label="Class Standing" :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
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
                :rules="[requiredRule]"
              />
            </v-col>
          </v-row>

          <v-row v-if="currentAdvisor" class="text-right" no-gutters>
            <v-col cols="12">
              <v-btn color="error" text small @click="removeAdvisor">Remove</v-btn>
            </v-col>
          </v-row>

          <v-row>
            <v-col>
              <v-select 
                v-model="form.financialhold"
                :items="holdsOptions"
                item-title="text"
                item-value="value"
                label="Financial Hold"
                placeholder="Hold"
                persistent-placeholder
                :rules="[requiredRule]"
                />
            </v-col>
          </v-row>

          <v-row>
            <v-col>
              <v-select 
                v-model="form.advisinghold"
                :items="holdsOptions"
                item-title="text"
                item-value="value"
                label="Advising Hold"
                placeholder="Hold"
                persistent-placeholder
                :rules="[requiredRule]"
                />
            </v-col>
          </v-row>

          <v-row>
            <v-col>
              <v-select 
                v-model="form.academichold"
                :items="holdsOptions"
                item-title="text"
                item-value="value"
                label="Academic Hold"
                placeholder="Hold"
                persistent-placeholder
                :rules="[requiredRule]"
                />
            </v-col>
          </v-row>

          <v-row>
            <v-col>
              <v-select 
                v-model="form.registrationstatus"
                :items="registrationStatusOptions"
                item-title="text"
                item-value="value"
                label="Registration Status"
                placeholder="Status"
                persistent-placeholder
                :rules="[requiredRule]"
                />
            </v-col>
          </v-row>

          <v-row>
            <v-col>
              <v-select 
                v-model="form.advisingstatus"
                :items="advisingStatusOptions"
                item-title="text"
                item-value="value"
                label="Advising Status"
                placeholder="Status"
                persistent-placeholder
                :rules="[requiredRule]"
                />
            </v-col>
          </v-row>

          <v-row>
            <v-col>
              <v-select 
                v-model="form.activestatus"
                :items="activeStatusOptions"
                item-title="text"
                item-value="value"
                label="Active Status"
                placeholder="Status"
                persistent-placeholder
                :rules="[requiredRule]"
                />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="displayDate"
                label="Date Advised"
                readonly
                prepend-icon="mdi-calendar"
                @click="datePickerVisible = true"
              />
            </v-col>
          </v-row>

          <v-dialog v-model="datePickerVisible" width="320px">
            <v-card>
              <v-card-title>Select Date</v-card-title>
              <v-card-text>
                <v-date-picker
                  v-model="tempDate"
                  @update:modelValue="onDateSelect"
                />
              </v-card-text>
            </v-card>
          </v-dialog>
           
        </v-container>

      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="red" text @click="close">Cancel</v-btn>
        <v-btn color="primary" :disabled="!isFormValid" @click="save">{{ props.student ? 'Update' : 'Add' }}</v-btn>
      </v-card-actions>

    </v-card>
  </v-dialog>
</template>
