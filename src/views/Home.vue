<script setup lang="ts">
import MissionGallery from '../components/MissionGallery.vue'
</script>

<template>
  <section class="hero">
    <div class="container hero__inner">
      <p class="eyebrow">Mission control</p>
      <h1 class="hero__title">Every SpaceX launch,<br />tracked in one feed.</h1>
      <p class="section-lede">
        Live status, mission patches, and vehicle data for every flight — past, present, and
        upcoming.
      </p>
    </div>
  </section>

  <MissionGallery />
</template>

<style scoped>
.hero {
  padding: 88px 0 40px;
  border-bottom: 1px solid var(--color-border);
}

.hero__inner {
  max-width: 720px;
}

.hero__title {
  margin-top: 14px;
  font-size: clamp(34px, 5vw, 56px);
  font-weight: 700;
  line-height: 1.1;
}

.hero__actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}
</style>
