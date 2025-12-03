import api from './API';

export default {
  async getAllStudents() {
    try {
      const response = await api.get('/Student/');
      console.log('All Students:', response.data);
      return response.data;
    } catch (err) {
      console.error('Get All Students Error:', err);
      throw err;
    }
  },

  async getStudentById(studentid) {
      try {
        const response = await api.get(`/Student/${studentid}`);
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
        const response = await api.post(`/Student/Update/${studentid}`, formData);
        console.log('Student Updated:', response.data);
        return response.data;
    } catch (err) {
        console.error('Update Student Error:', err);
        throw err;
    }
  },

  async addSchedule(studentid) {
    try {
      const response = await api.post(`/Schedule/GenerateSchedule/${studentid}`);
      console.log('Schedule Generated:', response.data);
      return response.data;
    } catch (err) {
      console.error('Schedule Generated Error:', err);
      throw err;
    }
  },

  async checkAdvisingHold(studentid) {
    try {
      const response = await api.post(`/Schedule/CheckAdvisingHold/${studentid}`);
      console.log(response.data)
      return response.data;
    } catch (err) {
      console.error("Advising Hold Check Error:", err);
      throw err;
    }
  }
};