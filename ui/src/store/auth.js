import API from '@/api'

const ls = window.localStorage

const auth = {
  namespaced: true,
  state: {
    loading: false,
    token: ls.getItem('token'),
    user: {
      id: '',
      email: '',
      name: ''
    },
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
       state.token = token
       ls.setItem('token', token)
    },
    'LOGIN_FAILURE' (state, error) {
      state.loading = false
      state.error = error
      ls.setItem('token', undefined)
      state.token = ''
    },
    'LOGOUT_REQUEST' (state) {
      console.log('logout request hit')
      state.token = ''
      state.loading = true
      ls.setItem('token', undefined)
    },
    'LOGOUT_SUCCESS' (state) {
      console.log('logout success hit')
      state.token = ''
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
      state.error = undefined
    },
    'SIGNUP_FAILURE' (state, error) {
      state.loading = false
      state.error = error
    },
    'CHECK_FAILURE' (state, error) {
      state.token = ''
      state.error = error
    }
  },
  getters: {
    token: state => ls.getItem('token')
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
      console.log('logout hit')
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
    async check ({ commit, state, dispatch }, router) {
      try {
        let { data } = await API().get('/auth/check')
        commit('CHECK_SUCCESS')
      } catch (error) {
        if (error === 'Request failed with status code 401') {
          console.log('failed with 401 error: ', error)
          commit('LOGOUT_REQUEST')
          commit('LOGOUT_SUCCESS')
          router.push({ path: '/login' })
        }
        if (error === 'Request failed with status code 405') {
          console.log('USER NOT LOGGED IN: ', error)
          commit('LOGIN_FAILURE')
        } else {
          console.log('general auth error: ', error)
        }
      }
    }
  }
}

export default auth
