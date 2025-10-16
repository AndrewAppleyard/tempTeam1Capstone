import { createMemoryHistory, createRouter } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import AdvisorView from '../views/AdvisorView.vue'
import StudentView from '../views/StudentView.vue'
import TranscriptView from '../views/TranscriptView.vue'

const routes = [
  { path: '/', component: LoginView, },
  { path: '/admin', component: AdminView, },
  { path: '/advisor', component: AdvisorView },
  { path: '/advisor/:advisorid', component: AdvisorView },
  { path: '/student', component: StudentView },
  { path: '/student/:studentid', component: StudentView },
  { path: '/transcript', component: TranscriptView }, //based on studentID
  // { path: '/courseCatalog', component: CourseCatalogView },
  // { path: '/adminDashboard', component: MainAdminView }, //crud
]

export const router = createRouter({
  history: createMemoryHistory(),
  routes,
})