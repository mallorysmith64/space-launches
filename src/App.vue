<template>
  <AppNavbar />
  <main>
    <router-view />
  </main>
</template>

<script setup lang="ts">
import AppNavbar from './components/Navbar.vue'
</script>

<style>
main {
  padding-top: var(--nav-height);
  /* Space background that works for the entire main content */
  background:
    linear-gradient(135deg, rgba(10, 13, 18, 0.4) 0%, rgba(20, 25, 40, 0.3) 100%),
    url('https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920&q=80') center/cover
      no-repeat;
  min-height: 100vh;
  /* Creates a parallax effect when scrolling */
  background-attachment: fixed;
}

/* For the hero/first section specifically with a stronger space vibe */
main::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 100vh;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(79, 209, 255, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 50%, rgba(255, 106, 61, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 1;
}
</style>
