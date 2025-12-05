<script setup>
import NavBar from './components/NavBar.vue'
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useUserStore } from './store/user.js'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'

const userStore = useUserStore()
const route = useRoute()

const showNavBar = computed(() => {
  return userStore.isLoggedIn && route.path !== '/'
})

const pendingCount = ref(0)
const globalLoading = computed(() => pendingCount.value > 0)

function handlePending(event) {
  pendingCount.value = event.detail || 0
}

onMounted(() => {
  window.addEventListener('api:pending', handlePending)
})

onBeforeUnmount(() => {
  window.removeEventListener('api:pending', handlePending)
})

// restore token if available
// onMounted(() => {
//   userStore.restoreSession()
// })
</script>

<template>
  <v-app>
    <div id="app">
      <transition name="fade">
        <div v-if="globalLoading" class="global-loader-card">
          <v-card elevation="8" class="pa-3 d-flex align-center">
            <v-progress-circular
              indeterminate
              color="primary"
              size="26"
              width="3"
              class="mr-3"
            />
            <div class="text-body-2" style="color:#002856;">Working on request...</div>
          </v-card>
        </div>
      </transition>
      <NavBar v-if="showNavBar" />

      <v-main>
        <!-- <nav>
          <RouterLink to="/UserProfilePage">User Profile</RouterLink> |
          <RouterLink to="/admin">Admin</RouterLink> |
          <RouterLink to="/advisor">Advisor</RouterLink> |
          <RouterLink to="/student">Student</RouterLink> |
          <RouterLink to="/transcript">Transcript</RouterLink> |
          <RouterLink to="/courseCatalog">Course Catalog</RouterLink> |
          <RouterLink to="/DegreePlanView">Degree Plan</RouterLink>
        </nav> -->

        <router-view />

      </v-main>
    </div>
  </v-app>
</template>

<style>
.v-application {
  background-color: #E5F3FD !important;
}

body {
  background-color: #E5F3FD;
}

.global-loader {
  position: fixed;
  bottom: 16px;
  right: 16px;
  z-index: 2000;
}

.global-loader-card {
  position: fixed;
  bottom: 16px;
  right: 16px;
  z-index: 2100;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>