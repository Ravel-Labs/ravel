<template>
    <b-navbar>
        <template slot="brand">
            <b-navbar-item class="has-text-weight-bold" tag="router-link" :to="{ path: '/' }">
              <p class="is-size-4">Ravel Labs</p>
            </b-navbar-item>
        </template>
        <template slot="start">
            <b-navbar-item v-if="token">
              <a href="#" router-link :to="{name: 'tracks'}">
                Tracks
              </a>
            </b-navbar-item>
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
                <div v-else>
                    <a href="/profile" class="button is-light">
                      <strong>Account</strong>
                    </a>
                    <a @click="logout()" class="button is-primary">
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
      ...mapState({
        user: state => state.auth.user,
        token: state => state.auth.token
      })
    },
    methods: {
      logout () {
        this.$store.dispatch('auth/logout')
        this.$router.push('/login')
      }
    }
}
</script>
