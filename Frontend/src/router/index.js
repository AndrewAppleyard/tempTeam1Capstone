import { createWebHistory, createRouter } from 'vue-router'
import { useUserStore } from '../store/user.js'

import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import AdvisorView from '../views/AdvisorView.vue'
import StudentView from '../views/StudentView.vue'
import TranscriptView from '../views/TranscriptView.vue'
import CourseCatalogView from '../views/CourseCatalogView.vue'
import UserProfilePage from '../views/UserProfilePage.vue'
import AdvisorProfilePage from '../views/AdvisorProfilePage.vue'
import DegreePlanView from '../views/DegreePlanView.vue'
import DegreePlanProgressView from '../views/DegreePlanProgressView.vue'

const routes = [
  { path: '/', component: LoginView },
  { path: '/admin', component: AdminView },
  { path: '/advisor', component: AdvisorView },
  { path: '/student', component: StudentView },
  { path: '/transcript', component: TranscriptView },
  { path: '/courseCatalog', component: CourseCatalogView },
  { path: '/DegreePlanView', component: DegreePlanView },
  { path: '/degreePlanProgressView', component: DegreePlanProgressView },
  { path: '/UserProfilePage', component: UserProfilePage },
  { path: '/AdvisorProfilePage', component: AdvisorProfilePage },
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
    '/degreePlanProgressView',
    '/UserProfilePage',
  ],
  UAFS_ADVISORS: [
    '/advisor',
    // '/AdvisorProfilePage',
    '/UserProfilePage',
    '/student',
    '/transcript',
    '/courseCatalog',
    '/DegreePlanView',
    '/degreePlanProgressView'
  ],
  UAFS_ADMINS: [
    '/admin',
    '/advisor',
    '/student',
    '/courseCatalog',
    '/DegreePlanView',
  ],
}

router.beforeEach((to, from, next) => {
  return next()
})