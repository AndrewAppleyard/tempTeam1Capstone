<script setup>
import NavBar from './components/NavBar.vue'
import { computed, onMounted } from 'vue'
import { useUserStore } from './store/user.js'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'

const userStore = useUserStore()
const route = useRoute()

const showNavBar = computed(() => {
  return userStore.isLoggedIn && route.path !== '/'
})

// restore token if available
// onMounted(() => {
//   userStore.restoreSession()
// })
</script>

<template>
  <v-app>
    <div id="app">
      <NavBar v-if="showNavBar" />

      <v-main>
        <nav>
          <RouterLink to="/UserProfilePage">User Profile</RouterLink> |
          <RouterLink to="/admin">Admin</RouterLink> |
          <RouterLink to="/advisor">Advisor</RouterLink> |
          <RouterLink to="/student">Student</RouterLink> |
          <RouterLink to="/transcript">Transcript</RouterLink> |
          <RouterLink to="/courseCatalog">Course Catalog</RouterLink> |
          <RouterLink to="/DegreePlanView">Degree Plan</RouterLink>
        </nav>

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
</style>