import api from './API';

export default {
  async getAdmin(adminid) {
    try {
      const response = await api.get(`/Admin/${adminid}`);
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

      const response = await api.post('/Admin/Advisor/Insert', formData);
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

      const response = await api.post(`/Admin/Advisor/Update/${advisorid}`, formData);
      console.log('Advisor Updated:', response.data);
      return response.data;
    } catch (err) {
      console.error('Update Advisor Error:', err);
      throw err;
    }
  },

  async deleteAdvisor(advisorid) {
    try {
      const response = await api.get(`/Admin/Advisor/${advisorid}`, null);
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
      const response = await api.post('/Admin/Student/Insert', formData);
      console.log('Student Added:', response.data);

      // const ldapResponse = await api.post('/Admin/Student/Insert', formData);
      // console.log('Student Added to LDAP DB:', ldapResponse.data);
      return response.data;
    } catch (err) {
      console.error('Add Student Error:', err);
      throw err;
    }
  },

  async deleteStudent(studentid) {
    try {
      const response = await api.post(`/Admin/Student/${studentid}`, null);
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
      const response = await api.post('/Admin/Student/Advisor', formData);
      return response.data;
    } catch (err) {
      console.error('Add Student to Advisor Error:', err);
      throw err;
    }
  },

  async removeStudentFromAdvisor(studentid, advisorid) {
    try {
      const response = await api.get(`/Admin/Student/Advisor/${studentid}/${advisorid}`);
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
