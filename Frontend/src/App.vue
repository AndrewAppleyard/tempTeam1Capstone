<script setup>
import NavBar from './components/NavBar.vue'
</script>

<template>
  <v-app>
    <div id="app">

    <NavBar />
    
    <v-main>
      <nav>
        <RouterLink to="/admin">Admin</RouterLink> |
        <RouterLink to="/advisor">Advisor</RouterLink> |
        <RouterLink to="/student">Student</RouterLink> |
        <RouterLink to="/transcript">Transcript</RouterLink>
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