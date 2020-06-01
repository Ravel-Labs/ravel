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
      'SET_ERROR' (state, error) {
        state.error = error
      },
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
      'DELETE_TRACK_SUCCESS' (state, data) {
        state.loading = false
      }, 
      'DELETE_TRACK_FAILURE' (state, error) {
        state.error = error
        state.loading = false
      },
      'UPLOAD_WAV_REQUEST' (state, data) {
        state.loading = true 
        state.error = ""
      },
      'UPLOAD_WAV_SUCCESS' (state, data) {

      },
      'UPLOAD_WAV_FAILURE' (state, error) {

      },
      'PROCESS_REQUEST' (state, data) {

      },
      'PROCESS_FAILURE' (state, error) {

      },
      'PROCESS_SUCCESS' (state, data) {

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
          commit('SET_ERROR', err)
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
      async getTrackouts ({ commit, state }, id) {
        try {
          commit('GET_TRACKOUTS')
          let { data } = await API().get(`/trackouts`, {
            track_id: id 
          })
          commit('GET_TRACKOUTS_SUCCESS', data.payload)
        } catch (err) {
          commit('GET_TRACKOUTS_FAILURE', err)
          console.error(err)
          throw err
        }
      },
      async update ({ commit, state}, track) {
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
          let { data } = await API().delete(`/tracks/${track.id}`)
          commit('DELETE_TRACK_SUCCESS')
        } catch (err) {
          commit('DELETE_TRACK_FAILURE', err)
          console.error('failed to delete track')
        }
      },
      async uploadFile ({ commit, state }, formData) {
        axios.post(`/trackouts/wav/${id}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        .then((data) => {
          console.log('upload file response: ', data)
          commit('UPLOAD_WAV_SUCCESS')
        })
        .catch((err) => {
          console.log('failed to upload file: ', err)
        })
      },
      async process ({ commit, state }, id, settings) {
        try {
          let { data } = API().put(`/tracks/${id}/process`)
          commit('PROCESS_SUCCESS', data)
        } catch (err) {
          console.error('error processing track: ', err)
        }
      }
    }
}

export default tracks
