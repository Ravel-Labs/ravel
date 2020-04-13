import API from '@/api'

const tracks = {
    namespaced: true,
    state: {

    },
    mutations: {

    },
    actions: {
      async create ({ commit, state }, track) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await api.post('/tracks', {})
          commit('TRACK_SUCCESS', data)
        } catch (err) {
          commit('TRACK_FAILURE', err)
        }
      }
    }
}

export default tracks
