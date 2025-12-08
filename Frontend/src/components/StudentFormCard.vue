<script setup>
import { ref, watch, defineProps, computed, onMounted } from 'vue'
import AdminAPI from '../apis/AdminAPI.js'
import AdvisorAPI from '../apis/AdvisorAPI.js'
import StudentAPI from '../apis/StudentAPI.js'
import { useUserStore } from '../store/user.js'
import DegreePlanAPI from '../apis/DegreePlanAPI.js'


const userStore = useUserStore()

const props = defineProps({
  student: { type: Object, default: null }, 
  visible: { type: Boolean, default: false },
  advisors: { type: Array, default: () => [] } 
})

const emits = defineEmits(['update:visible', 'close', 'saved'])

/*============== STATE AND STORES =================*/

const localVisible = ref(props.visible)
const selectedAdvisor = ref(null)
const currentAdvisor = ref(null)
const majors = ref([])
const selectedMajor = ref('')
const datePickerVisible = ref(false)
const tempDate = ref(null)
const displayDate = ref('')

/*============== FETCH POSSIBLE MAJORS ==============*/
async function fetchMajors() {
  try {
    console.log('Fetching Majors...');
    
    // Call the API method to fetch majors
    const majorOptions = await DegreePlanAPI.get_majors();
    
    // Check if we have valid data
    if (majorOptions && majorOptions.length > 0) {
      // Update the majors list with the fetched major options
      majors.value = majorOptions;
      console.log('Majors Fetched:', majors.value);
    } else {
      console.log('No majors found.');
    }
  } catch (err) {
    console.error('Error fetching degree plans or majors:', err);
  }
}


const advisorsList = computed(() =>
  (props.advisors || []).map(a => ({
    fullname: `${a.firstname || ''} ${a.lastname || ''}`.trim(),
    userid: String(a.userid)
  }))
)

/*============ WATCHES ==============*/

watch(() => props.visible, (newVal) => {
  localVisible.value = newVal;
  if (newVal) {
    fetchMajors();
  }
});

watch(() => props.student, (newStudent) => {
    if (newStudent) {
      // Set the current student's data
      form.value = { ...newStudent };
      // Make sure form.major is set correctly
      form.value.major = newStudent.major;
    }
  }, { immediate: true });



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
  role: 'student',
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
  dateadvised: null  
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

const isFieldEditable = computed(() => (field) => {
  if (!props.student) return true

  if (userStore.userRole === 'UAFS_ADMINS') {
    return true
  } else if (userStore.userRole === 'UAFS_ADVISORS') {
    return [
      'major', 'majorconcentration', 'minor', 'classstanding',
      'advisingstatus', 'dateadvised', 'advisinghold', 'preferences'
    ].includes(field)
  } else if (userStore.userRole === 'UAFS_STUDENTS') {
    return ['phonenumber', 'preferences'].includes(field)
  }
  return false
})

const isFormValid = computed(() => {
  if (!selectedAdvisor.value) return false //Checks if Advisor is selected
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
      if (userStore.userRole === "UAFS_ADMINS") {
        studentid = props.student.studentid
      } else if (userStore.userRole === "UAFS_ADVISORS") {
        studentid = props.student.userid
      }

      await StudentAPI.updateStudent(studentid, payload)
      alert('Successfully updated student!')
    } else {
      form.value.role = 'student'
      console.log(form)
      const response = await AdminAPI.addStudent(payload)
      studentid = response.studentid
      alert('Successfully added student!')
    }
    
    if (selectedAdvisor.value && userStore.userRole === "UAFS_ADMINS") {
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
    role: 'student',
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
    dateadvised: null 
  }
  selectedAdvisor.value = null
  currentAdvisor.value = null
  displayDate.value = ''
  tempDate.value = null
}

function formatDateToYYYYMMDD(value) {
  if (!value) return null

  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value
  }

  const date = new Date(value)
  if (isNaN(date)) return null

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

function onDateSelect(value) {
  const formatted = formatDateToYYYYMMDD(value)

  if (formatted) {
    displayDate.value = formatted
    form.value.dateadvised = formatted
    tempDate.value = value
  } else {
    displayDate.value = ''
    form.value.dateadvised = null
    tempDate.value = null
  }

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
    let advisor = null;
    
    if (userStore.userRole === "UAFS_ADMINS") {
      advisor = await AdvisorAPI.getAdvisorByStudent(newStudent.studentid)
    } else if (userStore.userRole === "UAFS_ADVISORS") {
      advisor = await AdvisorAPI.getAdvisorByStudent(newStudent.userid)
    }

    if (newStudent.dateadvised) {
      const formatted = formatDateToYYYYMMDD(newStudent.dateadvised)
      displayDate.value = formatted
      form.value.dateadvised = formatted
      tempDate.value = formatted
    } else {
      displayDate.value = ''
      form.value.dateadvised = null
      tempDate.value = null
    }

    if (advisor) {
      currentAdvisor.value = advisor
      selectedAdvisor.value = String(advisor.userid)
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

/*onMounted(async () => {
  try {
    const response = await AdvisorAPI.getAllAdvisors()
    advisors.value = response.map(a => ({
      fullname: a.firstname + ' ' + a.lastname,
      userid: a.userid
    }))
  } catch (err) {
    console.error('Failed to load advisors:', err)
  }
})*/
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
              <v-text-field v-model="form.firstname" label="First Name" 
              :disabled="!isFieldEditable('firstname')"
              :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.lastname" label="Last Name" 
              :disabled="!isFieldEditable('lastname')"
              :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.email" label="Email" 
              :disabled="!isFieldEditable('email')"
              :rules="[requiredRule, emailRule, value => charRule(value, 50, 'string')]" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.phonenumber" label="Phone Number" 
              :disabled="!isFieldEditable('phonenumber')"
              :rules="[requiredRule, value => charRule(value, 10, 'int')]" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.school" label="School" 
              :disabled="!isFieldEditable('school')"
              :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.gpa" label="GPA" type="number" 
              :disabled="!isFieldEditable('gpa')"
              :rules="[requiredRule, value => charRule(value, 10, 'decimal')]" />
            </v-col>
          </v-row>
          <v-row v-if="majors.length > 0">
            <v-col cols="6">
               <v-select
                  v-model="form.major"
                  :items="majors"
                  label="Major"
                  placeholder="Select Major"
                  :disabled="!isFieldEditable('major')"
                  :rules="[requiredRule]"
                />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.majorconcentration" label="Major Concentration" 
              :disabled="!isFieldEditable('majorconcentration')"
              :rules="[requiredRule, value => charRule(value, 50, 'string')]"/>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.minor" label="Minor" 
              :disabled="!isFieldEditable('minor')"
              :rules="[value => charRule(value, 50, 'string')]"/>
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.classstanding" label="Class Standing" 
              :disabled="!isFieldEditable('classstanding')"
              :rules="[requiredRule, value => charRule(value, 50, 'string')]" />
            </v-col>

            <v-spacer></v-spacer>
          </v-row>

          <v-row>
            <v-col>
              <v-select
                :key="advisorsList.map(a => a.userid).join('-')"
                v-model="selectedAdvisor"
                :items="advisorsList"
                item-title="fullname"
                item-value="userid"
                label="Advisor"
                placeholder="Select Advisor"
                persistent-placeholder
                :disabled="!isFieldEditable('advisor')"
                :rules="[requiredRule]"
              />
            </v-col>
          </v-row>

          <v-row v-if="currentAdvisor && isFieldEditable('advisor')" class="text-right" no-gutters>
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
                :disabled="!isFieldEditable('financialhold')"
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
                :disabled="!isFieldEditable('advisinghold')"
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
                :disabled="!isFieldEditable('academichold')"
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
                :disabled="!isFieldEditable('registrationstatus')"
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
                :disabled="!isFieldEditable('advisingstatus')"
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
                :disabled="!isFieldEditable('activestatus')"
                :rules="[requiredRule]"
                />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="displayDate"
                label="Date Advised"
                prepend-icon="mdi-calendar"
                :disabled="!isFieldEditable('dateadvised')"
                @click="isFieldEditable('dateadvised') ? datePickerVisible = true : null"
              />
            </v-col>
          </v-row>

          <v-dialog v-model="datePickerVisible" max-width="400px">
            <v-card>
              <v-card-title>Select Date</v-card-title>
              <v-card-text>
                <v-date-picker
                  v-model="tempDate"
                  @update:modelValue="onDateSelect"
                  color="primary"
                  width="100%"
                  hide-header
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
