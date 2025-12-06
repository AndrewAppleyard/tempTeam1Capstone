import api from './API';

export default{
    async view_degree_plans(){
        try{
         const response = api.get('/DegreePlan/View');
        console.log('Degree Plans', response.data);
        } catch(err){
            console.log('Degree Plan Retrieval Error ', err);
        }
    }

}