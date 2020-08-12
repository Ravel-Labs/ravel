import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import About from './views/About.vue'
import TermsOfService from './views/TermsOfService.vue'
import Login from './views/Login.vue'
import Signup from './views/Signup.vue'
import Tracks from './views/Tracks.vue'
import CreateTrack from './views/CreateTrack.vue'
import TrackDetail from './views/TrackDetail.vue'
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
          path: '/termsofservice',
          name: 'termsofservice',
          component: TermsOfService 
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
        },
        {
          path: '/tracks/create',
          name: 'createTrack',
          component: CreateTrack,
          meta: {
            requireAuth: true
          }
        },
        {
          path: '/tracks/:id',
          name: 'trackDetail',
          component: TrackDetail,
          meta: {
            requireAuth: true
          }
        }
    ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.requireAuth) {
    // NB: Get the authtoken _after_ the requireAuth 
    // is checked or else there will be async issues.
    const authtoken = store.getters['auth/token']
    if (!authtoken) {
      console.error('ERRAUTHTOKEN: no auth token present - rerouting to login.')
      router.push('login')
    }
  }

  return next()
})

export default router