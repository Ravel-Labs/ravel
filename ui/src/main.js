import Vue from 'vue'
import App from './App.vue'
import router from './router'

// Buefy imports
import Buefy from 'buefy'
import 'buefy/dist/buefy.css'
Vue.use(Buefy)

// Mount Buefy to Vue
Vue.config.productionTip = false

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
