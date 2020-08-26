<template id="">
  <div class="container has-text-centered">
    <div>
      <h1 class="title is-4">Email: {{ user.email }}</h1>
      <h1 class="title is-4">Ravel Beta Program: {{ active }}</h1>
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
      active: "Active"
    };
  },
  computed: {
    ...mapState({
      user: state => state.auth.user
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
      return this.$store
        .dispatch("auth/delete", userID)
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
