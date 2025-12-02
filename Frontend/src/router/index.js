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
  { path: '/DegreePlanView', component: DegreePlanView },
  { path: '/UserProfilePage', component: UserProfilePage },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

const roleRoutes = {
  UAFS_STUDENTS: [
    '/student',
    '/transcript',
    '/courseCatalog',
    '/DegreePlanView',
    '/UserProfilePage',
  ],
  UAFS_ADVISORS: [
    '/advisor',
    '/UserProfilePage',
    '/student',
    '/transcript',
    '/courseCatalog',
    '/DegreePlanView',
  ],
  UAFS_ADMINS: [
    '/admin',
    '/UserProfilePage',
    '/advisor',
    '/student',
    '/courseCatalog',
  ],
}

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  const publicPaths = ['/']
  const isPublic = publicPaths.includes(to.path)

  if (!userStore.isLoggedIn && !isPublic) {
    return next('/')
  }

  if (userStore.isLoggedIn && to.path === '/') {
    const role = userStore.userRole

    if (role === 'UAFS_STUDENTS') {
      return next(`/student/${userStore.userID}`)
    }
    if (role === 'UAFS_ADVISORS') {
      return next(`/advisor/${userStore.userID}`)
    }
    if (role === 'UAFS_ADMINS') {
      return next('/admin')
    }

    return next('/')
  }

  const allowed = roleRoutes[userStore.userRole] || []
  const match = allowed.some(prefix => to.path.startsWith(prefix))
  if (userStore.isLoggedIn) {
    if (!match && !isPublic) {
      return next(allowed[0])
    }
  }

  if (!match && !isPublic) {
      if (role === 'UAFS_STUDENTS') {
        return next(`/student/${userStore.userID}`)
      }
      if (role === 'UAFS_ADVISORS') {
        return next(`/advisor/${userStore.userID}`)
      }
      if (role === 'UAFS_ADMINS') {
        return next('/admin')
      }
  }

  return next()
})