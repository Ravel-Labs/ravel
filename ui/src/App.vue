<template>
  <div id="app">
    <Navbar
      user="user"
    ></Navbar>
    <router-view />
  </div>
</template>
<script>
import { mapState } from 'vuex'
import Navbar from '@/components/Navbar.vue'

export default {
  name: "home",
  components: {
    Navbar,
  },
  computed: mapState({
    user: state => state.user,
    isAuthenticated: state => state.user.isAuthenticated
  }),
  created () {
    this.$store.dispatch('auth/check')
  }
}
</script>
