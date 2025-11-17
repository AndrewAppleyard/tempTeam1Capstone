import axios from 'axios';

axios.interceptors.request.use(
  config => {
    console.log('Sending Request:', {
      method: config.method,
      url: config.url,
      headers: config.headers,
      data: config.data,
    });
    return config;
  },
  error => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  response => {
    console.log('Received Response:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: response.data,
    });
    return response;
  },
  error => {
    console.error('Response Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export default {
  async getAllDegreePlans() {
    try {
      const token = sessionStorage.getItem("token");
      const res = await axios.get('/DegreePlan/View', {
        headers: { Authorization: `Bearer ${token}` }
      });

      console.log("Degree Plans:", res.data);
      return res.data;
    } catch (err) {
      console.error("Get All Degree Plans Error:", err);
      throw err;
    }
  }
}