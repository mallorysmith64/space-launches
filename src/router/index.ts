import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Launches from '../views/Launches.vue'
import Rockets from '../views/Rockets.vue'
import About from '../views/About.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/launches', name: 'launches', component: Launches },
    { path: '/rockets', name: 'rockets', component: Rockets },
    { path: '/about', name: 'about', component: About }
  ]
})

export default router