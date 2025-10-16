import axios from 'axios';

export default {
  data() {
    return {
      advisorList: [],
      studentList: [],
    };
  },
  methods: {
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

    async deleteAdvisor(advisorid) {
      try {
        const response = await axios.get(`/Admin/Advisor/${advisorid}`); // axios.delete
        console.log('Advisor Deleted:', response.data);
        return response.data;
      } catch (err) {
        console.error('Delete Advisor Error:', err);
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


    async addStudent(student) {
      try {
        const formData = new FormData();
        formData.append('firstname', student.firstname);
        formData.append('lastname', student.lastname);
        formData.append('email', student.email);
        formData.append('phonenumber', student.phonenumber);
        formData.append('role', student.role);
        formData.append('school', student.school);
        formData.append('gpa', student.gpa);
        formData.append('major', student.major);
        formData.append('majorconcentration', student.majorconcentration || '');
        formData.append('minor', student.minor || '');
        formData.append('classstanding', student.classstanding || '');
        formData.append('classes', JSON.stringify(student.classes || []));
        formData.append('financialhold', student.financialhold || false);
        formData.append('advisinghold', student.advisinghold || false);
        formData.append('academichold', student.academichold || false);
        formData.append('registrationstatus', student.registrationstatus || false);
        formData.append('advisingstatus', student.advisingstatus || false);
        formData.append('activestatus', student.activestatus || true);
        if (student.dateadvised) {
          formData.append('dateadvised', student.dateadvised); // MM-DD-YYYY
        }

        const response = await axios.post('/Admin/Student/Insert', formData);
        console.log('Student Added:', response.data);
        return response.data;
      } catch (err) {
        console.error('Add Student Error:', err);
        throw err;
      }
    },

    async deleteStudent(studentid) {
      try {
        const response = await axios.get(`/Admin/Student/${studentid}`); // axios.delete
        console.log('Student Deleted:', response.data);
        return response.data;
      } catch (err) {
        console.error('Delete Student Error:', err);
        throw err;
      }
    },

    
    async addStudentToAdvisor(studentid, advisorid) {
      try {
        const formData = new FormData();
        formData.append('studentid', studentid);
        formData.append('advisorid', advisorid);

        const response = await axios.post('/Admin/Student/Advisor', formData);
        console.log('Student Added to Advisor:', response.data);
        return response.data;
      } catch (err) {
        console.error('Add Student to Advisor Error:', err);
        throw err;
      }
    },

    async removeStudentFromAdvisor(studentid, advisorid) {
      try {
        const response = await axios.get(`/Admin/Student/Advisor/${studentid}/${advisorid}`);
        console.log('Student Removed from Advisor:', response.data);
        return response.data;
      } catch (err) {
        console.error('Remove Student from Advisor Error:', err);
        throw err;
      }
    },

    async getAdmin(adminid) {
      try {
        const response = await axios.get(`/Admin/${adminid}`);
        console.log('Admin Data:', response.data);
        return response.data;
      } catch (err) {
        console.error('Fetch Admin Error:', err);
        throw err;
      }
    },
  },

  async created() {
    try {
      const admin = await this.getAdmin(1);
      console.log('Admin on Created:', admin);
    } catch (err) {
      console.error(err);
    }
  }
};