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
          // TODO: Update this with actually getting the user ID
          const user_id = 1
          let { data } = await api.post('/tracks', {
            name: track.name,
            user_id: user_id,
            artist: track.artist
          })
          commit('TRACK_SUCCESS', data)
        } catch (err) {
          commit('TRACK_FAILURE', err)
        }
      }
    }
}

export default tracks
