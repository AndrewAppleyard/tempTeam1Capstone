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
  async getAdmin(adminid) {
    try {
      const token = sessionStorage.getItem("token");  
      const response = await axios.get(`/Admin/${adminid}`, {
          headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('Admin Data:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get Admin Error:', err);
      throw err;
    }
  },

  async addAdvisor(advisor) {
    try {
      const formData = new FormData();
      formData.append('firstname', advisor.firstname);
      formData.append('lastname', advisor.lastname);
      formData.append('email', advisor.email);
      formData.append('phonenumber', advisor.phonenumber);
      formData.append('role', advisor.role);
      formData.append('school', advisor.school);

      const token = sessionStorage.getItem("token"); 
      const response = await axios.post('/Admin/Advisor/Insert', formData,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      console.log('Advisor Added:', response.data);
      return response.data;
    } catch (err) {
      console.error('Add Advisor Error:', err);
      throw err;
    }
  },

  async updateAdvisor(advisorid, updates) {
    try {
      const formData = new FormData();
      Object.keys(updates).forEach(key => formData.append(key, updates[key]));
      const token = sessionStorage.getItem("token"); 

      const response = await axios.post(`/Admin/Advisor/Update/${advisorid}`, formData,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      console.log('Advisor Updated:', response.data);
      return response.data;
    } catch (err) {
      console.error('Update Advisor Error:', err);
      throw err;
    }
  },

  async deleteAdvisor(advisorid) {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.get(`/Admin/Advisor/${advisorid}`, null, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('Advisor Deleted:', response.data);
      return response.data;
    } catch (err) {
      console.error('Delete Advisor Error:', err);
      throw err;
    }
  },

  async addStudent(student) {
    try {
      const formData = new FormData();
      Object.keys(student).forEach(key => formData.append(key, student[key]));
      const token = sessionStorage.getItem("token");
      const response = await axios.post('/Admin/Student/Insert', formData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('Student Added:', response.data);
      return response.data;
    } catch (err) {
      console.error('Add Student Error:', err);
      throw err;
    }
  },

  async deleteStudent(studentid) {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.post(`/Admin/Student/${studentid}`, null, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });
      console.log('Student Deleted:', response.data);
      return response.data;
    } catch (err) {
      console.error('Delete Student Error:', err);
      throw err;
    }
  },

  async addStudentToAdvisor(advisorid, studentid) {
    try {
      const formData = new FormData();
      formData.append('advisorid', advisorid);
      formData.append('studentid', studentid);
      const token = sessionStorage.getItem("token");
      const response = await axios.post('/Admin/Student/Advisor', formData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (err) {
      console.error('Add Student to Advisor Error:', err);
      throw err;
    }
  },

  async removeStudentFromAdvisor(studentid, advisorid) {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.get(`/Admin/Student/Advisor/${studentid}/${advisorid}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (err) {
      console.error('Remove Student from Advisor Error:', err);
      throw err;
    }
  },

  async updateDegreePlans(count) {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.post(`/DegreePlan/UpdateDegreePlans/${count}`, null, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log("Degree Plan API Response:", response.data);
      return response.data;
      
    } catch (err) {
      console.error("Update Degree Plans Error:", err);
      throw err;
    }
  },

  async updateCurrentCourses() {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.post(`/CurrentCourses/AddCourses`, null, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log("Current Courses API Response:", response.data);
      return response.data;
      
    } catch (err) {
      console.error("Update Current Courses Error:", err);
      throw err;
    }
  }
};
