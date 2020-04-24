<template>
    <b-navbar>
        <template slot="brand">
            <b-navbar-item class="has-text-weight-bold" tag="router-link" :to="{ path: '/' }">
              <p class="is-size-4">Ravel Labs</p>
            </b-navbar-item>
        </template>
        <template slot="start">
            <b-navbar-item href="/signup">
                Get Started
            </b-navbar-item>
            <b-navbar-dropdown label="Info">
                <b-navbar-item href="/about">
                    About
                </b-navbar-item>
            </b-navbar-dropdown>
        </template>

        <template slot="end">
            <b-navbar-item tag="div">
                <div v-if="!token" class="buttons">
                    <a href="/signup" class="button is-primary">
                        <strong>Sign up</strong>
                    </a>
                    <a class="button is-light" href="/login">
                        Log in
                    </a>
                </div>
                <div class="" v-else>
                    <a href="/profile" class="button is-light">
                      <strong>Account {{ user.email }}</strong>
                    </a>
                    <a @click="logoutUser()" class="button is-primary">
                        Log out
                    </a>
                </div>
            </b-navbar-item>
        </template>
    </b-navbar>
</template>
<script>
import { mapActions, mapState } from 'vuex'
import router from '@/router'

export default {
    name: 'Navbar',
    data () {
      return {}
    },
    computed: {
      ...mapActions('auth', [
        'logout'
      ]),
      ...mapState({
        user: state => state.auth.user,
        token: state => state.auth.token
      })
    },
    methods: {
      logout () {
        this.logout()
        .then(() => {
          router.push('/login')
        })
      }
    }
}
</script>
