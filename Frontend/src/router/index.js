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
  { path: '/advisor/:id', component: AdvisorView },
  { path: '/student/:id', component: StudentView },
  { path: '/transcript/:id', component: TranscriptView },
  { path: '/courseCatalog/:studentid?', component: CourseCatalogView },
  { path: '/DegreePlanView/:id', component: DegreePlanView },
  { path: '/degreePlanProgressView/:id', component: DegreePlanProgressView },
  { path: '/UserProfilePage/:id', component: UserProfilePage },
  { path: '/AdvisorProfilePage/:id', component: AdvisorProfilePage },
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
  const userStore = useUserStore()

  const publicPaths = ['/']
  const isPublic = publicPaths.includes(to.path)

  if (!userStore.isLoggedIn && !isPublic) {
    return next('/')
  }

  if (userStore.isLoggedIn && to.path === '/') {
    switch (userStore.userRole) {
      case 'UAFS_STUDENTS': return next(userStore.roleID ? `/student/${userStore.roleID}` : '/student')
      case 'UAFS_ADVISORS': return next(userStore.roleID ? `/advisor/${userStore.roleID}` : '/advisor')
      case 'UAFS_ADMINS': return next('/admin')
      default: return next('/')
    }
  }

  if (userStore.isLoggedIn && userStore.userRole === 'UAFS_STUDENTS' && to.path === '/student' && userStore.roleID) {
    return next(`/student/${userStore.roleID}`)
  }

  if (userStore.isLoggedIn) {
    const allowed = roleRoutes[userStore.userRole] || []
    const match = allowed.some(prefix => to.path.startsWith(prefix))

    if (!match && !isPublic) {
      return next(allowed[0])
    }
  }

  return next()
})