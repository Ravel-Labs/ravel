import vue from 'vue'
import vuex from 'vuex'
import auth from '@/store/auth'
import tracks from '@/store/tracks'

vue.use(vuex)

export default new vuex.Store({
  modules: {
    auth,
    tracks
  }
})
