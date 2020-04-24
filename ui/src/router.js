import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import About from './views/About.vue'
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
          path: '/about',
          name: 'about',
          component: About
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
          path: '/profile',
          name: 'profile',
          // component: Profile,
          meta: {
            requireAuth: true
          }
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
  const authtoken = store.getters['auth/token']
  if (to.name === 'login') {
    if (authtoken) {
      router.push('tracks')
    }
  }
  if (to.meta.requireAuth) {
    if (!authtoken) {
      console.log('no auth token')
      router.push('login')
    }
  }

  store.dispatch('auth/check', router)
  return next()
})

export default router
