import axios from 'axios';

export default {
    data() {
        return {
            studentList: [],
        };
    },
    created() {
        axios.get('/APIs/advisorAPI') //request flask api
            .then(response => {
                console.log('Data:', response.data);
            })
            .catch(error => {
                console.error('Error', error);
            });

        axios.post('/APIs/advisorAPI', { //request flask api
            advisorID: '1234'
        })
            .then(response => {
                console.log('advisor created', response.data)
            })
            .catch(error => {
                console.error('Error', error);
            });
    }
}