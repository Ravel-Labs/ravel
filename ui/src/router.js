import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import NewQuote from "./views/NewQuote.vue"
import Login from "./views/Login.vue"
import Signup from "./views/Signup.vue"
import Tracks from "./views/Tracks.vue"

Vue.use(Router)

export default new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [{
            path: '/',
            name: 'home',
            component: Home
        },
        {
            path: '/new',
            name: 'new-quote',
            component: NewQuote
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
        }
    ]
})
