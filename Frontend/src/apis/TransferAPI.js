import api from "./API";
import { useUserStore } from "../store/user.js"

export default {

    async login(username, password) {
        try {
            const response = await api.post("/Transfer/login", { username, password });

            const userStore = useUserStore()
            if (response.data.login) {
                userStore.isLoggedIn = true
                await userStore.restoreLogin()
            } else {
                userStore.isLoggedIn = false    
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
            localStorage.clear()
            const response = await api.post("/Transfer/logout");
            console.log("Logout successful:", response.data);
            return response.data;
        } catch (err) {
            console.error("Logout failed:", err);
            throw err;
        }
    },
};