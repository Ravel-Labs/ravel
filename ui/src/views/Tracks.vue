<template id="projects">
  <section class="section">
    <CreateTrack v-if="showModal"></CreateTrack>
    <div class="container">
      <nav class="panel">
        <p class="panel-heading">
            Tracks
        </p>
        <!-- <div class="panel-block">
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

        <!-- <div class="panel-block">
          <button class="button is-link is-outlined is-fullwidth">
            Reset all filters
          </button>
        </div> -->
      </nav>
      <b-button type="is-primary" outlined @click="toggle()">Create a track</b-button>
    </div>
  </section>
</template>
<script>
import { mapActions, mapState } from 'vuex'
import CreateTrack from '@/components/CreateTrack'

export default {
  data () {
    return {
      showModal: true,
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
  },
  methods: {
    ...mapActions(['tracks/create']),

    toggle () {
    }
  }
}
</script>
