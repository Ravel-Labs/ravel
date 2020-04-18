import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Login from './views/Login.vue'
import Signup from './views/Signup.vue'
import Tracks from './views/Tracks.vue'
import store from './store'

Vue.use(Router)

const router = new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [{
            path: '/',
            name: 'home',
            component: Home
        },
        {
            path: '/login',
            name: 'login',
            component: Login,
        },
        {
            path: '/signup',
            name: 'signup',
            component: Signup,
        },
        {
            path: '/tracks',
            name: 'tracks',
            component: Tracks,
            meta: {
              requireAuth: true
            }
        }
    ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.requireAuth) {
    if (store.getters['auth/token'] == "") {
      router.push('login')
    }

  }

  console.log("to: ", to)
  console.log("from: ", from)
  next()
})

export default router
