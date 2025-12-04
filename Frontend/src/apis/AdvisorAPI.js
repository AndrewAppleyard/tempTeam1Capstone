import api from './API';

export default {
  async getAllAdvisors() {
    try {
      const response = await api.get('/Advisor/');
      console.log('All Advisors:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get All Advisors Error:', err);
      throw err;
    }
  },

  async getAdvisorById(advisorid) {
    try {
      const response = await api.get(`/Advisor/${advisorid}`);
      console.log('Advisor Data:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get Advisor Error:', err);
      throw err;
    }
  },

  async getAdvisorStudents(advisorid) {
    try {
      const response = await api.get(`/Advisor/Student/${advisorid}`);
      console.log(`Students for Advisor ${advisorid}:`, response.data);
      return response.data;
    } catch (err) {
      console.error('Get Advisor Students Error:', err);
      throw err;
    }
  },

  async getAdvisorByStudent(studentid) {
    try {
      const response = await api.get(`/Advisor/ByStudent/${studentid}`);
      console.log("Advisor data:", response.data);
      return response.data;
    } catch (err) {
      console.error("Error fetching advisor:", err);
      throw err;
    }
  }  
};
