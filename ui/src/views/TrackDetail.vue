<template>
  <section class="section">
    <div class="container">
      <div class="trackouts container">
        <div class="columns">
          <div class="column">
            <h1 class="title is-1">{{ trackDetail.name }}</h1>
            <p>{{ trackDetail.info }}</p>
          </div>
        </div>
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
    <section>
      <code>
        {{ trackDetail }}
      </code>
    </section>
  </section>
</template>
<script>
import { mapState } from 'vuex'

export default {
  name: 'trackDetails',
  data () {
    return {
      file: '',
      dropFiles: [],
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
    this.$store.dispatch('tracks/getTrackDetails', this.$route.params.id)
    this.$store.dispatch('tracks/getTrackouts', this.$route.params.id)
  },
  computed: {
    ...mapState({
      trackDetail: state => state.tracks.current,
      trackouts: state => state.tracks.current.trackouts
    })
  },
  methods: {
    handleFileUpload () {
      console.log('upload hit')
      this.file = this.$refs.file.files[0]
      let formData = new FormData() 
      formData.append('file', this.file)
      this.$store.dispatch('tracks/uploadFile', formData)
        .then((data) => {
          console.log('dispatch upload response: ', data)
        })
        .catch((err) => console.error('error uploading: ', err))
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
