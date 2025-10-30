import axios from 'axios';

export default {
    data() {
        return {
            advisorList: [],
            studentList: [],
        };
    },
    created() {
        axios.get('/APIs/AdminAPI') //request flask api
            .then(response => {
                console.log('Data:', response.data);
            })
            .catch(error => {
                console.error('Error', error);
            });

        axios.post('/APIs/AdminAPI', { //request flask api
            adminID: '1234'
        })
            .then(response => {
                console.log('Admin created', response.data)
            })
            .catch(error => {
                console.error('Error', error);
            });
    }
}