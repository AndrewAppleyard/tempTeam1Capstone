<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useViewModeStore } from '../store/pinia.js'
const { viewMode, setViewMode } = useViewModeStore()

const drawer = ref(false)
const route = useRoute()
const router = useRouter()

// const isAdminRoute = computed(() => route.path === '/admin')

function handleSetMode(mode) {
  console.log('Setting view mode to:', mode)
  setViewMode(mode)
  router.push('/admin')
  drawer.value = false
}

// placeholder
const advisor = ref({
  firstName: 'Andrew',
  lastName: 'Mackey',
})

const initials = `${advisor.value.firstName[0]}${advisor.value.lastName[0]}`
</script>

<template>
  <v-navigation-drawer v-model="drawer" app temporary color="#002856">
    <v-list>
      <v-list-item style="background-color: #F5F5F5; position: relative; height: 56px;">
        <v-list-item-title style="color: black; text-align: center; width: 100%; position: absolute; left: 0; right: 0; top: 17px;">
          Menu
        </v-list-item-title>
        <v-btn icon @click="drawer = false" style="position: absolute; right: 5px; top: 3px;">
          <v-icon color="#002856">mdi-menu</v-icon>
        </v-btn>
      </v-list-item>

      <v-divider></v-divider>

      <!-- grab id -->
      <v-list-item to="/userProfile" @click="drawer = false"> 
          <v-list-item-title>Profile</v-list-item-title>
      </v-list-item>

      <!-- admin -->
      <v-list-item v-if="viewMode === 'admin'" @click="handleSetMode('advisors')">
        <v-list-item-title>Advisors</v-list-item-title>
      </v-list-item>

      <v-list-item v-if="viewMode === 'admin'" @click="handleSetMode('students')">
        <v-list-item-title>Students</v-list-item-title>
      </v-list-item>

      <v-divider v-if="viewMode === 'admin'"></v-divider>

      <v-list-item v-if="viewMode === 'admin'">
        <v-list-item to="/adminProfile" @click="drawer = false">
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item>
        <v-list-item to="/addUser" @click="drawer = false">
          <v-list-item-title>Add User</v-list-item-title>
        </v-list-item>
      </v-list-item>

      <!-- advisor -->
      <v-list-item v-if="viewMode === 'admin'">
        <v-list-item to="/advisorProfile" @click="drawer = false">
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item>
      </v-list-item>

      <!-- admin, advisor, student -->
      <v-list-item v-if="viewMode === 'admin' || viewMode === 'advisor' || viewMode === 'student'">
        <v-list-item to="/courseCatalog" @click="drawer = false">
          <v-list-item-title>Course Catalog</v-list-item-title>
        </v-list-item>
        <v-list-item to="/" @click="drawer = false">
          <v-list-item-title>Logout</v-list-item-title>
        </v-list-item>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>

  <v-app-bar class="pr-4" app color="#002856">
    <v-app-bar-nav-icon @click="drawer = !drawer" color="#F5F5F5"></v-app-bar-nav-icon>

    <v-spacer />

    <v-card flat class="px-4 py-2 mr-4">
      <span>
        Hello, {{ advisor.firstName }} {{ advisor.lastName }}!
      </span>
    </v-card>

    <v-avatar color="#8C4799" size="36">
      <span color="#F5F5F5">{{ initials }}</span>
    </v-avatar>
  </v-app-bar>
</template>