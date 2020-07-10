
import axios from 'axios'
const ls = window.localStorage
export default () => axios.create({
  baseURL: `${process.env.VUE_APP_API_URL}`,
  headers: {
    'Authorization': `JWT ${ls.getItem('token')}`
  }
})
