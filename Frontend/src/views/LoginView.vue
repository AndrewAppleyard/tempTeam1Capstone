<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user.js'

/* =========================
   STATE
========================= */
const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const message = ref('')

const form = ref(null)
const valid = ref(false)

/* =========================
   VALIDATION RULES
========================= */
const rules = {
  required: (v) => (!!v && v.toString().trim().length > 0) || 'Required',
  minPass: (v) => (v && v.length >= 6) || 'Min 6 characters'
}

/* =========================
   ACTIONS
========================= */
async function login() {
  const result = await form.value?.validate()
  if (!result?.valid) return

  loading.value = true
  message.value = ''

  try {
    await userStore.login(username.value, password.value)

    if (userStore.isLoggedIn) {
      message.value = 'Login successful!'

      switch (userStore.userRole) {
        case 'student':
          router.replace('/student')
          break
        case 'advisor':
          router.replace('/advisor')
          break
        case 'admin':
          router.replace('/admin')
          break
        default:
          router.replace('/')
      }
    } else {
      message.value = 'Invalid credentials.'
    }
  } catch (e) {
    console.error(e)
    message.value = 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}

/* UI helpers */
const loginDisabled = computed(() => !valid.value || loading.value)
</script>

<template>
  <v-container
    fluid
    class="pa-0"
    style="background-color: transparent; min-height: 100vh;"
  >

    <!-- Centered content -->
    <v-container class="fill-height">
      <v-row class="fill-height" align="center" justify="center">
        <v-col cols="12" sm="10" md="8" lg="6" xl="5">
          <v-card
            elevation="2"
            class="pa-6"
            style="background-color:#BDD5E7; border:1px solid #002856; border-radius:16px;"
          >
            <!-- Header -->
            <div class="text-center mb-1">
              <v-avatar size="56" class="mb-2" style="background:#F5F5F5; border:1px solid #002856;">
                <v-icon size="34" color="#002856">mdi-lock</v-icon>
              </v-avatar>
              <h1 style="font-size: 28px; margin:0; color:#002856;">
                Welcome to Numa Advising
              </h1>
              <p class="mt-1 mb-0" style="color:#002856; opacity:.9;">
                Secure portal for students & advisors
              </p>
            </div>

            <v-divider class="my-4" style="border-color:#002856;"></v-divider>

            <!-- Form -->
            <v-form ref="form" v-model="valid" @submit.prevent="login">
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="username"
                    label="Username"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required]"
                    bg-color="#F5F5F5"
                    prepend-inner-icon="mdi-account"
                    hide-details="auto"
                    autocomplete="username"
                  />
                </v-col>

                <v-col cols="12">
                  <v-text-field
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    label="Password"
                    variant="outlined"
                    density="comfortable"
                    :rules="[rules.required, rules.minPass]"
                    bg-color="#F5F5F5"
                    :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    @click:append-inner="showPassword = !showPassword"
                    prepend-inner-icon="mdi-lock"
                    hide-details="auto"
                    autocomplete="current-password"
                  />
                </v-col>

                <!-- Row for aux actions -->
                <v-col cols="12" class="d-flex justify-center">
                  <v-btn
                    variant="text"
                    color="#0032A0"
                    class="text-none"
                    @click="$emit('forgot-password')"
                  >
                    Forgot password?
                  </v-btn>
                </v-col>

                <v-col cols="12" class="mt-2">
                  <v-btn
                    block
                    size="large"
                    :disabled="loginDisabled"
                    :loading="loading"
                    color="#0032A0"
                    style="color:#F5F5F5;"
                    @click="login"
                  >
                    Log in
                  </v-btn>
                </v-col>
              </v-row>
            </v-form>

            <!-- Trust / Compliance -->
            <v-alert
              density="comfortable"
              class="mt-4"
              variant="tonal"
              type="info"
              :border="'start'"
              style="--v-theme-overlay-multiplier: 0; border-left: 4px solid #002856;"
            >
              Your credentials are encrypted in transit. By continuing, you agree to our
              <a href="#" style="color:#002856; text-decoration: underline;">Acceptable Use</a> and
              <a href="#" style="color:#002856; text-decoration: underline;">Privacy Policy</a>.
            </v-alert>

            <v-divider class="my-4" style="border-color:#002856;"></v-divider>
          </v-card>

          <!-- Subtle institution footer -->
          <div class="text-center mt-4" style="color:#002856; opacity:.85;">
            © {{ new Date().getFullYear() }} Numa Advising • University of Arkansas – Fort Smith
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<style scoped>
.v-btn { letter-spacing: 0.2px; }
.text-none { text-transform: none !important; }
</style>
