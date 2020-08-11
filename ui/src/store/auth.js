import API from "@/api";

const ls = window.localStorage;

const auth = {
  namespaced: true,
  state: {
    loading: false,
    token: ls.getItem("token"),
    user: {
      id: ls.getItem("user:id"),
      email: ls.getItem("user:email")
    },
    message: "",
    error: undefined
  },
  mutations: {
    SET_USER(state, user) {
      state.user.email = user.email;
      state.user.id = user.id;
      ls.setItem("user:email", user.email);
      ls.setItem("user:id", user.id);
    },
    CLEAR_USER(state) {
      state.user = {};
    },
    LOGIN_REQUEST(state, user) {
      state.user.email = user.email;
      state.loading = true;
    },
    LOGIN_SUCCESS(state, token) {
      state.loading = false;
      state.error = undefined;
      state.token = token;
      ls.setItem("token", token);
    },
    LOGIN_FAILURE(state, error) {
      state.loading = false;
      state.error = error;
      ls.setItem("token", "");
      state.token = "";
    },
    LOGOUT_SUCCESS(state) {
      ls.setItem("token", "");
      state.user = {};
    },
    LOGOUT_FAILURE(state, err) {
      state.error = err;
    },
    SIGNUP_REQUEST(state, user) {
      state.loading = true;
      state.error = undefined;
    },
    SIGNUP_SUCCESS(state, data) {
      state.loading = false;
      state.error = undefined;
    },
    SIGNUP_FAILURE(state, err) {
      state.loading = false;
      state.error = err;
      state.message = err;
    },
    CHECK_SUCCESS(state) {
      state.isAuthenticated = true;
    },
    CHECK_FAILURE(state, error) {
      state.token = "";
      state.user = {};
      state.error = error;
    }
  },
  getters: {
    token: () => ls.getItem("token"),
    user: state => state.user
  },
  actions: {
    async login({ commit }, user) {
      try {
        commit("LOGIN_REQUEST", user);
        let { data } = await API().post("/auth/login", {
          username: user.email,
          password: user.password
        });
        commit("LOGIN_SUCCESS", data["access_token"]);
        return data;
      } catch (err) {
        commit("LOGIN_FAILURE", err);
        throw new Error("failed to login");
      }
    },
    async logout({ commit }) {
      try {
        commit("LOGOUT_SUCCESS");
      } catch (error) {
        commit("LOGOUT_FAILURE", error);
      }
    },
    async signup({ commit, dispatch }, user) {
      try {
        commit("SIGNUP_REQUEST");
        let data = await API().post("/auth/signup", {
          email: user.email,
          password: user.password,
          name: user.name
        });

        // successfully signed up
        if (data.status === 201) {
          commit("SIGNUP_SUCCESS", data.data.message);
          return Promise.resolve(data);
        }

        // email already exists
        if (data.data.status === "500") {
          commit("SIGNUP_FAILURE", data.data.message);
          return Promise.reject(Error(`error signing up user: ${data.data.message}`))
        }

        // default error
        commit("SIGNUP_FAILURE", data.data.message);
        return Promise.reject(Error(`unknonw data payload: ${err}`))
      } catch (err) {
        commit("SIGNUP_FAILURE", "Failed to signup.");
        throw new Error("error signing up");
      }
    },
    async check({ commit, dispatch }) {
      try {
        let { data } = await API().get("/auth/check");
        commit("CHECK_SUCCESS", data);
      } catch (error) {
        if (error === "Request failed with status code 401") {
          commit("LOGOUT_REQUEST");
          commit("LOGOUT_SUCCESS");
        } else {
          throw new Error(error);
        }

        dispatch("CHECK_FAILURE", error);
        return error;
      }
    }
  }
};

export default auth;
