<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useViewModeStore } from '../store/pinia.js'
const { viewMode, setViewMode } = useViewModeStore()

const drawer = ref(false)
const route = useRoute()
const router = useRouter()

const isAdminRoute = computed(() => route.path.startsWith('/admin'))

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

const initials = computed(() => `${advisor.value.firstName[0]}${advisor.value.lastName[0]}`)
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

      <!-- change so it goes to the specific user's profile -->
      <v-list-item link :to="{ path: '/UserProfilePage' }" @click="drawer = false">
        <v-list-item-title>Profile</v-list-item-title>
      </v-list-item>

      <!-- admin -->
      <template v-if="isAdminRoute">
        <v-list-item link @click="handleSetMode('advisors')">
          <v-list-item-title>Advisors</v-list-item-title>
        </v-list-item>
        <v-list-item link @click="handleSetMode('students')">
          <v-list-item-title>Students</v-list-item-title>
        </v-list-item>
        <v-divider></v-divider>
      </template>

      <v-list-item
        v-if="viewMode === 'admin'"
        link
        :to="{ path: '/adminProfile' }"
        @click="drawer = false"
      >
        <v-list-item-title>Admin Profile</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="viewMode === 'admin'"
        link
        :to="{ path: '/addUser' }"
        @click="drawer = false"
      >
        <v-list-item-title>Add User</v-list-item-title>
      </v-list-item>

      <!-- advisor  -->
      <v-list-item
        v-if="viewMode === 'advisor'"
        link
        :to="{ path: '/advisorProfile' }"
        @click="drawer = false"
      >
        <v-list-item-title>Advisor Profile</v-list-item-title>
      </v-list-item>

      <!-- admin, advisor, student -->
      <v-list-item link :to="{ path: '/courseCatalog' }" @click="drawer = false">
        <v-list-item-title>Course Catalog</v-list-item-title>
      </v-list-item>
      <v-list-item link :to="{ path: '/DegreePlanView' }" @click="drawer = false">
        <v-list-item-title>Degree Plan</v-list-item-title>
      </v-list-item>
      <v-list-item link :to="{ path: '/' }" @click="drawer = false">
        <v-list-item-title>Logout</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>

  <v-app-bar app color="#002856" class="pr-4">
    <v-app-bar-nav-icon color="#F5F5F5" @click="drawer = !drawer"></v-app-bar-nav-icon>

    <v-spacer />

    <v-card flat class="px-4 py-2 mr-4">
      <span>Hello, {{ advisor.firstName }} {{ advisor.lastName }}!</span>
    </v-card>

    <v-avatar color="#8C4799" size="36">
      <span style="color: #F5F5F5">{{ initials }}</span>
    </v-avatar>
  </v-app-bar>
</template>