<template id="projects">
  <section class="section">
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
        <a class="panel-block is-active">
          <span class="panel-icon">
            <i class="fas fa-book" aria-hidden="true"></i>
          </span>
          Project X
        </a>
        <!-- <div class="panel-block">
          <button class="button is-link is-outlined is-fullwidth">
            Reset all filters
          </button>
        </div> -->
      </nav>
    </div>
  </section>
</template>
<script>
import { mapActions } from 'vuex'

export default {
  data () {
    return {
      valid: false,
      track: {}
    }
  },
  created () {
    this['tracks/get']
  },
  computed: {
    ...mapState({
      tracks: state => state.tracks.list,
      user: state => state.auth.user
    })
  },
  methods: {
    ...mapActions(['tracks/create'])
  }
}
</script>
