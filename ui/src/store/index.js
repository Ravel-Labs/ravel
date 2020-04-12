import vue from 'vue'
import vuex from 'vuex'
import auth from '@/store/auth'

vue.use(vuex)

export default new vuex.Store({
  modules: {
    auth
  }
})
