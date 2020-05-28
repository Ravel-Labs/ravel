<template>
  <section class="section">
    <div class="container padded">
      <p class="is-size-1">Create Track</p>
      <div class="columns is-desktop">
        <div class="column is-half">
          <b-field label="Track Name">
            <b-input v-model="track.name"></b-input>
          </b-field>

          <b-field label="Artist">
            <b-input v-model="track.artist"></b-input>
          </b-field>

          <b-field label="Info">
            <b-input v-model="track.info"></b-input>
          </b-field>
          <button class="button is-large is-primary" @click="create()">Create</button>
        </div>
        <div class="">
        </div>
      </div>
    </div>
  </section>
</template>
<script>
import { mapState } from 'vuex'
import router from '@/router'

export default {
  name: 'createTrack',
  data () {
    return {
      track: {
        name: '',
        info: '',
        artist: ''
      }
    }
  },
  computed: {
    ...mapState({
      user: state => state.auth.user
    })
  },
  methods: {
    create () {
      const track = {
        name: this.track.name,
        artist: this.track.artist,
        info: this.track.info,
      }
      this.$store.dispatch('tracks/create', track)
      .then(() => {
        router.push({ path: '/tracks' })
        this.$buefy.notification.open({
          message: 'Track created!',
          type: 'is-success'
        })
        this.$store.dispatch('tracks/get')
      })
    }
  }
}
</script>
<style media="screen">

</style>
