import api from './API';

export default {
  async getUserByEmail(email) {
    try {
      const response = await api.get(`/User/GetUserByEmail/${email}`);
      console.log('User UID', response.data);

      return response.data;
    } catch (err) {
      console.error('Get User By Email Error:', err);
      throw err;
    }
  },

  async getAdvisorByUID(userid) {
    try {
      const response = await api.get(`/User/GetAdvisorByUID/${userid}`); 
      console.log('Advisor ID received:', response.data.advisorid);
      
      return response.data.advisorid;
    } catch (err) {
      console.error('Get Advisor ID By UID Error:', err);
      throw err;
    }
  },

  async getStudentByUID(userid) {
    try {
      const response = await api.get(`/User/GetStudentByUID/${userid}`); 
      console.log('Student ID received:', response.data.studentid);
      
      return response.data.studentid;
    } catch (err) {
      console.error('Get Student ID By UID Error:', err);
      throw err;
    }
  }

};