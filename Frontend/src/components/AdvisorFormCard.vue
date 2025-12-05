<script setup>
import { ref, watch, defineProps, defineEmits, computed } from 'vue'
import AdminAPI from '../apis/AdminAPI.js'
import Popups from '../components/Popups.vue'

const props = defineProps({
  advisor: { type: Object, default: null },
  visible: { type: Boolean, default: false }
})

const emits = defineEmits(['update:visible', 'close', 'saved'])

const form = ref({
  firstname: props.advisor?.firstname || '',
  lastname: props.advisor?.lastname || '',
  email: props.advisor?.email || '',
  phonenumber: props.advisor?.phonenumber || '',
  role: 'advisor',
  school: props.advisor?.school || '',

  // NEW FIELD (mandatory):
  // When editing → use existing advisortype
  // When adding → use the defaultType passed from admin view (“ROAR”)
  advisortype: props.advisor?.advisortype || props.defaultType || 'ROAR'

  
})

const advisorTypeOptions = [
  { title: 'ROAR Advisor', value: 'ROAR' },
  { title: 'College Advisor', value: 'COLLEGE' }
]


const localVisible = ref(props.visible)

const emailRule = value => {
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(value) || 'Please enter a valid email';
}

const requiredRule = value => (value !== null && value !== undefined && value !== '') || 'This field is required'

const charRule = (value, maxLength = 5, type = "string") => {

  if (value === false || value === true) return true
  
  if (value === null || value === undefined || value === '') return true

  if (value.length > maxLength) return `Max ${maxLength} characters allowed`

  const intPattern = /^\d+$/             

  if (type === 'int') {
    if (!intPattern.test(value)) return 'Must consist of only whole numbers'
  } 

  return true
}

const requiredFields = [
  'firstname',
  'lastname',
  'email',
  'phonenumber',
  'school',
]

const isFormValid = computed(() => {
  return requiredFields.every(field => {
    const value = form.value[field]

    if (value === null || value === '' || value === undefined) return false

    if (field === 'phonenumber') {
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
    if (props.advisor) {
      console.log('Updating advisor ID:', props.advisor?.userid) // advisorid = userid
      await AdminAPI.updateAdvisor(props.advisor.userid, form.value)
      alert('Successfully updated advisor!')
    } else {
      form.value.role = 'advisor'
      await AdminAPI.addAdvisor(form.value)
      alert('Successfully added advisor!')
    }
    emits('saved')
    localVisible.value = false
    resetForm()
  } catch (err) {
    console.error('Save Error:', err)
  }
}


function resetForm() { // need to reset id
  form.value = {
    firstname: '',
    lastname: '',
    email: '',
    phonenumber: '',
    role: 'advisor',
    school: ''
  }
}

function close() {
  localVisible.value = false
  resetForm()
  emits('close')
}

watch(() => props.visible, (newVal) => {
  localVisible.value = newVal
})
watch(localVisible, (val) => {
  emits('update:visible', val)
})
watch(() => props.advisor, (newAdvisor) => {
  if (newAdvisor) {
    Object.assign(form.value, newAdvisor)
  } else {
    Object.keys(form.value).forEach(key => form.value[key] = '')
  }
}, { immediate: true })
</script>

<template>
  <v-dialog v-model="localVisible" persistent max-width="500px">
    <v-card>
      <v-card-title class="headline">
        {{ props.advisor ? 'Update Advisor' : 'Add Advisor' }}
      </v-card-title>

      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="form.firstname"
                label="First Name"
                :rules="[requiredRule, value => charRule(value, 50, 'string')]"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.lastname"
                label="Last Name"
                :rules="[requiredRule, value => charRule(value, 50, 'string')]"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="form.email"
                label="Email"
                :rules="[emailRule, requiredRule, value => charRule(value, 50, 'string')]"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.phonenumber"
                label="Phone Number"
                :rules="[requiredRule, value => charRule(value, 10, 'int')]"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="form.school"
                label="School"
                :rules="[requiredRule, value => charRule(value, 50, 'string')]"
              />
            </v-col>

            <!-- NEW: Advisor Category (ROAR / College) -->
            <v-col cols="6">
          <v-select
            v-model="form.advisortype"
            :items="advisorTypeOptions"
            label="Advisor Category"
            item-title="title"
            item-value="value"
            density="comfortable"
            :rules="[requiredRule]"
          />
        </v-col>
          </v-row>
        </v-container>
</v-card-text>


      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="red" text @click="close">Cancel</v-btn>
        <v-btn color="primary" :disabled="!isFormValid" @click="save">{{ props.advisor ? 'Update' : 'Add' }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
