import API from '@/api'

const tracks = {
    namespaced: true,
    state: {
      list: [],
      error: "",
      loading: false
    },
    mutations: {
      'TRACK_REQUEST' (state) {
        console.log('mutation: TRACK_REQUEST', state)
        state.loading = true
      },

      'TRACK_SUCCESS' (state, tracks) {
        state.loading = false
        state.list = tracks
      },
      'TRACK_FAILURE' (state) {
        state.loading = false
      }
    },
    actions: {
      async create ({ commit, state }, track) {
        try {
          commit('TRACK_REQUEST')
          // TODO: Update this with actually getting the user ID
          const user_id = 1
          let { data } = await API().post('/tracks', {
            name: track.name,
            user_id: user_id,
            artist: track.artist
          })
          commit('TRACK_SUCCESS', data)
        } catch (err) {
          commit('TRACK_FAILURE', err)
        }
      },
      async get ({ commit, state }) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get('/tracks')
          console.table(data.payload)
          commit('TRACK_SUCCESS', data.payload)
        } catch (err) {
            console.log('error getting tracks: ', err)
            return err
        }
      },
      async update({ commit, state}, track) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get(`/tracks/${id}`, track)
          commit('TRACK_SUCCESS')
        } catch (err) {
          commit('TRACK_FAILURE')
          console.log('error updating track: ', err)
        }
      },
      async delete ({commit, state}, track) {
        try {
          let { data } = await api.delete(`/tracks/${track.id}`)
        } catch (e) {

        }
      }
    }
}

export default tracks
