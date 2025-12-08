// the backend methods and model are in AdvisorAPI.py and Advisor.py

import api from './API';

export default {
    
    async bookAppointment(studentid, appointment) {
        try {
            const formData = new FormData();
            Object.keys(appointment).forEach(key => formData.append(key, appointment[key]));

            const response = await api.post(`/Advisor/Appointment/${studentid}`, formData);
            console.log('Appointment Scheduled:', response.data);
            return response.data;
        } catch (err) {
            console.error("Error booking appointment:", err.response || err); 
            throw new Error(err.response?.data?.error || "Failed to book appointment.");
        }
    },

    async cancelAppointment(appointmentid) {
        try {
            const formData = new FormData();
            Object.keys(advisorid).forEach(key => formData.append(key, updates[key]));
            const response = await api.post(`/Advisor/Appointment/Cancel/${appointmentid}`, formData);
            console.log('Appointment cancelled:', response.data);
            return response.data;
        } catch (err) {
            console.error(`Error canceling appointment ID ${appointmentid}:`, err.response || err);
            throw new Error(err.response?.data?.error || "Failed to cancel appointment.");
        }
    }
}