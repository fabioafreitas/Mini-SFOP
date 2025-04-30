<template>
  <div class="dashboard">
    <aside class="sidebar">
      <h1 class="logo">SmartOps</h1>
      <nav class="nav-links">
        <RouterLink to="/main/dashboard" active-class="active-link">Dashboard</RouterLink>
        <!-- <RouterLink to="/main/cicrano" active-class="active-link">Cicrano</RouterLink> -->
      </nav>
      <button class="logout-btn" @click="logout">Logout</button>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>


<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const logout = () => {
  localStorage.removeItem('token');      // Clear the JWT
  router.push('/');                 // Redirect to login page
};
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
  font-family: 'Segoe UI', Tahoma, sans-serif;
}

.sidebar {
  width: 25vh;
  background-color: #1e1e2f;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 2rem;
  text-align: center;
  color: #4fd1c5;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex-grow: 1;
}

.nav-links a {
  color: #f1f5f9; /* brighter for better contrast */
  text-decoration: none;
  font-size: 1rem;
  padding: 0.5rem;
  border-radius: 5px;
  transition: background 0.2s ease, color 0.2s ease;
}

.nav-links a:hover {
  background-color: #2d2d44;
  color: #ffffff;
}

.active-link {
  background-color: #4fd1c5;
  color: #1e1e2f;
  font-weight: bold;
}

.logout-btn {
  background-color: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.logout-btn:hover {
  background-color: #dc2626;
}

.main-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background-color: #ffffff;
  box-shadow: inset 1px 0 4px rgba(0, 0, 0, 0.05);
}
</style>
