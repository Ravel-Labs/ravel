<template>
  <section class="section">
    <div class="container">
      <div class="trackouts container">
        <div class="columns">
          <div class="column">
            <h1 class="title is-1">{{ track.name }}</h1>
            <p>{{ track.info }}</p>
          </div>
        </div>
        <!-- Each trackout has a set of details for it -->
        <b-collapse v-for="t in track.trackOuts"
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
                  {{ t.name }}
                </p>
                <a class="card-header-icon">
                    <b-icon
                        :icon="props.open ? 'menu-down' : 'menu-up'">
                    </b-icon>
                </a>
            </div>
            <div class="card-content">
                  <b-field label="Compression">
                      <b-slider v-model="t.compression"></b-slider>
                  </b-field>

                  <b-field label="Reverb">
                      <b-slider v-model="t.reverb"></b-slider>
                  </b-field>

                  <b-field label="EQ">
                      <b-slider v-model="t.eq"></b-slider>
                  </b-field>

                  <div class="columns">
                    <div class="column">
                      <b-switch v-model="t.vocal_magic">
                        Vocal Magic
                      </b-switch>
                    </div>
                    <div class="column">
                      <b-switch v-model="t.drum_booster">
                        Drum Booster
                      </b-switch>
                    </div>

                    <div class="column">
                      <b-switch v-model="t.deesser">
                          De-Esser
                      </b-switch>
                    </div>
                  </div>
                  <div class="columns">
                    <div class="column">
                    <b-field label="Track Type">
                        <b-select
                        placeholder="What instrument is this trackout?">
                            <option
                              v-for="option in trackTypes"
                              :value="option.name"
                              :key="option.id">
                              {{ option.name }}
                            </option>
                        </b-select>
                    </b-field>
                    </div>
                  </div>
                <br>
            </div>
        </b-collapse>
        <div class="container columns is-desktop is-mobile is-centered">
           <b-field class="file upload-area">
             <b-upload v-model="file" expanded>
               <a class="button is-medium is-primary is-fullwidth">
                 <i class="fas fa-upload upload" aria-hidden="true"></i>
                 <span>{{ file.name || "Click to upload a trackout"}}</span>
               </a>
             </b-upload>
           </b-field>
        </div>
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
      file: {},
      dropFiles: [],
      track: {
        trackOuts: [
          {
            id: 1,
            created_at: Date.now(),
            user_id: 1,
            name: 'vocals',
            type: 'vocals',
            wavefile: [],
            track_id: 1,
            compression: 15,
            reverb: 30,
            eq: 50,
            deesser: true,
            vocal_magic: true,
            drum_booster: false
          },
        {
            id: 2,
            created_at: Date.now(),
            user_id: 1,
            name: 'drums',
            type: 'drums',
            wavefile: [],
            track_id: 1,
            compression: 90,
            reverb: 20,
            eq: 50,
            deesser: true,
            vocal_magic: false,
            drum_booster: true
          }
        ],
        name: 'Neon Dreams',
        created_at: Date.now(),
        info: 'Recorded at SoundCity Studios'
      },
      trackTypes: [
        {
          id: 1,
          type: 'vocals',
          name: 'vocals'
        },
        {
          id: 2,
          type: 'drums',
          name: 'drums'
        },
        {
          id: 3,
          type: 'piano',
          name: 'piano'
        },
        {
          id: 4,
          type: 'guitar',
          name: 'guitar'
        },
        {
          id: 5,
          type: 'bass',
          name: 'bass'
        },
        {
          id: 6,
          type: 'synths / electronic',
          name: 'synths / electronic'
        },
      ]
    }
  },
  created () {
    // this.$store.dispatch('tracks')
  },
  computed: {
    // ...mapState({
    //   track: state => state.tracks.current,
    // })
  },
  methods: {
    upload () {
      console.log('upload hit')
    },
    deleteDropFile (index) {
      this.dropFiles.splice(index, 1);
    }
  }
}
</script>
<style media="screen">
  .upload-section {
    width: 100%;
  }
  .upload {
    margin-right: .5rem;
  }
  .upload-area {
    margin: 2rem;
  }
</style>
