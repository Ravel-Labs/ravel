<template>
  <div id="app">
    <Navbar user="user"
      isAuthenticated="isAuthenticated"
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
  created () {
    const t = this.$cookies.get('token')
    console.log(t)
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
