import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref(false)
  const userRole = ref(null)
  const userID = ref(null)
  const email = ref(null)
  const token = ref(null)

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

  // async function login(username, password) {
  //   try {
  //     const res = await axios.post('http://127.0.0.1:5000/Transfer/login', {
  //       username,
  //       password
  //     })

  //     token.value = res.data.Token
  //     localStorage.setItem('token', token.value)

  //     const payload = decodeToken(token.value)
  //     if (payload) {
  //       userRole.value = payload.Role
  //       userID.value = payload.userID
  //       email.value = payload.Email
  //       isLoggedIn.value = true
  //     } else {
  //       logout()
  //     }
  //   } catch (err) {
  //     console.error('Login failed', err)
  //     logout()
  //     throw err
  //   }
  // }



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
      userID.value = payload.userID
      email.value = payload.Email
      isLoggedIn.value = true

      return true
    } catch (err) {
      console.error('JWT decode failed in restoreSession()', err)
      return false
    }
  }

  function logout() {
    isLoggedIn.value = false
    userRole.value = null
    userID.value = null
    email.value = null
    token.value = null

    localStorage.removeItem('token')
    localStorage.removeItem('role')

    window.location.href = '/'
  }

  // return { isLoggedIn, userRole, userID, email, token, login, logout, restoreSession }
  return { isLoggedIn, userRole, userID, email, token, logout, restoreSession }
})