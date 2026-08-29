import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import AdminPortal from '../views/AdminPortal.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/about', name: 'about', component: About },
    { path: '/admin', name: 'admin', component: AdminPortal },
    { path: '/admin/dashboard', name: 'admin-dashboard', component: AdminDashboard },
  ],
})

export default router
