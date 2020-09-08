<template>
  <section class="section">
    <div class="container" v-if="!loading">
      <div class="trackouts container">
        <!-- Header -->
        <div class="columns">
          <div class="column">
            <h1 class="title is-1">{{ track.name }}</h1>
            <p class="subtitle">{{ track.info }}</p>
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
            <b-switch v-model="isReverbed">
              Reverb
            </b-switch>
            <b-switch v-model="isEQed">
              EQ
            </b-switch>
            <b-switch v-model="isCompressed">
              Compression
            </b-switch>
          </div>
        </div>

        <!-- If Empty Trackouts -->
        <div class="tile is-ancestor" v-if="track.trackouts.length == 0">
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

              <b-field label="Track Type">
                <b-select v-model="trackout.type" placeholder="What type of track is this?">
                  <option v-for="option in trackTypes" :value="option.name" :key="option.id">
                    {{ option.name }}
                  </option>
                </b-select>
              </b-field>

              <b-field class="file" v-if="!loading">
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
            <b-skeleton size="is-large" :active="loading"></b-skeleton>
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
            <button class="button is-danger is-small" @click="handleDeleteTrackOut(t.id)">Remove Trackout</button>
          </div>
        </b-collapse>
        <br />
        <div class="container columns toolbar">
          <div class="column">
            <button class="button is-danger is-small" @click="handleDeleteTrack()">Delete Track</button>
          </div>
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
      isReverbed: localStorage.getItem(`${this.$route.params.id}:settings:re`) || false,
      dropFiles: [],
      addTrackout: false,
      trackout: {
        name: "",
        type: ""
      },
      trackTypes: [
        {
          id: 1,
          type: "full_track",
          name: "full track"
        },
        {
          id: 2,
          type: "vocals",
          name: "vocals"
        },
        {
          id: 3,
          type: "drums",
          name: "drums"
        },
        {
          id: 4,
          type: "piano",
          name: "piano"
        },
        {
          id: 5,
          type: "guitar",
          name: "guitar"
        },
        {
          id: 6,
          type: "bass",
          name: "bass"
        },
        {
          id: 7,
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
      loading: state => state.tracks.loading,
      track: state => state.tracks.current,
      token: state => state.auth.token,
      user: state => state.user
    })
  },
  watch: {
    isCompressed: function(val) {
      localStorage.setItem(`${this.$route.params.id}:settings:co`, val);
    },
    isEQed: function(val) {
      localStorage.setItem(`${this.$route.params.id}:settings:eq`, val);
    },
    isDeessed: function(val) {
      localStorage.setItem(`${this.$route.params.id}:settings:de`, val);
    },
    isReverbed: function(val) {
      localStorage.setItem(`${this.$route.params.id}:settings:re`, val);
    }
  },
  methods: {
    submitFile() {
      let formData = new FormData();
      formData.append("file", this.file);

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

      // show a loading screen
      const loadingComponent = this.$buefy.loading.open({
        container: null
      });

      // hide add trackout modal
      this.toggleAddTrackout = false
      this.$store
        .dispatch("tracks/createTrackoutWithoutWav", trackPayload)
        .then(data => {
          // reset trackout form data
          this.trackout = { name: "", type: "" };

          // try to upload trackout to recently created track
          this.$store
            .dispatch("tracks/updateTrackoutWithWav", {
              id: data.payload.id,
              formData: formData
            })
            .then(data => {
              loadingComponent.close();
              this.$store.dispatch("tracks/getTrackouts", this.$route.params.id);
              this.addTrackout = false;
              this.$buefy.notification.open({
                message: "Uploaded trackout!",
                type: "is-success"
              });
            });
        })
        .catch(err => {
          loadingComponent.close();
          console.log("error creating trackout: ", err);
          return err;
        });
    },
    deleteDropFile(index) {
      this.dropFiles.splice(index, 1);
    },
    toggleAddTrackout() {
      this.addTrackout = !this.addTrackout;
    },
    process() {
      this.$store.dispatch("tracks/process", {
        trackID: this.$route.params.id,
        co: !!this.isCompressed,
        eq: !!this.isEQed,
        de: false, // NB: currently broken, so always send false
        re: !!this.isReverbed
      });
      this.$buefy.notification.open({
        message: "Process request received. Once your track is done processing we'll send you an email with a download link.",
        type: "is-success",
        duration: 5000
      });
    },
    handleDeleteTrackOut(id) {
      this.$store.dispatch("tracks/deleteTrackout", id);
    },
    handleDeleteTrack() {
      this.$store.dispatch("tracks/delete", {
        id: this.$route.params.id
      });
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
.toolbar {
  margin: 5px;
}
</style>
