import api from "./API";
import { useUserStore } from "../store/user.js"

export default {

    async login(username, password) {
        try {
            console.log("BEGINNING OF LOGIN")
            const response = await api.post("/Transfer/login", { username, password });
            console.log("AFTER AWAIT LOGIN")

            const userStore = useUserStore()
            if (response.data.login) {
            userStore.isLoggedIn = true
            userStore.userRole = response.data.Role
            userStore.userID = response.data.UserID || null
            userStore.email = response.data.Email || username
            } else {
            userStore.isLoggedIn = false
            userStore.userID = null
            userStore.email = null
            }

            console.log("Login successful:", response.data, "\nRole:", userStore.userRole);
            return response.data; 
        } catch (err) {
            console.error("Login failed:", err);
            throw err;
        }
    },

    async refresh() {
        try {
            const response = await api.post("/Transfer/refresh"); 
            console.log("Token refreshed:", response.data);
            return response.data;
        } catch (err) {
            console.error("Refresh failed:", err);
            throw err;
        }
    },

    async logout() {
        try {
            const response = await api.post("/Transfer/logout");
            console.log("Logout successful:", response.data);
            return response.data;
        } catch (err) {
            console.error("Logout failed:", err);
            throw err;
        }
    },
};