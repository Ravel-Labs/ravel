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
  }),
  created () {
    this.$store.dispatch('auth/check')
    .then((data) => {
      console.log('app.vue data: ', data)
    })
    .catch((err) => console.error('error auth check:', err))
  }
}
</script>
