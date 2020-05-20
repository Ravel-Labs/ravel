<template>
  <div id="app">
    <Navbar
      user="user"
    ></Navbar>
    <router-view :key="$route.fullPath" />
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
  })
}
</script>
<style lang="scss" media="screen">
// Import Bulma's core
@import "~bulma/sass/utilities/_all";

// Set your colors
$primary: #753a88;
$primary-invert: findColorInvert($primary);
$twitter: #cc2b5e;
$twitter-invert: findColorInvert($twitter);

// Setup $colors to use as bulma classes (e.g. 'is-twitter')
$colors: (
    "white": ($white, $black),
    "black": ($black, $white),
    "light": ($light, $light-invert),
    "dark": ($dark, $dark-invert),
    "primary": ($primary, $primary-invert),
    "info": ($info, $info-invert),
    "success": ($success, $success-invert),
    "warning": ($warning, $warning-invert),
    "danger": ($danger, $danger-invert),
    "twitter": ($twitter, $twitter-invert)
);

// Links
$link: $primary;
$link-invert: $primary-invert;
$link-focus-border: $primary;

// Import Bulma and Buefy styles
@import "~bulma";
@import "~buefy/src/scss/buefy";

</style>
