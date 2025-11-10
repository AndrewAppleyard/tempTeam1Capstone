<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import AdminAPI from '../apis/AdminAPI.js'
import Popups from '../components/Popups.vue'

const props = defineProps({
  advisor: { type: Object, default: null },
  visible: { type: Boolean, default: false }
})

const emits = defineEmits(['update:visible', 'close', 'saved'])

const form = ref({
  firstname: '',
  lastname: '',
  email: '',
  phonenumber: '',
  role: 'advisor',
  school: ''
})

const localVisible = ref(props.visible)

const emailRule = value => {
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(value) || 'Please enter a valid email';
}
  
async function save() {
  try {
    if (props.advisor) {
      console.log('Updating advisor ID:', props.advisor?.userid) // advisorid = userid
      await AdminAPI.updateAdvisor(props.advisor.userid, form.value)
    } else {
      form.value.role = 'advisor'
      await AdminAPI.addAdvisor(form.value)
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
            <!-- <v-col cols="6">
              <v-text-field v-model="form.role" label="Role" />
            </v-col> -->
            <v-col cols="6">
              <v-text-field v-model="form.school" label="School" />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey" text @click="close">Cancel</v-btn>
        <v-btn color="primary" @click="save">{{ props.advisor ? 'Update' : 'Add' }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
