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
  async getAllStudents() {
    try {
      const response = await axios.get('/Student/');
      console.log('All Students:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get All Students Error:', err);
      throw err;
    }
  },

  async getStudentById(studentid) {
      try {
        const response = await axios.get(`/Student/${studentid}`);
        console.log('Student Data:', response.data);
        return response.data;
      } catch (err) {
        console.error('Get Advisor Error:', err);
        throw err;
      }
  },

  async updateStudent(studentid, role, updates) {
    try {
      const formData = new FormData();
        Object.keys(updates).forEach(key => formData.append(key, updates[key]));
    
        const response = await axios.post(`/Student/Update/${studentid}/${role}`, formData);
        console.log('Student Updated:', response.data);
        return response.data;
    } catch (err) {
        console.error('Update Student Error:', err);
        throw err;
    }
  },
};