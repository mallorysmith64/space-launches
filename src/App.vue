<template>
  <Navbar />
  <main>
    <router-view />
  </main>
</template>

<script setup lang="ts">
import Navbar from './components/Navbar.vue'
</script>

<style>
main {
  padding-top: var(--nav-height);
}
</style>
