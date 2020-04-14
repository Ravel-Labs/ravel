import axios from 'axios'
import store from '@/store'

export default function init(router) {
    axios.interceptors.request.use(function(config) {
      const token = store.getters.token;
      if (token) {
        console.log('token being added to headers: ', token)
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    }, function(err) {
      console.log('error:', err)
      console.log('router: ', router)
      return Promise.reject(err);
    });
}
