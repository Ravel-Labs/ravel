<template>
  <section class="section">
    <div class="container">
      <p>{{ name }}</p>

      <div class="trackouts container">

        <!-- Each trackout has a set of details for it -->
        <b-collapse v-for="t in trackouts"
          :key="t.id"
          class="card"
          animation="slide">
            <div
                slot="trigger"
                slot-scope="props"
                class="card-header"
                role="button"
                aria-controls="contentIdForA11y3">
                <p class="card-header-title">
                  trackout name
                </p>
                <a class="card-header-icon">
                    <b-icon
                        :icon="props.open ? 'menu-down' : 'menu-up'">
                    </b-icon>
                </a>
            </div>
            <div class="card-content">
                <div class="content">
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec iaculis mauris.
                    <a>#buefy</a>.
                </div>
            </div>
            <footer class="card-footer">
                <a class="card-footer-item">Save</a>
                <a class="card-footer-item">Edit</a>
                <a class="card-footer-item">Delete</a>
            </footer>
        </b-collapse>

      </div>
    </div>
  </section>
</template>
<script>
import { mapState } from 'vuex'

export default {
  name: 'trackDetails',
  data () {
    return {
      trackouts: [{
        id: 1,
        name: 'test track out',
        instrument: 'guitar'
      }]
    }
  },
  computed: {
    ...mapState({
      track: state => state.tracks.current
    })
  },
  methods: {
    upload () {
      console.log('upload hit')
    }
  }
}
</script>
