import axios from 'axios';

export default {
  async getAllAdvisors() {
    try {
      const response = await axios.get('/Advisor/');
      console.log('All Advisors:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get All Advisors Error:', err);
      throw err;
    }
  },

  async getAdvisorById(advisorid) {
    try {
      const response = await axios.get(`/Advisor/${advisorid}`);
      console.log('Advisor Data:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get Advisor Error:', err);
      throw err;
    }
  },

  async getAdvisorStudents(advisorid) {
    try {
      const response = await axios.get(`/Advisor/Student/${advisorid}`);
      console.log(`Students for Advisor ${advisorid}:`, response.data);
      return response.data;
    } catch (err) {
      console.error('Get Advisor Students Error:', err);
      throw err;
    }
  },
};