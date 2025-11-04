import axios from 'axios';

export default {
  async getAllStudents() {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.get('/Student/',{
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('All Students:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get All Students Error:', err);
      throw err;
    }
  },

  async getStudentById(studentid) {
      try {
        const token = sessionStorage.getItem("token");
        const response = await axios.get(`/Student/${studentid}`,{
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        console.log('Student Data:', response.data);
        return response.data;
      } catch (err) {
        console.error('Get Advisor Error:', err);
        throw err;
      }
  },

  async updateStudent(studentid, updates) {
    try {
      const formData = new FormData();
        Object.keys(updates).forEach(key => formData.append(key, updates[key]));
        const token = sessionStorage.getItem("token");
        const response = await axios.post(`/Student/Update/${studentid}`, formData,{
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        console.log('Student Updated:', response.data);
        return response.data;
    } catch (err) {
        console.error('Update Student Error:', err);
        throw err;
    }
  },
};
