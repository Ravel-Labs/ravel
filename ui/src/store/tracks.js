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
      'WAVEFILE_REQUEST' (state, data) {
        console.log('wavefile request: ', data)
      },
      'WAVEFILE_FAILURE' (state, err) {
        console.log('wavefile failure: ', err)
        state.error = err
      },
      'WAVEFILE_SUCCESS' (state, data) {
        console.log('wavefile success: ', data)
        state.message = data
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
          console.log('getTrackouts: ', data)
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
          console.log('add trackout: ', data)
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
          console.log('removing track:', data)
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
          console.log('delete trackout response data: ', data)
          return data
        } catch (err) {
          console.error('error deleting trackout: ', err)
          return err
        }
      },
      async process ({ commit }, trackID) {
        try {
          commit('PROCESS_REQUEST', trackID)
          let { data } = await API().put(`/tracks/process/${trackID}`, {
            'toggle_effects_params': {
              'co': true,
              'eq': true,
              'de': true
            }
          })
          console.log('process request data: ', data)
          if (data.status === "200") {
            commit('TRACK_SUCCESS', `Processing! You should be receiving an email with a download link shortly.`)
            return data
          }

          console.log('got past success: ', data)
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
      async uploadFile ({ commit }, payload) {
        try {
          let { data } = await api.post(`/trackouts/wav/${payload.id}`, payload.formData)
          if (data.status === "500") {
            commit('TRACK_FAILURE', `Failed to upload track: ${data.message}`)
            return data
          }

          // commit('UPLOAD_SUCCESS', data)
          return data
        } catch (err) {
          console.error('error uploading file: ', err)
          return Error(err)
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
          console.log('attempting to create trackout with payload: ', payload)
          let { data } = await API().post('/trackouts', payload)
          commit('ADD_TRACKOUT_SUCCESS', data)
        } catch (err) {
          console.error('FAILED to create trackout without wav: ', err)
          commit('ADD_TRACKOUT_FAILURE', err)
        }
      },
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
        } catch (err) {
          console.error('wav upload failed: ', err)
          return err
        }
      }
    }
}

export default tracks
