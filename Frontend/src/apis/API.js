import axios from "axios"
import Cookies from "js-cookie"

const api = axios.create({
    // baseURL: "/",
    withCredentials: true,
})

api.interceptors.request.use((config) => {
  if (config.url && config.url.includes("/Transfer/refresh")) {
    const refreshCsrf = Cookies.get("csrf_refresh_token") ||
      (document && document.cookie.match(/(?:^|\s*)csrf_refresh_token=([^]+)/)?.[1])
    if (refreshCsrf) {
      config.headers["X-CSRF-TOKEN"] = refreshCsrf
    }
  } else {
    const accessCsrf = Cookies.get("csrf_access_token") ||
      (document && document.cookie.match(/(?:^|\s*)csrf_access_token=([^]+)/)?.[1])
    if (accessCsrf) {
      config.headers["X-CSRF-TOKEN"] = accessCsrf
    }
  }

  return config
}, (error) => Promise.reject(error))

let isRefreshing = false
let refreshPromise = null

api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log("[api] Response:", response.status, response.config.url)
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config

    if (!error.response) return Promise.reject(error)

    if (error.response.status === 401 && !originalRequest._retry) {
      if (!isRefreshing) {
        isRefreshing = true
        refreshPromise = api.post("/Transfer/refresh")
          .then((r) => {
            isRefreshing = false
            return r
          })
          .catch((refreshErr) => {
            isRefreshing = false
            throw refreshErr
          })
      }

      try {
        await refreshPromise
        originalRequest._retry = true
        return api(originalRequest)
      } catch (refreshError) {
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api
