<template>
  <section class="section">
    <div class="container">
      <div class="trackouts container">
        <!-- Header -->
        <div class="columns">
          <div class="column">
            <h1 class="title is-1">{{ track.name }}</h1>
            <p class="subtitle">{{ track.info }}</p>
          </div>
        </div>

        <!-- If Empty Trackouts -->
        <div class="tile is-ancestor" v-if="!track.trackouts">
          <div class="tile is-vertical">
            <div class="tile">
              <div class="tile is-parent is-vertical">
                <article class="tile is-child notification is-primary is-vcentered">
                  <p>You haven't created a trackout yet. Create one to get started!</p>
                  <p>
                    <b-button class="is-info" @click="toggleAddTrackout()">Create Trackout</b-button>
                  </p>
                </article>
              </div>
            </div>
          </div>
        </div>

        <div class="columns">
          <b-button class="is-info" @click="toggleAddTrackout()">
            Add Trackout
          </b-button>
        </div>

        <!-- Add Trackout Modal -->
        <div class="modal" v-bind:class="{ 'is-active': addTrackout }">
          <div @click="toggleAddTrackout()" class="modal-background"></div>
          <div class="modal-card">
            <header class="modal-card-head">
              <p class="modal-card-title">Add Trackout</p>
              <button class="delete" @click="toggleAddTrackout()" aria-label="close"></button>
            </header>
            <section class="modal-card-body">
              <b-field label="Name">
                <b-input v-model="trackout.name"></b-input>
              </b-field>

              <b-field label="Type">
                <b-input v-model="trackout.type"></b-input>
              </b-field>

              <b-field class="file">
                <b-upload v-model="file">
                  <a class="button is-primary">
                    <b-icon class="fa fa-arrow-up"></b-icon>
                    <span>Click to select a trackout</span>
                  </a>
                </b-upload>
                <span class="file-name" v-if="file">
                  {{ file.name }}
                </span>
              </b-field>

              <code>
                {{ file }}
              </code>
            </section>
            <footer class="modal-card-foot">
              <button class="button is-primary" @click="submitFile()">Upload</button>
              <button class="button">Cancel</button>
            </footer>
          </div>
        </div>

        <!-- Edit Trackout Modal -->
        <!-- TODO -->

        <!-- Trackouts List -->
        <b-collapse v-for="t in track.trackouts" :key="t.id" class="card" animation="slide">
          <div slot="trigger" slot-scope="props" class="card-header" role="button" aria-controls="contentIdForA11y3">
            <p class="card-header-title">
              {{ t.name }}
            </p>
            <a class="card-header-icon">
              <b-icon :icon="props.open ? 'menu-down' : 'menu-up'"> </b-icon>
            </a>
          </div>
          <div class="card-content">
            <p>Created at: {{ t.created_at }}</p>
            <p>Type: {{ t.type }}</p>

            <!-- Manual settings
                  <!-- <b-field label="Compression">
                      <b-slider v-model="t.compression"></b-slider>
                  </b-field>

                  <b-field label="Reverb">
                      <b-slider v-model="t.reverb"></b-slider>
                  </b-field>

                  <b-field label="EQ">
                      <b-slider v-model="t.eq"></b-slider>
                  </b-field> -->

            <!-- Presets -->
            <!-- <div class="columns">
                    <div class="column">
                    <b-field>
                    </b-field>
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
                <br> -->
          </div>
        </b-collapse>
      </div>
    </div>
    <section></section>
  </section>
</template>
<script>
import { mapState } from "vuex";

export default {
  name: "trackDetails",
  data() {
    return {
      file: {
        name: ""
      },
      dropFiles: [],
      addTrackout: false,
      trackout: {
        name: "",
        type: ""
      },
      trackTypes: [
        {
          id: 1,
          type: "vocals",
          name: "vocals"
        },
        {
          id: 2,
          type: "drums",
          name: "drums"
        },
        {
          id: 3,
          type: "piano",
          name: "piano"
        },
        {
          id: 4,
          type: "guitar",
          name: "guitar"
        },
        {
          id: 5,
          type: "bass",
          name: "bass"
        },
        {
          id: 6,
          type: "synths / electronic",
          name: "synths / electronic"
        }
      ]
    };
  },
  created() {
    this.$store.dispatch("tracks/getTrackDetails", this.$route.params.id);
    this.$store.dispatch("tracks/getTrackouts", this.$route.params.id);
  },
  computed: {
    ...mapState({
      track: state => state.tracks.current,
      token: state => state.auth.token,
      user: state => state.user
    })
  },
  methods: {
    submitFile() {
      let formData = new FormData();
      const trackPayload = {
        user_id: 1,
        track_id: this.$route.params.id,
        name: this.trackout.name,
        type: this.trackout.type
      };
      const filePayload = {
        formData: formData,
        id: this.$route.params.id
      };
      // attempt track creation and upload to it.
      this.$store
        .dispatch("tracks/createTrackoutWithoutWav", trackPayload)
        .then(data => {
          this.$store.dispatch("tracks/updateTrackoutWithWav", filePayload).then(data => {
            // everything succeeded
            this.$store.dispatch("tracks/getTrackouts", this.$route.params.id);

            // fire notification and clean up
            this.addTrackout = false;
            this.$buefy.notification.open({
              message: "Uploaded trackout!",
              type: "is-success"
            });
          });
        })
        .catch(err => {
          console.log("error creating trackout: ", err);
        });
    },
    deleteDropFile(index) {
      this.dropFiles.splice(index, 1);
    },
    toggleAddTrackout() {
      console.log("addTrackout: ", this.addTrackout);
      this.addTrackout = !this.addTrackout;
      console.log("addTrackout after: ", this.addTrackout);
    }
  }
};
</script>
<style media="screen">
.upload-section {
  width: 100%;
}

.upload {
  margin-right: 0.5rem;
}

.upload-area {
  margin: 2rem;
}
</style>
