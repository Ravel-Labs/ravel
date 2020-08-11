import router from '@/router';
import axios from 'axios'
const ls = window.localStorage
const api = axios.create({
  baseURL: `${process.env.VUE_APP_API_URL}`,
  headers: {
    'Authorization': `JWT ${ls.getItem('token')}`
  }
})

// api.interceptors.response.use((response) => {
//   console.log('axios response: ', response)
//   return response
// }, (err) => {
//   console.error('axios error: ', err)
//   // TODO: Need to make this a singleton
//   // if (err == "Error: Request failed with status code 401") {
//   //   // handle missing token or token invalidation error
//   //   router.push({ name: 'login' })
//   //   return Promise.reject(err)
//   // }

//   // // handle and log general error
//   // console.log('axios interceptor error: ', err)
//   // return Promise.reject(err)
// })

export default () => api