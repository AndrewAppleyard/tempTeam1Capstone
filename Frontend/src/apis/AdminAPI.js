import axios from 'axios';

export default {
  async addAdvisor(advisor) {
    try {
      const formData = new FormData();
      formData.append('firstname', advisor.firstname);
      formData.append('lastname', advisor.lastname);
      formData.append('email', advisor.email);
      formData.append('phonenumber', advisor.phonenumber);
      formData.append('role', advisor.role);
      formData.append('school', advisor.school);

      const response = await axios.post('/Admin/Advisor/Insert', formData);
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
      const response = await axios.post(`/Admin/Advisor/Update/${advisorid}`, formData);
      console.log('Advisor Updated:', response.data);
      return response.data;
    } catch (err) {
      console.error('Update Advisor Error:', err);
      throw err;
    }
  },

  async deleteAdvisor(advisorid) {
    try {
      const response = await axios.get(`/Admin/Advisor/${advisorid}`);
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
      const response = await axios.post('/Admin/Student/Insert', formData);
      console.log('Student Added:', response.data);
      return response.data;
    } catch (err) {
      console.error('Add Student Error:', err);
      throw err;
    }
  },

  async updateStudent(studentid, updates) {
    try {
      const formData = new FormData();
      Object.keys(updates).forEach(key => formData.append(key, updates[key]));
      const response = await axios.post(`/Admin/Student/Update/${studentid}`, formData);
      console.log('Student Updated:', response.data);
      return response.data;
    } catch (err) {
      console.error('Update Student Error:', err);
      throw err;
    }
  },

  async deleteStudent(studentid) {
    try {
      const response = await axios.get(`/Admin/Student/${studentid}`);
      console.log('Student Deleted:', response.data);
      return response.data;
    } catch (err) {
      console.error('Delete Student Error:', err);
      throw err;
    }
  }
};