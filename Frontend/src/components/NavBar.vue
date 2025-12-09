<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useViewModeStore } from '../store/pinia.js'
import { useUserStore } from '../store/user.js'
const { viewMode, setViewMode } = useViewModeStore()
const userStore = useUserStore();

const drawer = ref(false)
const route = useRoute()
const router = useRouter()

const mode = computed(() => userStore.storedRole)
const isAdminRoute = computed(() => userStore.userRole === "UAFS_ADMINS")
const isStudentRoute = computed(() => userStore.userRole === "UAFS_STUDENTS")
const homePath = computed(() => {
  if (userStore.userRole === 'UAFS_STUDENTS') {
    return `/student`
  }
  if (userStore.userRole === 'UAFS_ADVISORS') {
    return `/advisor`
  }
  return '/'
})

function handleSetMode(mode) {
  console.log('Setting view mode to:', mode)
  setViewMode(mode)
  router.push('/admin')
  drawer.value = false
}

const initials = computed(() => {
  const firstInitial = userStore.firstName && userStore.firstName.length > 0 ? userStore.firstName[0] : '';
  const lastInitial = userStore.lastName && userStore.lastName.length > 0 ? userStore.lastName[0] : '';
  return `${firstInitial}${lastInitial}`.toUpperCase();
});
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

      <!-- advisor and student -->
      <template v-if="!isAdminRoute">
        <v-list-item link :to="{ path: homePath }" @click="drawer = false">
          <v-list-item-title>Home</v-list-item-title>
        </v-list-item>

        <v-divider></v-divider>
        
      </template>

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

      <!-- advisor -->
       <template v-if="!isAdminRoute && !isStudentRoute">
          <v-list-item 
          v-if="userStore.roleID"
          link 
          :to="{ path: `/advisorProfilePage` }" 
          @click="drawer = false"
        >
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item>
<!--<v-list-item 
          v-if="userStore.roleID"
          link 
          :to="{ path: `/userProfilePage` }" 
          @click="drawer = false"
        >
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item> -->
       </template>

      <!-- student  -->
      <template v-if="isStudentRoute">
        <v-list-item 
          v-if="userStore.roleID"
          link 
          :to="{ path: `/userProfilePage` }" 
          @click="drawer = false"
        >
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item>

        <v-list-item 
          v-if="userStore.roleID"
          link 
          :to="{ path: `/transcript` }" 
          @click="drawer = false"
        >
          <v-list-item-title>Transcript</v-list-item-title>
        </v-list-item>

        <v-list-item 
          v-if="userStore.roleID"
          link 
          :to="{ path: `/degreePlanProgressView` }" 
          @click="drawer = false"
        >
          <v-list-item-title>Degree Progress</v-list-item-title>
        </v-list-item>
      </template>

      <!-- admin, advisor, student -->
      <v-list-item
        link
        :to="{ path:`/courseCatalog`}"
        @click="drawer = false"
      >
        <v-list-item-title>Current Courses</v-list-item-title>
      </v-list-item>
      <v-list-item
        link
        :to="{path: '/degreePlanView'}"
        @click="drawer = false"
      >
        <v-list-item-title>Degree Plan</v-list-item-title>
      </v-list-item>

      <v-list-item @click="userStore.logout()">
        <v-list-item-title>Logout</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>

  <v-app-bar app color="#002856" class="pr-4">
    <v-app-bar-nav-icon color="#F5F5F5" @click="drawer = !drawer"></v-app-bar-nav-icon>

    <!-- NUMA ADVISING text -->
    <span
      class="ml-3 font-weight-bold text-white"
      style="font-size: 20px; font-weight: 700; cursor: pointer;"
      @click="router.push(homePath.value)"
    >
      NUMA ADVISING
    </span>

    <v-spacer />

    <v-card flat class="px-4 py-2 mr-4">
      <span>Hello, {{ userStore.firstName }} {{ userStore.lastName }}!</span>
    </v-card>

    <v-avatar color="#8C4799" size="36">
      <span style="color: #F5F5F5">{{ initials }}</span>
    </v-avatar>
  </v-app-bar>
</template>
