<template>
  <section class="section container mission-gallery">
    <p class="eyebrow">Mission gallery</p>
    <h2 class="section-title">Recent missions, in pictures.</h2>
    <p class="section-lede">A look back at SpaceX's rockets and completed flights</p>

    <!-- Show missions grid -->
    <div v-if="missions.length > 0" class="mission-gallery__grid">
      <article v-for="mission in missions" :key="mission.id" class="mission-card">
        <div class="mission-card__image-wrapper">
          <img
            :src="mission.image"
            :alt="mission.name"
            class="mission-card__image"
            loading="lazy"
            decoding="async"
          />
          <div class="mission-card__rocket-badge">{{ mission.rocketName }}</div>
        </div>
        <div class="mission-card__body">
          <h3 class="mission-card__title">{{ mission.name }}</h3>
          <p class="mission-card__date">{{ mission.date }}</p>
          <p class="mission-card__rocket">{{ mission.rocketName }}</p>
          <p class="mission-card__type" v-if="mission.missionType">{{ mission.missionType }}</p>
          <p class="mission-card__desc">{{ mission.description }}</p>
        </div>
      </article>
    </div>

    <div v-else class="mission-gallery__status">No mission images available.</div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import missionsData from '../data/spacex-mission-data.json'

interface Mission {
  id: string
  name: string
  date: string
  description: string
  image: string
  rocketName: string
  missionType?: string
}

const missions = ref<Mission[]>([])

/**
 * Loads missions straight from the bundled JSON, keeping only one mission per
 * unique image URL (first occurrence wins) so no photo appears twice in the
 * grid. Missions are included even if their image URL turns out to be broken —
 * we don't have a way to verify reachability at build time, so we render them
 * as-is for now.
 */
function loadMissions(): Mission[] {
  try {
    const seenImages = new Set<string>()
    const deduped: Mission[] = []

    for (const mission of missionsData as Mission[]) {
      if (!mission.image || seenImages.has(mission.image)) continue
      seenImages.add(mission.image)
      deduped.push(mission)
    }

    return deduped
  } catch (err) {
    console.error('Failed to load mission data:', err)
    return []
  }
}

onMounted(() => {
  missions.value = loadMissions()
})
</script>

<style scoped>
.mission-gallery {
  padding-top: 40px;
  padding-bottom: 60px;
}

.mission-gallery__status {
  margin-top: 32px;
  color: var(--color-text-dim);
  font-size: 14px;
}

.mission-gallery__grid {
  margin-top: 40px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.mission-card {
  background: var(--color-bg-raised);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.mission-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mission-card__image-wrapper {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
}

.mission-card__image {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
  background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
}

.mission-card:hover .mission-card__image {
  transform: scale(1.05);
}

.mission-card__rocket-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  backdrop-filter: blur(4px);
}

.mission-card__body {
  padding: 18px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.mission-card__title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.mission-card__date {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 4px 0 0 0;
}

.mission-card__rocket {
  margin-top: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mission-card__type {
  margin-top: 4px;
  font-size: 11px;
  color: var(--color-accent, #0ea5e9);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mission-card__desc {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-dim);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}
</style>
