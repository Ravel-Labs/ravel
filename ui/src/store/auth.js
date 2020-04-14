import API from '@/api'

const ls = window.localStorage

const auth = {
  namespaced: true,
  state: {
    loading: false,
    token: "",
    user: {
      id: '',
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
     'LOGIN_SUCCESS' (state, token) {
       state.loading = false
       state.error = undefined
       state.isAuthenticated = true
       state.token = token
       ls.setItem('token', token)
    },
    'LOGIN_FAILURE' (state, error) {
      state.loading = false
      state.error = error
      ls.setItem('token', undefined)
      state.token = undefined
      state.isAuthenticated = false
    },
    'LOGOUT_REQUEST' (state) {
      state.token = undefined
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
  getters: {
    token: state => state.token,
  },
  actions: {
    async login ({ commit, state }, user) {
      try {
        commit('LOGIN_REQUEST', user)
        let { data } = await API().post('/auth/login', {
          username: user.email,
          password: user.password,
        })
        commit('LOGIN_SUCCESS', data["access_token"])
      } catch (error) {
        commit('LOGIN_FAILURE', error)
      }
    },
    async logout ({ commit, state}) {
      try {
        commit('LOGOUT_REQUEST')
        commit('LOGOUT_SUCCESS')
      } catch (error) {
        commit('LOGOUT_FAILURE', error)
      }
    },
    async signup ({ commit, state }, user) {
      try {
        commit('SIGNUP_REQUEST')
        let { data } = await API().post('/auth/signup', {
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
        let { data } = await API().get('/auth/check')
        console.log('check response data: ', data)
      } catch(error) {
        if (error = 'Request failed with status code 405') {
          console.log('USER NOT LOGGED IN: ', error)
          commit('LOGIN_FAILURE')
        }
      }
    }
  }
}

export default auth
