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
},
    async get_majors(){
         try{
        const response = await api.get('/DegreePlan/View');
        
        const degrees = response.data.degrees;
        let majorOptions = []
        const majors = new Set();

        degrees.forEach(degreePlan => {
        const major = degreePlan.degree;  // Or use `degreePlan.major` if that's the correct field
        if (major) {
          majors.add(major);  // Add the major to the Set
        }

      });

        majorOptions = Array.from(majors);
        console.log('Majors Retrieved ', majorOptions)
        return majorOptions;
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