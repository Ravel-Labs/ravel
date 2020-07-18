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
          <div class="column">
            <b-button class="is-info" @click="toggleAddTrackout()">
              Add Trackout
            </b-button>
            <b-button style="margin-left: 10px;" class="is-info" @click="process()">
              Process
            </b-button>
          </div>
          <div class="column" v-if="track.trackouts">
            <!-- Processing toggles -->
            <b-switch v-model="isDeessed">
              De-Esser
            </b-switch>
            <b-switch v-model="isEQed">
              EQ
            </b-switch>
            <b-switch v-model="isCompressed">
              Compression
            </b-switch>
          </div>
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
                <!-- This should be "vocals" or "instrument" types -->
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
            </section>
            <footer class="modal-card-foot">
              <button class="button is-primary" @click="submitFile()">Upload</button>
              <button class="button" @click="toggleAddTrackout()">Cancel</button>
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
            <button class="button is-danger is-small" @click="handleDeleteTrackOut()">Remove Trackout</button>
          </div>
        </b-collapse>

        <div>
          <button class="button is-danger is-small" @click="handleDeleteTrack()">Delete Track</button>
        </div>
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
      file: [],
      isDeessed: localStorage.getItem(`${this.$route.params.id}:settings:de`) || false,
      isEQed: localStorage.getItem(`${this.$route.params.id}:settings:eq`) || false,
      isCompressed: localStorage.getItem(`${this.$route.params.id}:settings:co`) || false,
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
  watch: {
    isCompressed: function(val) {
      localStorage.setItem(`${this.$route.params.id}:settings:co`, val)
    },
    isEQed: function(val) {
      localStorage.setItem(`${this.$route.params.id}:settings:eq`, val)
    },
    isDeessed: function(val) {
      localStorage.setItem(`${this.$route.params.id}:settings:de`, val)
    }
  },
  methods: {
    submitFile() {
      let formData = new FormData();
      console.log("processing file: ", this.file)
      formData.append('file', this.file)

      // set payloads up 
      const trackPayload = {
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
          this.$store.dispatch("tracks/updateTrackoutWithWav", filePayload)
            // TODO show a loading bar 
            .then(data => {
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
          return err
        });
    },
    deleteDropFile(index) {
      this.dropFiles.splice(index, 1);
    },
    toggleAddTrackout() {
      console.log("addTrackout: ", this.addTrackout);
      this.addTrackout = !this.addTrackout;
      console.log("addTrackout after: ", this.addTrackout);
    },
    process() {
      // TODO: add params to this processing request 
      this.$store.dispatch("tracks/process", this.$route.params.id);
    },
    handleDeleteTrack() {
      this.$store.dispatch('tracks/delete', {
        id: this.$route.params.id
      })
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
