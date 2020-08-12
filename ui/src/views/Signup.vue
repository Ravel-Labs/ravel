<template>
  <section class="section">
    <div class="level">
      <div class="tile container level-item">
        <div class="tile is-vertical is-6">
        <h1 class="is-size-2 has-text-centered">Signup</h1>
          <div class="tile">
            <div class="tile is-parent is-vertical">
              <article @keyup.enter="handleSignup(user)" class="tile is-child notification is-primary">
                <div class="field">
                  <label class="label has-text-white">Name</label>
                  <div class="control">
                    <input class="input" v-model="user.name" type="text" placeholder="name">
                  </div>
                </div>
                <div class="field">
                  <label class="label has-text-white">Email</label>
                  <div class="control">
                    <input class="input" v-model="user.email" type="text" placeholder="email">
                  </div>
                </div>
                <div class="field">
                  <label class="label has-text-white">Password</label>
                  <div class="control">
                    <input class="input" v-model="user.password" type="password" placeholder="password">
                  </div>
                </div>
                <div class="field level-item">
                  <button class="button is-medium" @click="handleSignup(user)">Sign up</button>
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
<script>
import { mapActions } from 'vuex'
import router from '@/router'

export default {
  data () {
    return {
      user: {
        email: "",
        password: "",
        name: ""
      }
    }
  },
  methods: {
    handleSignup(user) {
      this.$store.dispatch('auth/signup', user)
      .then((data) => {
        this.$buefy.toast.open({
          message: 'You\'re ready to go!',
          type: 'is-success'
        }) 
        return data
      })
      .then((data) => {
        this.$store.dispatch('auth/login', {
          email: user.email,
          password: user.password,
        })
        .then((data) => {
          this.$buefy.toast.open({
            message: `Success! You've been signed up.`,
            type: 'is-success'
          })
          this.user.email = undefined
          this.user.password = undefined
          this.user.name = undefined
          // HACK: force a refresh of the page to update the API instance with localstorage.
          window.location.href = "/tracks"
          return data
        })
      })
      .catch((err) => {
        console.error('ERRSIGNUP:', err)
        this.$buefy.toast.open({
          message: `Something went wrong: ${err}`,
          type: 'is-danger'
        })
        this.user.email = undefined
        this.user.password = undefined
        this.user.name = undefined
        return err
      })
    },
  }
}
</script>
