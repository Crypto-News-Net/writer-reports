const config = {
  apiUrl: process.env.NODE_ENV === 'production' 
    ? 'https://writer-reports-api.onrender.com/api'
    : 'http://localhost:5000/api'
};

export default config;
