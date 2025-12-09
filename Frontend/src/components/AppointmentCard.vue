<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import AppointmentAPI from '../apis/AppointmentAPI.js'


const COLOR_PRIMARY = '#002856'
const COLOR_PANEL_BG  = '#F3F8FD' 

const props = defineProps<{
  advisorId: number | null
  advisorName: string
  advisorEmail: string
  advisorPhone: string
  studentId: number | null
  hasStudentId: boolean
  formatPhoneNumber: (rawNumber: string | null | undefined) => string
}>()

console.log("Inside appointment card", props)

/* =========================================================
   APPOINTMENT DATA & STATE
========================================================= */
const appointmentDialog = ref(false)
const appointmentSubmitting = ref(false)
const appointmentSnackbar = ref(false)
const appointmentSnackbarColor = ref<'success' | 'error' | 'info'>('success')
const appointmentSnackbarMessage = ref('')
const dateMenu = ref(false);

const TIME_OPTIONS = [
  { text: '9:00 AM', value: '09:00' },
  { text: '9:30 AM', value: '09:30' },
  { text: '10:00 AM', value: '10:00' },
  { text: '10:30 AM', value: '10:30' },
  { text: '11:00 AM', value: '11:00' },
  { text: '11:30 AM', value: '11:30' },
  { text: '12:00 PM', value: '12:00' },
  { text: '12:30 PM', value: '12:30' },
  { text: '1:00 PM', value: '13:00' },
  { text: '1:30 PM', value: '13:30' },
  { text: '2:00 PM', value: '14:00' },
  { text: '2:30 PM', value: '14:30' },
  { text: '3:00 PM', value: '15:00' },
  { text: '3:30 PM', value: '15:30' },
  { text: '4:00 PM', value: '16:00' },
  { text: '4:30 PM', value: '16:30' },
];

const appointmentForm = ref({
  advisorid: null as number | null,
  appointmentDate: new Date().toISOString().split('T')[0],
  appointmentTime: TIME_OPTIONS[0].value,
})

function showAppointmentSnackbar(message: string, color: 'success' | 'error' | 'info' = 'success', duration = 5000) {
  appointmentSnackbarMessage.value = message
  appointmentSnackbarColor.value = color
  appointmentSnackbar.value = true
}

/* =========================================================
   ACTION: APPOINTMENTS
========================================================= */
function openAppointmentDialog() {
  if (!props.studentId) {
    showAppointmentSnackbar('Cannot book appointment: Student ID not found.', 'error')
    return
  }
  
  appointmentForm.value.advisorid = props.advisorId
  
  if (!appointmentForm.value.advisorid) {
    showAppointmentSnackbar('Cannot book appointment: Advisor ID not available.', 'error')
    return
  }
  
  appointmentDialog.value = true
}

async function bookAppointment() {
  if (!props.studentId || !appointmentForm.value.advisorid) return

  appointmentSubmitting.value = true
  try {
    let cleanDate = appointmentForm.value.appointmentDate;
    if (typeof cleanDate !== 'string') {
        cleanDate = new Date(cleanDate).toISOString().split('T')[0];
    }

    const payload = {
      advisorid: appointmentForm.value.advisorid,
      // 'YYYY-MM-DD HH:MM:SS'
      start_time: `${cleanDate} ${appointmentForm.value.appointmentTime}:00`,
    }
    
    await AppointmentAPI.bookAppointment(props.studentId, payload) 
    
    showAppointmentSnackbar('Appointment request submitted successfully!', 'success')
    appointmentDialog.value = false
    
  } catch (err) {
    console.error('Appointment booking error:', err)
    showAppointmentSnackbar('Failed to book appointment. Please try again.', 'error')
  } finally {
    appointmentSubmitting.value = false
  }
}

const availableTimes = ref([]);

watch(
  () => appointmentForm.value.appointmentDate,
  async (newDate) => {
    if (!newDate || !props.advisorId) return;

    let cleanDate = newDate;
    if (typeof cleanDate !== 'string' || cleanDate.includes('T')) {
      cleanDate = new Date(cleanDate).toISOString().split('T')[0];
    }

    try {
      const times = await AppointmentAPI.getAvailableSlots(props.advisorId, cleanDate);
      console.log("API received the date:", cleanDate); // Verify the sent date
      console.log("Available times received:", times);
      availableTimes.value = times;
      
      if (!times.includes(appointmentForm.value.appointmentTime)) {
        appointmentForm.value.appointmentTime = null;
      }
    } catch (e) {
      console.error("Error loading available times", e);
      availableTimes.value = [];
    }
  },
  { immediate: true }
);

</script>

<template>
  <div>
    <v-card class="panel-card" :style="{ backgroundColor: COLOR_PANEL_BG }">
      <v-card-title class="panel-title">
        <v-icon size="20" class="mr-2">mdi-account-tie</v-icon>
        Advisor Information
      </v-card-title>
      <v-divider />
      <v-list density="comfortable" class="info-list">
        <v-list-item class="info-item">
          <strong>Name:</strong> {{ advisorName }}
        </v-list-item>
        <v-list-item class="info-item">
          <strong>Email: </strong>
          <a
            :href="'mailto:' + advisorEmail"
            v-if="advisorEmail !== 'TBA' && advisorEmail !== 'N/A'"
          >
            {{ advisorEmail }}
          </a>
          <span v-else>{{ advisorEmail }}</span>
        </v-list-item>
        <v-list-item class="info-item">
          <strong>Phone:</strong> {{ formatPhoneNumber(advisorPhone) }}
        </v-list-item>
      </v-list>
      <v-card-actions class="justify-end pt-0 pb-3 pr-4">
        <v-btn
          color="primary" 
          variant="flat"
          :disabled="!hasStudentId || advisorName === 'TBA'"
          @click="openAppointmentDialog"
        >
          <v-icon start>mdi-calendar-plus</v-icon>
          Book Appointment
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-dialog
      v-model="appointmentDialog"
      max-width="600"
      aria-label="Book Appointment Dialog"
    >
      <v-card class="dialog-card">
        <v-card-title class="dialog-title">
          Book Appointment with {{ advisorName }}
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form @submit.prevent="bookAppointment">
            <v-row dense>
              <v-col cols="12">
                <v-text-field
                  v-model.number="appointmentForm.advisorid"
                  label="Advisor ID"
                  :hint="`Booking with: ${advisorName}`"
                  persistent-hint
                  density="comfortable"
                  :disabled="true"
                  type="number"
                  required
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-menu
                    v-model="dateMenu"
                    :close-on-content-click="false"
                    transition="scale-transition"
                    offset-y
                    min-width="auto"
                >
                    <template #activator="{ props }">
                    <v-text-field
                        v-model="appointmentForm.appointmentDate"
                        label="Appointment Date"
                        prepend-inner-icon="mdi-calendar"
                        readonly
                        v-bind="props"
                        density="comfortable"
                        required
                    />
                    </template>

                    <v-date-picker
                    v-model="appointmentForm.appointmentDate"
                    color="primary"
                    :min="new Date().toISOString().split('T')[0]"
                    @update:model-value="() => (dateMenu = false)"
                    />
                </v-menu>
                </v-col>

              <v-col cols="12" md="6">
                <!-- <v-select
                  v-model="appointmentForm.appointmentTime"
                  :items="TIME_OPTIONS"
                  item-title="text"
                  item-value="value"
                  label="Appointment Time"
                  density="comfortable"
                  required
                /> -->
                <v-select
                    v-model="appointmentForm.appointmentTime"
                    :items="availableTimes"
                    label="Appointment Time"
                    density="comfortable"
                    required
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="appointmentDialog = false" :disabled="appointmentSubmitting">Cancel</v-btn>
          <v-btn 
            color="primary" 
            @click="bookAppointment" 
            :loading="appointmentSubmitting"
            :disabled="!appointmentForm.appointmentDate || !appointmentForm.appointmentTime"
          >
            Confirm Booking
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="appointmentSnackbar"
      :timeout="5000"
      :color="appointmentSnackbarColor"
      location="bottom right"
    >
      {{ appointmentSnackbarMessage }}
      <template #actions>
        <v-btn :color="appointmentSnackbarColor === 'success' ? 'white' : 'red'" variant="text" @click="appointmentSnackbar = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>