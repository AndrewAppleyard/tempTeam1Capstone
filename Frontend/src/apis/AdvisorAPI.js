import axios from 'axios';

export default {
  async getAllAdvisors() {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.get('/Advisor/',{
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('All Advisors:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get All Advisors Error:', err);
      throw err;
    }
  },

  async getAdvisorById(advisorid) {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.get(`/Advisor/${advisorid}`,{
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('Advisor Data:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get Advisor Error:', err);
      throw err;
    }
  },

  async getAdvisorStudents(advisorid) {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.get(`/Advisor/Student/${advisorid}`,{
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log(`Students for Advisor ${advisorid}:`, response.data);
      return response.data;
    } catch (err) {
      console.error('Get Advisor Students Error:', err);
      throw err;
    }
  },
};

async function getAdvisorByStudent(studentid) {
  try {
    const response = await axios.get(`Advisor/ByStudent/${studentid}`);
    console.log("Advisor data:", response.data);
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error("Error fetching advisor:", error.response.data);
    } else {
      console.error("Network or other error:", error.message);
    }
    return null;
  }
};
