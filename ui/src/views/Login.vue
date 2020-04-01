<template>
  <section class="section">
    <div class="level">
      <div class="tile container level-item">
        <div class="tile is-vertical is-6">
        <h1 class="is-size-2 has-text-centered">Login</h1>
          <div class="tile">
            <div class="tile is-parent is-vertical">
              <article class="tile is-child notification is-primary">
                <div class="field">
                  <label class="label has-text-white">Email</label>
                  <div class="control">
                    <input class="input" v-model="user.username" type="text" placeholder="email">
                  </div>
                </div>
                <div class="field">
                  <label class="label has-text-white">Password</label>
                  <div class="control">
                    <input class="input" v-model="user.password" type="password" placeholder="password">
                  </div>
                </div>

                <div class="field level-item">
                  <button class="button is-medium" @click="submit()">Login</button>
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: "home",
  data: () => ({
    user: {
      username: "",
      password: "",
    }
  }),
  created() {
    // fetch("http://localhost:8000")
    //   .then(res => res.json())
    //   .then(response => {
    //     this.quotes = response.quotes;
    //   })
    //   .catch(e => {
    //     console.error(e.message);
    //   });
  }
};
</script>


<style  scoped>
</style>
