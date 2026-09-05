import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/HomePortal.vue'
import AboutPage from '../views/AboutPage.vue'
import AdminPortal from '../views/AdminPortal.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/about', name: 'about-page', component: AboutPage },
    { path: '/admin', name: 'admin-portal', component: AdminPortal },
    { path: '/admin/dashboard', name: 'admin-dashboard', component: AdminDashboard },
  ],
})

export default router
