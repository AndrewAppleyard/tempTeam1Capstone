import axios from 'axios';

// Request Interceptor
axios.interceptors.request.use(
  config => {
    console.log('Sending Request:', {
      method: config.method,
      url: config.url,
      headers: config.headers,
      data: config.data, // Log request body if applicable
    });
    return config;
  },
  error => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response Interceptor
axios.interceptors.response.use(
  response => {
    console.log('Received Response:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: response.data, // Log response body
    });
    return response;
  },
  error => {
    console.error('Response Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export default {
  async getAllAdvisors() {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.get('/Advisor/', {
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
      const response = await axios.get(`/Advisor/${advisorid}`, {
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
      const response = await axios.get(`/Advisor/Student/${advisorid}`, {
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

  async getAdvisorByStudent(studentid) {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.get(`/Advisor/ByStudent/${studentid}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log("Advisor data:", response.data);
      return response.data;
    } catch (err) {
      console.error("Error fetching advisor:", err);
      throw err;
    }
  }  
};
