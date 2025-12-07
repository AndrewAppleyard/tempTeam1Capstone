import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import UserAPI from '../apis/UserAPI'
import TransferAPI from '../apis/TransferAPI'
import Cookies from "js-cookie"
import { router } from '../router'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref(false)
  const userRole = ref(null)
  const userID = ref(null)
  const email = ref(null)
  const roleID = ref(null)
  const token = ref(null)
  const firstName = ref(null)
  const lastName = ref(null)

  async function restoreLogin() {
    const refreshToken = Cookies.get('csrf_refresh_token')
    if (!refreshToken) return
    try {
      const data = await TransferAPI.refresh() 

      isLoggedIn.value = true
      userRole.value = data.Role || null
      userID.value = data.UserID || null
      email.value = data.Email || null

      if (email.value) {
        await restoreUserDetails(email.value)
      }

    } catch (err) {
      isLoggedIn.value = false
      userRole.value = null
      userID.value = null
      email.value = null
      firstName.value = null
      lastName.value = null
      // roleID.value = null
    }
  }

  function decodeToken(jwt) {
    try {
      const base64 = jwt.split('.')[1]
      const decoded = JSON.parse(atob(base64))
      return decoded
    } catch (err) {
      console.error('Invalid JWT:', err)
      return null
    }
  }

  axios.interceptors.request.use((config) => {
    const storedToken = token.value || localStorage.getItem('token')
    if (storedToken) {
      config.headers.Authorization = `Bearer ${storedToken}`
    }
    return config
  })

  async function restoreUserDetails(email) {
    try {
      const userInfo = await UserAPI.getUserByEmail(email)

      firstName.value = userInfo.firstname
      lastName.value = userInfo.lastname

      if (userRole.value === 'UAFS_STUDENTS') {
          roleID.value = await UserAPI.getStudentByUID(userID.value);
      } else if (userRole.value === 'UAFS_ADVISORS') {
          roleID.value = await UserAPI.getAdvisorByUID(userID.value);
      }
    } catch (err) {
      console.error('Failed to restore user details:', err)
      // logout() 
    }
  }

  async function restoreSession() {
    const storedToken = localStorage.getItem('token')

    if (!storedToken) {
      return false
    }

    try {
      const payload = decodeToken(storedToken)
      if (!payload || !payload.Role) {
        return false
      }

      token.value = storedToken
      userRole.value = payload.Role
      userID.value = payload.userID // double check
      email.value = payload.Email
      isLoggedIn.value = true

      await restoreUserDetails(email.value)

      return true
    } catch (err) {
      console.error('JWT decode failed in restoreSession()', err)
      return false
    }
  }

  async function logout() {
    isLoggedIn.value = false
    userRole.value = null
    userID.value = null
    email.value = null
    token.value = null
    roleID.value = null
    firstName.value = null
    lastName.value = null

    try{
      const data = await TransferAPI.logout()
      console.log(data.logout)
    }catch (e) {
      console.warn('Logout request failed', e)
    }

    router.replace('/')
  }

  return { isLoggedIn, userRole, userID, email, roleID, token, firstName, lastName, logout, restoreSession, restoreLogin, decodeToken }
})