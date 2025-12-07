import api from './API';

export default{
    async view_degree_plans(){
        try{
        const response = await api.get('/DegreePlan/View');
        console.log('Degree Plans', response.data);
        return response;
        } catch(err){
            console.log('Degree Plan Retrieval Error ', err);
        }
    },

    async view_degree_plans_by_degree(major){
    try{
        const formData = new URLSearchParams();
        formData.append("major", major);

        const response = await api.post("/DegreePlan/View/ByDegree", formData)
        return response;
    } catch(err){
        console.log('Degree Plan Retrieval Error ', err);
    }
}

}