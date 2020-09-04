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
      loading: false,
      processing: false
    },
    mutations: {
      'TRACK_REQUEST' (state) {
        state.loading = true
      },
      'TRACK_SUCCESS' (state, tracks) {
        if  (!tracks) {
          // handle empty case
          state.list = []
        } else {
          // happy path 
          state.list = tracks
        }
        state.loading = false
        state.error = undefined
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
      'GET_TRACKOUTS' (state) {
        state.loading = true
      },
      'GET_TRACKOUTS_SUCCESS' (state, trackouts) {
        state.loading = false
        if (trackouts == undefined) {
          state.current.trackouts = []
          return
        }
        if (trackouts.length === 0) {
          state.current.trackouts = []
          return
        } 

        state.current.trackouts = trackouts
      },
      'GET_TRACKOUTS_FAILURE' (state, err) {
        state.loading = false
        state.error = err
      },
      'TRACK_FAILURE' (state, error) {
        state.loading = false
        state.error = error
      },
      'TRACKOUT_REQUEST' (state) {
        state.loading = true
      },
      'TRACKOUT_SUCCESS' (state, trackout) {
        state.loading = false
        state.current = trackout
        state.error = undefined
      },
      'ADD_TRACKOUT_SUCCESS' (state, trackout) {
        state.loading = false
        state.error = undefined
        state.current.trackouts.push(trackout)
      },
      'ADD_TRACKOUT_FAILURE' (state, error) {
        state.error = error
        state.loading = false
      },
      'DELETE_TRACKOUT_REQUEST' (state) {
        state.error = ""
        state.loading = true
      },
      'DELETE_TRACKOUT_SUCCESS' (state, data) {
        state.loading = false
      },
      'DELETE_TRACKOUT_FAILURE' (state, err) {
        state.loading = false
        state.error = err
      },
      'DELETE_TRACK_SUCCESS' (state, i) {
        state.loading = false
        state.error = undefined
        state.list.splice(1, i)
      }, 
      'DELETE_TRACK_FAILURE' (state, error) {
        state.error = error
        state.loading = false
      },
      'UPDATE_TRACKOUT_WAV_SUCCESS' (state, data) {
        state.error = ""
        state.loading = false
        console.log('update trackout wav success: ', data)
      },
      'TRACK_PROCESS_REQUEST' (state, data) {
        state.error = ""
        console.log('track_process_request data: ', data)
      },
      'PROCESS_REQUEST' (state, data) {
        console.log('process request kicked off')
        state.processing = true
        state.loading = false
      },
      'PROCESS_SUCCESS' (state, data) {
        state.processing = false
        state.message = "Successfully processed. Check your email."
        state.loading = false
      }
    },
    actions: {
      async create ({ commit }, track) {
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
      async get ({ commit }) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get('/tracks')
          commit('TRACK_SUCCESS', data.payload)
        } catch (err) {
          console.log('error getting tracks: ', err)
          return err
        }
      },
      async getTrackDetails ({ commit }, id) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get(`/tracks/${id}`)
          commit('GET_ONE_TRACK_SUCCESS', data)
        } catch (err) {
          console.error(err)
          return err
        }
      },
      async getTrackouts({ commit }, trackID) {
        try {
          commit('GET_TRACKOUTS')
          let { data } = await API().get(`/trackouts`, { params: {
              track_id: trackID
            }
          })
          if (data.message == "500 Internal Server Error: 400 Bad Request: No trackouts have been created yet") {
            commit('GET_TRACKOUTS_SUCCESS', [])
            return []
          }
          commit('GET_TRACKOUTS_SUCCESS', data.payload)
        } catch (err) {
          commit('GET_TRACKOUTS_FAILURE', err)
          console.error(err)
          return err
        }
      },
      async addTrackout({ commit }, trackout) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().post('/trackouts', trackout)
          commit('ADD_TRACKOUT_SUCCESS', data.payload)
        } catch (err) {
          console.error('error adding trackout: ', err)
          return new Error('error processing trackout: ', err)
        }
      },
      async update({ commit }, track) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get(`/tracks/${id}`, track)
          commit('TRACK_SUCCESS')
        } catch (err) {
          commit('TRACK_FAILURE')
          console.log('error updating track: ', err)
        }
      },
      async delete ({ commit, dispatch }, track) {
        try {
          let { data } = await API().delete(`/tracks/delete/${track.id}`)
          if (data.payload) {
            commit('DELETE_TRACK_SUCCESS')
            router.push('/tracks')
            dispatch('get')
            return data
          }

          if (data.message) {
            if (data.status === "500") {
              commit('DELETE_TRACK_FAILURE', data.message)
              return new Error(data.message)
            }
          }

          console.log('data.payload: ', data.payload)
          return data
        } catch (err) {
          commit('DELETE_TRACK_FAILURE', err)
          console.error('failed to delete track: ', err)
          return err
        }
      },
      async deleteTrackout ({ commit }, trackoutID) {
        try {
          let { data } = await API().delete(`/trackouts/delete/${trackoutID}`)
          return data
        } catch (err) {
          console.error('error deleting trackout: ', err)
          return err
        }
      },
      async process ({ commit }, payload) {
        try {
          commit('PROCESS_REQUEST', payload.trackID)
          let { data } = await API().put(`/tracks/process/${payload.trackID}`, {
            'toggle_effects_params': {
              'co': payload.co,
              'eq': payload.eq,
              'de': payload.de 
            }
          })
          return data
        } catch (err) {
          console.log('error processing track: ', err)
          commit('TRACK_FAILURE', err)
          return err
        }
      },

      async getWavefile ({ commit }, trackID) {
        try {
         let { data } = await API().get(`/tracks/wav/${trackID}`)
         console.log('got wavfile response: ', data)
         return data
        } catch (err) {
          console.log('error getting wavefile: ', err) 
          return err
        }
      },
      async createTrackoutWithoutWav ({ commit }, trackout) {
        try {
          let payload = {
            user_id : trackout.user_id,
            name : trackout.name,
            type : trackout.type,
            wavefile : trackout.wavefile,
            track_id : trackout.track_id
          }
          let { data } = await API().post('/trackouts', payload)
          commit('ADD_TRACKOUT_SUCCESS', data)
          return Promise.resolve(data) 
        } catch (err) {
          console.error('FAILED to create trackout without wav: ', err)
          commit('ADD_TRACKOUT_FAILURE', err)
          return Promise.reject(err)
        }
      },
      // updateTrackoutWithWav takes a payload of `{ id: <id>, formData: {}}`
      async updateTrackoutWithWav ({ commit }, payload) {
        try {
          let { data } = await API().put(`/trackouts/wav/${payload.id}`,
            payload.formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            } 
          )
          console.log('uploaded successfully: ', data)
          commit('UPDATE_TRACKOUT_WAV_SUCCESS', data)
          return Promise.resolve(data)
        } catch (err) {
          console.error('wav upload failed: ', err)
          return Promise.resolve(err)
        }
      }
    }
}

export default tracks
