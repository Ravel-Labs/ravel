import API from '@/api'
import router from '@/router'

const ls = window.localStorage

const auth = {
  namespaced: true,
  state: {
    loading: false,
    token: ls.getItem('token'),
    user: {
      id: '',
      email: ls.getItem('user:email'),
    },
    error: undefined
  },
  mutations: {
    'SET_USER' (state, user) {
      state.user.email = user.email
      ls.setItem('user:email', user.email)
      ls.setItem('user:id', user.id)
    },
    'CLEAR_USER' (state) {
      state.user = {}
    },
     'LOGIN_REQUEST' (state, user) {
        state.user.email = user.email
        state.loading = true
    },
     'LOGIN_SUCCESS' (state, token) {
       state.loading = false
       state.error = undefined
       state.token = token
       ls.setItem('token', token)
       router.push({ name: 'tracks' })
    },
    'LOGIN_FAILURE' (state, error) {
      state.loading = false
      state.error = error
      ls.setItem('token', '')
      state.token = ''
    },
    'LOGOUT_SUCCESS' (state) {
      ls.setItem('token', '')
      state.user = {}
    },
    'LOGOUT_FAILURE' (state, err) {
      state.error = err
    },
    'SIGNUP_REQUEST' (state, user) {
      state.loading = true
      state.error = undefined
    },
    'SIGNUP_SUCCESS' (state) {
      state.loading = false
      state.error = undefined
    },
    'SIGNUP_FAILURE' (state, error) {
      state.loading = false
      state.error = error
    },
    'CHECK_SUCCESS' (state) {
      state.isAuthenticated = true
    },
    'CHECK_FAILURE' (state, error) {
      state.token = ''
      state.user = {}
      state.error = error
    }
  },
  getters: {
    token: state => state.token,
    user: state => state.user
  },
  actions: {
    async login ({ commit }, user) {
      try {
        commit('LOGIN_REQUEST', user)
        let { data } = await API().post('/auth/login', {
          username: user.email,
          password: user.password,
        })
        commit('LOGIN_SUCCESS', data['access_token'])
      } catch (error) {
        commit('LOGIN_FAILURE', error)
      }
    },
    async logout ({ commit }) {
      try {
        commit('LOGOUT_SUCCESS')
        router.push({ name: 'login' })
        location.reload()
      } catch (error) {
        commit('LOGOUT_FAILURE', error)
      }
    },
    async signup ({ commit }, user) {
      try {
        commit('SIGNUP_REQUEST')
        await API().post('/auth/signup', {
          email: user.email,
          password: user.password,
          name: user.name
        })
        commit('SIGNUP_SUCCESS')
      } catch (error) {
        commit('SIGNUP_FAILURE', error)
      }
    },
    async check ({ commit, dispatch }) {
      try {
        let { data } = await API().get('/auth/check')
        commit('CHECK_SUCCESS', data)
      } catch (error) {
        if (error === "Request failed with status code 401") {
          console.log('failed with 401 error: ', error)
          commit('LOGOUT_REQUEST')
          commit('LOGOUT_SUCCESS')
        } else {
          console.log('general authentication error: ', error)
          throw new Error(error)
        }

        dispatch('CHECK_FAILURE', error)
        return error
      }
    }
  }
}

export default auth
