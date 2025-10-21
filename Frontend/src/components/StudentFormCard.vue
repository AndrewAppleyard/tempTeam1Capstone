<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import AdminAPI from '../apis/AdminAPI.js'
import StudentAPI from '../apis/StudentAPI.js'

const props = defineProps({
  student: { type: Object, default: null }, 
  visible: { type: Boolean, default: false }
})

const emits = defineEmits(['update:visible', 'close', 'saved'])

const localVisible = ref(props.visible)

watch(() => props.visible, (newVal) => {
  localVisible.value = newVal
})
watch(localVisible, (val) => {
  emits('update:visible', val)
})

const form = ref({
  firstname: '',
  lastname: '',
  email: '',
  phonenumber: '',
  // role: 'student',
  school: '',
  gpa: '',
  major: '',
  majorconcentration: '',
  minor: '',
  classstanding: '',
  classes: [],
  financialhold: false,
  advisinghold: false,
  academichold: false,
  registrationstatus: false,
  advisingstatus: false,
  activestatus: true,
  dateadvised: '' // needs to be null at first 
})

watch(() => props.student, (newStudent) => {
  if (newStudent) {
    Object.assign(form.value, newStudent)
  } else {
    Object.keys(form.value).forEach(key => form.value[key] = key === 'activestatus' ? true : '')
    form.value.classes = []
    form.value.financialhold = false
    form.value.advisinghold = false
    form.value.academichold = false
  }
}, { immediate: true })

async function save() {
  try {
    if (props.student) {
      console.log('Updating student ID:', props.student?.studentid)
      await StudentAPI.updateStudent(props.student.studentid, form.value)
    } else {
      form.value.role = 'student'
      form.value.dateadvised = '2025-01-01'
      await AdminAPI.addStudent(form.value)
    }
    emits('saved')
    localVisible.value = false
  } catch (err) {
    console.error('Save Error:', err)
  }
}

function close() {
  localVisible.value = false
  emits('close')
}
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
              <v-text-field v-model="form.email" label="Email" />
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
              <v-text-field v-model="form.major" label="Major" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="form.gpa" label="GPA" type="number" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.classstanding" label="Class Standing" />
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