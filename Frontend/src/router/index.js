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
import NotFoundView from '../views/NotFoundView.vue'

// const routes = [
//   { path: '/', component: LoginView },
//   { path: '/admin', component: AdminView },
//   { path: '/advisor', component: AdvisorView },
//   { path: '/student', component: StudentView },
//   { path: '/transcript', component: TranscriptView },
//   { path: '/courseCatalog', component: CourseCatalogView },
//   { path: '/degreePlanView', component: DegreePlanView },
//   { path: '/degreePlanProgressView', component: DegreePlanProgressView },
//   { path: '/userProfilePage', component: UserProfilePage },
//   { path: '/advisorProfilePage', component: AdvisorProfilePage },
// ]


const routes = [
  { path: '/', component: LoginView },

  {
    path: '/admin',
    component: AdminView,
    meta: { roles: ['UAFS_ADMINS'] }
  },
  {
    path: '/advisor',
    component: AdvisorView,
    meta: { roles: ['UAFS_ADVISORS', 'UAFS_ADMINS'] }
  },
  {
    path: '/student',
    component: StudentView,
    meta: { roles: ['UAFS_STUDENTS', 'UAFS_ADVISORS', 'UAFS_ADMINS'] }
  },
  {
    path: '/transcript',
    component: TranscriptView,
    meta: { roles: ['UAFS_STUDENTS', 'UAFS_ADVISORS'] }
  },
  {
    path: '/courseCatalog',
    component: CourseCatalogView,
    meta: { roles: ['UAFS_STUDENTS', 'UAFS_ADVISORS', 'UAFS_ADMINS'] }
  },
  {
    path: '/degreePlanView',
    component: DegreePlanView,
    meta: { roles: ['UAFS_STUDENTS', 'UAFS_ADVISORS', 'UAFS_ADMINS'] }
  },
  {
    path: '/degreePlanProgressView',
    component: DegreePlanProgressView,
    meta: { roles: ['UAFS_STUDENTS', 'UAFS_ADVISORS'] }
  },
  {
    path: '/userProfilePage',
    component: UserProfilePage,
    meta: { roles: ['UAFS_STUDENTS'] }
  },
  {
    path: '/advisorProfilePage',
    component: AdvisorProfilePage,
    meta: { roles: ['UAFS_ADVISORS'] }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/not-found'
  },
  {
    path: '/not-found',
    component: NotFoundView
  }
]


export const router = createRouter({
  history: createWebHistory(),
  routes,
})

// router.beforeEach((to, from, next) => {
//   return next()
// })


router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (!userStore.isLoggedIn) {
    await userStore.restoreLogin()
  }

  const allowedRoles = to.meta?.roles
  if (allowedRoles) {
    if (!userStore.isLoggedIn) {
      return next('/') 
    }

    if (!allowedRoles.includes(userStore.userRole)) {
      return next('/not-found')
    }
  }

  next()
})

export default router