<template>
  <section class="section">
    <b-loading :is-full-page="true" :active.sync="isLoading" :can-cancel="true"></b-loading>
    <b-notification
        type="is-danger"
        v-if="error"
        :active.sync="showError"
        aria-close-label="Close notification">
        {{ error }}
    </b-notification>
    <div class="level">
      <div class="tile container level-item">
        <div class="tile is-vertical is-6">
        <h1 class="is-size-2 has-text-centered">Login</h1>
          <div class="tile">
            <div class="tile is-parent is-vertical">
              <article class="tile is-child notification is-primary">
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
                  <button class="button is-medium" @click="login(user)">Login</button>
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
import { mapActions, mapState } from 'vuex'

export default {
  name: "home",
  data: () => ({
    user: {
      email: "",
      password: ""
    },
  }),
  computed: mapState({
    isLoading: state => state.auth.loading,
    error: state => state.auth.error,
    showError: state => !!(state.auth.error)
  }),
  methods: {
    login (user) {
      this.$store.dispatch('auth/login', user)
      .then(() => {
        console.log('error: ', this.error)
        if (!this.error) {
          this.$router.push('/')
        }
      })
    }
  }
};
</script>

<style  scoped>
</style>
