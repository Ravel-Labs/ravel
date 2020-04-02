import api from '@/api'

const auth = {
  namespaced: true,
  state: {
    loading: false,
    user: {
      email: "",
      name: ""
    },
    isAuthenticated: false,
    error: undefined
  },
  mutations: {
     'LOGIN_REQUEST' (state, user) {
      state.user.email = user.email
      state.user.name = user.name
      state.loading = true
    },
     'LOGIN_SUCCESS' (state, user) {
       state.loading = false
       state.user.email = user.email
       state.user.name = user.name
    },
    'LOGIN_FAILURE' (state, error) {
      state.loading = false
      state.error = error
    },
    'LOGOUT_REQUEST' (state) {
      state.loading = true
      state.user = {}
      state.isAuthenticated = false
    },
    'LOGOUT_SUCCESS' (state) {
      state.loading = false
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
    async login ({ commit, state }, credentials) {
      try {
        commit('LOGIN_REQUEST')
        let { data } = await api.post('/auth/login', data)
        commit('LOGIN_SUCCESS', data)
        console.log('login: ', data)
      } catch (error) {
        commit('LOGIN_FAILURE', error)
      }
    },
    async logout ({ commit, state}) {
      try {
        commit('LOGOUT_REQUEST')
        let { data } = await api.post('/auth/logout')
        console.log('logout: ', data)
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
    }
  }
}

export default auth
