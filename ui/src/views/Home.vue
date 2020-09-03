<template>
  <div class="home">
    <div>
      <section class="section columns">
        <div class="column is-full">
          <section class="hero is-twitter is-bold is-large">
            <div class="hero-body">
              <div class="container">
                <h1 class="title is-1 has-text-centered">
                  Welcome to Ravel Labs
                </h1>
                <h2 class="subtitle is-3 has-text-centered">
                  The future of audio mixing and mastering.
                </h2>
                <h2 class="subtitle is-4 has-text-centered">
                  Sign up now for free and try it out yourself.
                </h2>
                <h2 class="has-text-centered">
                  <div class="level">
                    <div class="level-item">
                      <button class="button is-medium is-white"><b>Sign up now</b></button>
                    </div>
                  </div>
                  <div class="level">
                    <div class="level-item">Already a member? <a class="has-text-white" href="/login">Login here.</a></div>
                  </div>
                </h2>
              </div>
            </div>
          </section>
        </div>
      </section>
    </div>
    <footer class="footer">
      <div class="content has-text-centered">
        <div class="level">
          <div class="level-item">
            <img class="logo" src="../assets/logo.png" alt="" />
          </div>
        </div>
        <p><strong>Ravel</strong> by Ravel Labs.</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: "home"
};
</script>

<style lang="scss" scoped>
.logo {
  height: 10rem;
  width: 10rem;
}
</style>
