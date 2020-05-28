<template>
  <section class="section">
    <b-loading
      :is-full-page="true"
      :active.sync="isLoading">
    </b-loading>
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
              <article @keyup.enter="login(user)" class="tile is-child notification is-primary">
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
                  <button class="button is-medium"
                  @click="login(user)">Login</button>
                </div>
              </article>
              <div class="field level-item">
              <a href="/signup">Don't have an account? Register here.</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import router from '@/router'

export default {
  name: "login",
  data: () => ({
    user: {
      email: "",
      password: ""
    },
  }),
  computed: mapState({
    isLoading: state => state.auth.loading,
    error: state => state.auth.error,
    showError: state => !!(state.auth.error),
  }),
  methods: {
    login (user) {
      this.$store.dispatch('auth/login', user)
      .then((data) => {
        this.$buefy.toast.open({
          message: 'Logged in.',
          type: 'is-success'
        })
      })
    }
  }
};
</script>