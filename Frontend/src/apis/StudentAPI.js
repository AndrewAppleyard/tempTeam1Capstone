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
      Object.entries(updates).forEach(([key, value]) => {
        if (value === undefined || value === null) return;
        const preparedValue = typeof value === 'object' ? JSON.stringify(value) : value;
        formData.append(key, preparedValue);
      });
      const response = await api.post(`/Student/Update/${studentid}`, formData);
      console.log('Student Updated:', response.data);
      console.log(formData)
      return response.data;
    } catch (err) {
        console.error('Update Student Error:', err);
        throw err;
    }
  },

  async savePreferences(studentid, preferences) {
    try {
      const formData = new FormData();
      formData.append('preferences', JSON.stringify(preferences));
      const response = await api.post(`/Student/Update/${studentid}`, formData);
      console.log('Preferences saved:', response.data);
      return response.data;
    } catch (err) {
      console.error('Save Preferences Error:', err);
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
  },

  async getTranscripts(studentid) {
    try {
      const response = await api.get(`/Transcript/Student/GetTranscripts/${studentid}`);
      console.log('Fetched Transcripts:', response.data);
      return response.data;
    } catch (err) {
      console.error('Error fetching student transcripts:', err);
      throw err;
    }
  },

};