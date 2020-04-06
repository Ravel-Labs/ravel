import Vue from 'vue'
import Vuex from 'vuex'
import VueCookies from 'vue-cookies'
import App from './App.vue'
import router from './router'
import store from './store'

Vue.use(VueCookies)

// setup buefy
import Buefy from 'buefy'
import 'buefy/dist/buefy.css'
Vue.use(Buefy)

// Mount Buefy to Vue
Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
