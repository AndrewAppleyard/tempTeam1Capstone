import api from './API';


export default{
    async getCurrentCourses(semester){
    try{
        const formData = new FormData();
        formData.append('semester', semester);
        const response = await api.post('/CurrentCourses/View/', formData);
        console.log('Current Course Data: ', response.data);

        return response.data;
    }
    catch(err){
        console.log('Get Current Course Error: ', err);
        throw err;
    }
    }

}

