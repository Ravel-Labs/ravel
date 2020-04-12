import axios from 'axios'
const ls = window.localStorage

export default () => axios.create({
  baseURL: 'http://localhost:5000/api/',
  headers: {
    'Authorization': `JWT ${ls.getItem('token')}`
  }
})
