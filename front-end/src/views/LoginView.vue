<template>
  <div class="container">
    <img src="../assets/logo-smartops.png" alt="SmartOps logo" class="logo" />
    <form class="login-form" @submit.prevent="login">
      <input class="input-login" v-model="username" placeholder="Username" />
      <input class="input-login" v-model="password" type="password" placeholder="Password" />
      <button class="input-login" type="submit">Login</button>
    </form>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import axios from 'axios'

const api_base_url = import.meta.env.VITE_API_BASE_URL;
const router = useRouter()

let username = ''
let password = ''

const login = async () => {
  try {
    const response = await axios.post(`${api_base_url}/api/token/`, {
      username,
      password,
    });
    const accessToken = response.data.access;
    localStorage.setItem("token", accessToken);
    router.push("/main/dashboard");
  } catch (err) {
    alert("Login failed: check username or password.");
    console.error(err);
  }
};
</script>

<style scoped>

.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.logo {
  width: clamp(100px, 20vw, 250px); /* responsive size */
  max-width: 100%;
  height: auto;
}

.login-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-form button,input { 
  display: flex;
  align-items: center;
  justify-content: center; 
  margin: 5px 0 15px 0; 
  width: 100%; 
  padding: 8px;
  width: 30vh;
}
</style>
