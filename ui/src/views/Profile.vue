<template id="">
  <div class="container has-text-centered">
    <h1 class="title is-4">Email: {{ email }}</h1>
    <h1 class="title is-4">Ravel Beta Program: {{ active }}</h1>


    <button class="button is-danger" @click="handleDelete()">Danger</button>
</div>  
</template>
<script>
import { mapState } from 'vuex'

export default {
  name: 'Profile',
  data () {
    return {
      active: 'Active'
    }
  },
  computed: {
    ...mapState({
      email: state => state.auth.user.email
    })
  },
  methods: {
    handleDelete() {
      return this.$store.dispatch('auth/delete')
        .then((data) => {
          console.log('successfully deleted account: ', data)
        })
        .catch((err) => {
          console.log('error deleting account: ', err)
        })
    }
  }
}
</script>
