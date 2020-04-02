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
        state.loading = true
    },
     'LOGIN_SUCCESS' (state, data) {
       state.loading = false
       state.error = undefined
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
    'LOGOUT_SUCCESS' (state, user) {
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
    async login ({ commit, state }, user) {
      try {
        commit('LOGIN_REQUEST', user)
        let { data, code } = await api.post('/auth/login', {
          email: user.email,
          password: user.password
        })
        if (data == 'logged in successfully') {
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
    }
  }
}

export default auth
