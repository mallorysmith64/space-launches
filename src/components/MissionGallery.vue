<template>
  <section class="section container mission-gallery">
    <p class="eyebrow">Mission gallery</p>
    <h2 class="section-title">Recent missions, in pictures.</h2>
    <p class="section-lede">
      A look back at SpaceX's most recent completed flights — mission photos where they exist,
      patches where they don't.
    </p>

    <div v-if="loading" class="mission-gallery__status">Loading missions…</div>
    <div v-else-if="error" class="mission-gallery__status">
      Couldn't load mission images right now. Try refreshing the page.
    </div>
    <div v-else class="mission-gallery__grid">
      <article v-for="mission in missions" :key="mission.id" class="mission-card">
        <img :src="mission.image" :alt="mission.name" class="mission-card__image" loading="lazy" />
        <div class="mission-card__body">
          <h3 class="mission-card__title">{{ mission.name }}</h3>
          <p class="mission-card__date">{{ mission.date }}</p>
          <p class="mission-card__desc">{{ mission.description }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface LL2Launch {
  id: string
  name: string
  net: string
  image: { image_url: string | null } | null
  mission: { description: string | null } | null
  rocket?: {
    configuration?: {
      name?: string | null
    }
  }
}

interface LL2Response {
  results: LL2Launch[]
}

interface Mission {
  id: string
  name: string
  date: string
  description: string
  image: string
}

const MISSION_COUNT = 9
const CACHE_KEY = 'spacex-mission-gallery'
const CACHE_TTL_MS = 1000 * 60 * 60 // 1 hour — launch history doesn't change often

const missions = ref<Mission[]>([])
const loading = ref(true)
const error = ref(false)

function formatDate(dateUtc: string): string {
  return new Date(dateUtc).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function mapLaunch(launch: LL2Launch): Mission {
  return {
    id: launch.id,
    name: launch.name,
    date: formatDate(launch.net),
    description: launch.mission?.description || 'No mission description available.',
    image: launch.image!.image_url!,
  }
}

function readCache(): Mission[] | null {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    if (!raw) return null
    const { timestamp, data } = JSON.parse(raw) as { timestamp: number; data: Mission[] }
    if (Date.now() - timestamp > CACHE_TTL_MS) return null
    return data
  } catch {
    return null
  }
}

function writeCache(data: Mission[]): void {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({ timestamp: Date.now(), data }))
  } catch {
    // Storage unavailable or full — safe to skip caching, next load just refetches.
  }
}

async function loadMissions(): Promise<void> {
  // Note: uses ll.thespacedevs.com (production). It's free but rate-limited per IP;
  // the 1-hour cache below already keeps repeat calls low. For local dev with heavier
  // testing, swap in https://lldev.thespacedevs.com (dev tier, no rate limit, may lag prod data).
  const cached = readCache()
  if (cached) {
    missions.value = cached
    loading.value = false
    return
  }

  try {
    // Over-fetch: SpaceX flies Falcon 9 far more than anything else, so to find enough
    // rocket variety (Falcon Heavy, Starship, etc.) we have to look through many past
    // launches. Falcon 9 is capped to just one appearance below.
    const params = new URLSearchParams({
      lsp__name: 'SpaceX',
      mode: 'detailed',
      limit: '100',
      ordering: '-net',
    })
    const res = await fetch(`https://ll.thespacedevs.com/2.3.0/launches/previous/?${params}`)
    if (!res.ok) throw new Error(`Launch Library API responded ${res.status}`)
    const data: LL2Response = await res.json()

    const seenImages = new Set<string>()
    const rocketCounts = new Map<string, number>()
    const MAX_PER_ROCKET = 1

    const withImages = data.results
      .filter((launch): launch is LL2Launch & { image: { image_url: string } } => {
        const url = launch.image?.image_url
        if (!url || seenImages.has(url)) return false

        const rocketName = launch.rocket?.configuration?.name || 'Unknown'
        const count = rocketCounts.get(rocketName) || 0
        if (count >= MAX_PER_ROCKET) return false

        seenImages.add(url)
        rocketCounts.set(rocketName, count + 1)
        return true
      })
      .slice(0, MISSION_COUNT)
      .map(mapLaunch)

    missions.value = withImages
    writeCache(withImages)
  } catch (err) {
    console.error('MissionGallery: failed to load launches', err)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadMissions)
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
}

.mission-card__image {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  display: block;
  background: var(--color-bg-raised);
}

.mission-card__body {
  padding: 18px;
}

.mission-card__title {
  font-size: 16px;
  font-weight: 600;
}

.mission-card__date {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mission-card__desc {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-dim);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
