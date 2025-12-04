import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import { router } from './router/index.js'
import { useUserStore } from './store/user.js'
// import router from './router/index.js'
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
})

async function bootstrap() {
  const app = createApp(App)

  const pinia = createPinia()
  app.use(pinia)
  app.use(vuetify)
  const userStore = useUserStore()
  //await userStore.restoreSession()
  await userStore.restoreLogin()

  app.use(router)

  app.mount('#app')
}
bootstrap()
