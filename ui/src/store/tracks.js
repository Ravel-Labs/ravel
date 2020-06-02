import API from '@/api'

const tracks = {
    namespaced: true,
    state: {
      list: [],
      current: {
        id: '',
        name: '',
        info: '',
        user_id: '',
        trackouts: [],
      },
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
      'GET_ONE_TRACK_SUCCESS' (state, track) {
        state.loading = false
        state.current = {
          id: track.payload.id,
          name: track.payload.name,
          info: track.payload.info,
          user_id: track.payload.user_id,
          trackouts: []
        }
      },
      'GET_TRACKOUTS' (state, trackID) {
        state.loading = true
      },
      'GET_TRACKOUTS_SUCCESS' (state, trackouts) {
        console.log('trackouts: ', trackouts)
        state.loading = false
        state.current.trackouts = trackouts
      },
      'GET_TRACKOUTS_FAILURE' (state, err) {
        state.loading = false
        state.error = err
      },
      'TRACK_FAILURE' (state) {
        state.loading = false
      },
      'TRACKOUT_REQUEST' (state) {
        state.loading = true
      },
      'TRACKOUT_SUCCESS' (state, trackout) {
        state.loading = false
        state.current = trackout
        state.error = ""
      },
      'TRACKOUT_FAILURE' (state, error) {
        state.error = error
        state.loading = false
      },
      'DELETE_TRACK_SUCCESS' (state, error) {

      }, 
      'DELETE_TRACK_FAILURE' (state, error) {
        state.error = error
        state.loading = false
      }
    },
    actions: {
      async create ({ commit, state }, track) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().post('/tracks', {
          	"name": track.name,
          	"user_id": track.user_id,
          	"artist": track.artist,
          	"info": track.info
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
      async getTrackDetails ({ commit, state }, id) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get(`/tracks/${id}`)
          commit('GET_ONE_TRACK_SUCCESS', data)
        } catch (err) {
          console.error(err)
          return err
        }
      },
      async getTrackouts({ commit, state }, trackID) {
        try {
          commit('GET_TRACKOUTS')
          let { data } = await API().get(`/trackouts`, {
            track_id: trackID
          })
          commit('GET_TRACKOUTS_SUCCESS', data.payload)
        } catch (err) {
          commit('GET_TRACKOUTS_FAILURE', err)
          console.error(err)
          throw err
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
          commit('DELETE_TRACK_SUCCESS')
        } catch (err) {
          commit('DELETE_TRACK_FAILURE', err)
          console.error('failed to delete track')
        }
      }
    }
}

export default tracks
