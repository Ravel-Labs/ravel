import API from '@/api'
import Cookies from 'js-cookie'

const api = API()

const auth = {
  namespaced: true,
  state: {
    loading: false,
    user: {
      email: '',
      name: ''
    },
    isAuthenticated: false,
    error: undefined
  },
  mutations: {
     'LOGIN_REQUEST' (state, user) {
        state.user.email = user.email
        state.loading = true
    },
     'LOGIN_SUCCESS' (state, data) {
       state.loading = false
       state.error = undefined
       state.isAuthenticated = true
    },
    'LOGIN_FAILURE' (state, error) {
      state.loading = false
      state.error = error
      state.isAuthenticated = false
    },
    'LOGOUT_REQUEST' (state) {
      state.loading = true
    },
    'LOGOUT_SUCCESS' (state, user) {
      state.loading = false
      state.user = {}
      state.isAuthenticated = false
    },
    'LOGOUT_FAILURE' (state, error) {
      state.loading = false
      state.error = error
    },
    'SIGNUP_REQUEST' (state, user) {
      state.loading = true
      state.error = undefined
    },
    'SIGNUP_SUCCESS' (state) {
      state.loading = false
      state.isAuthenticated = true
      state.error = undefined
    },
    'SIGNUP_FAILURE' (state, error) {
      state.loading = false
      state.isAuthenticated = false
      state.error = error
    }
  },
  actions: {
    async login ({ commit, state }, user) {
      try {
        commit('LOGIN_REQUEST', user)
        let { data, code } = await api.post('/auth/login', {
          email: user.email,
          password: user.password,
          remember: true
        })
        if (data == 'logged in successfully') {
          console.log('response: ', )
          commit('LOGIN_SUCCESS', data)
        } else if (data == 'user not found') {
          commit('LOGIN_FAILURE', 'User not found. Please try a different email.')
        } else {
          commit('LOGIN_FAILURE', 'Error: Failed to login.')
        }
      } catch (error) {
        commit('LOGIN_FAILURE', error)
      }
    },
    async logout ({ commit, state}) {
      try {
        commit('LOGOUT_REQUEST')
        let { data } = await api.post('/auth/logout')
        commit('LOGOUT_SUCCESS')
      } catch (error) {
        commit('LOGOUT_FAILURE', error)
      }
    },
    async signup ({ commit, state }, user) {
      try {
        commit('SIGNUP_REQUEST')
        let { data } = await api.post('/auth/signup', {
          email: user.email,
          password: user.password,
          name: user.name
        })
        commit('SIGNUP_SUCCESS', user)
      } catch (error) {
        commit('SIGNUP_FAILURE', error)
      }
    },
    async check ({ commit, state }) {
      try {
        let { data } = await api.post('/auth/check')
        console.log('check response: ', data)
      } catch(error) {
        if (error = 'Request failed with status code 405') {
          console.log('USER NOT LOGGED IN: ', error)
        }
      }
    }
  }
}

export default auth
