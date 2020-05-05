<template id="projects">
  <section class="section">
    <CreateTrack v-if="showModal"></CreateTrack>
    <div class="container">
      <nav class="panel">
        <p class="panel-heading">
            Tracks
        </p>
        <!-- ### TODO: Make this a simple filter by title ###
        <div class="panel-block">
          <p class="control has-icons-left">
            <input class="input" type="text" placeholder="Search">
            <span class="icon is-left">
              <i class="fas fa-search" aria-hidden="true"></i>
            </span>
          </p>
        </div> -->
        <a v-for="track in tracks" class="panel-block is-active">
          <span class="panel-icon">
            <i class="fas fa-book" aria-hidden="true"></i>
          </span>
          {{ track.name }}
        </a>
        <a v-if="tracks.length === 0" class="panel-block is-active">
          You haven't creatd any tracks yet. <a href="/tracks/create"> Make one now!</a>
        </a>

      </nav>
      <router-link :to="{ name: 'createTrack' }">
        <b-button
        type="is-primary"
        outlined>
          Create a track
        </b-button>
      </router-link>
    </div>
  </section>
</template>
<script>
import { mapActions, mapState } from 'vuex'
import CreateTrack from '@/components/CreateTrack'

export default {
  data () {
    return {
      showModal: false,
      error: '',
      showError: false,
      valid: false,
    }
  },
  components: {
    CreateTrack
  },
  created () {
    this.$store.dispatch('tracks/get')
  },
  computed: {
    ...mapState({
      tracks: state => state.tracks.list,
      user: state => state.auth.user
    })
  }
}
</script>
