import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/main',
      name: 'main',
      // route level code-splitting (lazy-loading)
      component: () => import('@/views/MainView.vue'),
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          // route level code-splitting (lazy-loading)
          component: () => import('@/views/DashboardView.vue'),
        },
      ]
    },
    
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");

  if (to.path === '/' && token) {
    // Already logged in, redirect to app
    return next('/main/dashboard');
  }

  if (to.path.startsWith('/main/dashboard') && !token) {
    // Trying to access protected page without auth
    return next('/');
  }

  next(); // allow access
});


export default router
