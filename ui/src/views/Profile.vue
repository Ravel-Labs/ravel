<template id="">
  <div class="container has-text-centered">
    <b-loading :is-full-page="true" v-model="loading" :can-cancel="true"></b-loading>
    <div class="profile">
      <div class="level">
        <div class="tile is-child is-2 level-item">
          <article class="tile is-child notification is-info">
          <div class="fa fa-user fa-3x"></div>
            <p class="title is-4">{{ user.email }}</p>
            <p>{{ user.name }}</p>
            <p>Member Since: {{ user.created_at }}</p>
            <p>Ravel Beta Membership: {{ active}} </p>
          </article>
        </div>
      </div>

      <button class="button is-danger" @click="confirmDelete()">Delete Account</button>
    </div>
  </div>
</template>
<script>
import { mapState } from "vuex";

export default {
  name: "Profile",
  data() {
    return {
      deleteModal: false,
      active: "Active",
      loading: true
    };
  },
  computed: {
    ...mapState({
      user: state => state.auth.user,
      // loading: state => state.auth.loading
    })
  },
  created () {
    this.$store.dispatch('auth/profile')
  },
  methods: {
    confirmDelete() {
      this.$buefy.dialog.confirm({
        title: "Deleting account",
        message: "Are you sure you want to <b>delete</b> your account? This action cannot be undone.",
        confirmText: "Delete Account",
        type: "is-danger",
        hasIcon: true,
        onConfirm: () => {
          this.handleDelete()
        }
      });
    },
    openDeleteModal() {
      this.deleteModal == !this.deleteModal;
    },
    handleDelete() {
      console.log(this.user.id)
      return this.$store
        .dispatch("auth/delete", this.user.id)
        .then(data => {
          this.$buefy.toast.open("Account deleted!")
          this.$store.dispatch('auth/logout')
          console.log("successfully deleted account: ", data);
        })
        .catch(err => {
          this.$buefy.toast.open("Error deleting acount. Contact us for further support.")
          console.log("error deleting account: ", err);
        });
    }
  }
};
</script>
<style>
.profile {
  margin: 20px;
}
</style>