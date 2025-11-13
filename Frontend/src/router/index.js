// import { createWebHistory, createRouter } from 'vue-router'
// import { useUserStore } from '../store/user.js'

// import LoginView from '../views/LoginView.vue'
// import AdminView from '../views/AdminView.vue'
// import AdvisorView from '../views/AdvisorView.vue'
// import StudentView from '../views/StudentView.vue'
// import TranscriptView from '../views/TranscriptView.vue'
// import CourseCatalogView from '../views/CourseCatalogView.vue'
// import UserProfilePage from '../views/UserProfilePage.vue'
// import DegreePlanView from '../views/DegreePlanView.vue'

// const routes = [
//   { path: '/', component: LoginView, },
//   { path: '/admin', component: AdminView, },
//   { path: '/advisor', component: AdvisorView },
//   { path: '/advisor/:advisorid', component: AdvisorView },
//   { path: '/student', component: StudentView },
//   { path: '/student/:studentid', component: StudentView },
//   { path: '/transcript', component: TranscriptView }, //based on studentID
//   { path: '/courseCatalog', component: CourseCatalogView },
//   { path: '/UserProfilePage', component: UserProfilePage },
//   { path: '/DegreePlanView', component: DegreePlanView }
//   // { path: '/adminDashboard', component: MainAdminView }, //crud
// ]

// export const router = createRouter({
//   history: createWebHistory(),
//   routes,
// })

// // // Guard: redirect based on login
// // router.beforeEach((to, from, next) => {
// //   const userStore = useUserStore()

// //   if (!userStore.isLoggedIn && to.path !== '/') {
// //     return next('/')
// //   }

// //   if (userStore.isLoggedIn && to.path === '/') {
// //     switch (userStore.userRole) {
// //       case 'student': return next(`/student`)//next(`/student/${userStore.userId}`)
// //       case 'advisor': return next(`/advisor`)//next(`/advisor/${userStore.userId}`)
// //       case 'admin': return next('/admin')
// //       default: return next('/')
// //     }
// //   }

// //   next()
// // })

// // export default router

import { createWebHistory, createRouter } from 'vue-router'
import { useUserStore } from '../store/user.js'

import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import AdvisorView from '../views/AdvisorView.vue'
import StudentView from '../views/StudentView.vue'
import TranscriptView from '../views/TranscriptView.vue'
import CourseCatalogView from '../views/CourseCatalogView.vue'
import UserProfilePage from '../views/UserProfilePage.vue'
import DegreePlanView from '../views/DegreePlanView.vue'

const routes = [
  { path: '/', component: LoginView },
  { path: '/admin', component: AdminView },
  { path: '/advisor', component: AdvisorView },
  { path: '/advisor/:advisorid', component: AdvisorView },
  { path: '/student', component: StudentView },
  { path: '/student/:studentid', component: StudentView },
  { path: '/transcript', component: TranscriptView },
  { path: '/courseCatalog', component: CourseCatalogView },
  { path: '/UserProfilePage', component: UserProfilePage },
  { path: '/DegreePlanView', component: DegreePlanView }
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

const roleRoutes = {
  student: ['/student', '/student/', '/transcript', '/courseCatalog', '/DegreePlanView', '/UserProfilePage'],
  advisor: ['/advisor', '/advisor/', '/UserProfilePage'],
  admin: ['/admin', '/UserProfilePage']
}

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  // userStore.restoreSession() 

  const publicPaths = ['/']
  const isPublic = publicPaths.includes(to.path)

  if (!userStore.isLoggedIn && !isPublic) {
    return next('/')
  }

  if (userStore.isLoggedIn && to.path === '/') {
    switch (userStore.userRole) {
      case 'UAFS_STUDENTS': return next('/student')
      case 'UAFS_ADVISORS': return next('/advisor')
      case 'UAFS_ADMINS': return next('/admin')
      default: return next('/')
    }
  }

  const allowedRoutes = roleRoutes[userStore.userRole] || []
  const pathMatches = allowedRoutes.some(r => to.path.startsWith(r))
  if (userStore.isLoggedIn && !pathMatches) {
    switch (userStore.userRole) {
      case 'UAFS_STUDENTS': return next('/student')
      case 'UAFS_ADVISORS': return next('/advisor')
      case 'UAFS_ADMINS': return next('/admin')
      default: return next('/')
    }
  }

  next()
})
