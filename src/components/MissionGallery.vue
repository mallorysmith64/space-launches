<template>
  <section class="section container mission-gallery">
    <p class="eyebrow">Mission gallery</p>
    <h2 class="section-title">Recent missions, in pictures.</h2>
    <p class="section-lede">
      A look back at SpaceX's most recent completed flights — mission photos where they exist,
      patches where they don't. Each card features a different SpaceX rocket.
    </p>

    <div v-if="loading" class="mission-gallery__status">Loading missions…</div>
    <div v-else-if="error && missions.length === 0" class="mission-gallery__status">
      Couldn't load mission images right now. Try refreshing the page.
    </div>
    <div v-else class="mission-gallery__grid">
      <article v-for="mission in missions" :key="mission.id" class="mission-card">
        <div class="mission-card__image-wrapper">
          <img :src="mission.image" :alt="mission.name" class="mission-card__image" loading="lazy" />
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
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import missionsData from '../data/spacex-mission-data.json'

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
  rocketName: string
  missionType?: string
}

const MISSION_COUNT = 15
const CACHE_KEY = 'spacex-mission-gallery'
const CACHE_TTL_MS = 1000 * 60 * 60 // 1 hour

const missions = ref<Mission[]>([])
const loading = ref(true)
const error = ref(false)

const ROCKET_DISPLAY_NAMES: Record<string, string> = {
  'Falcon 9': 'Falcon 9',
  'Falcon Heavy': 'Falcon Heavy',
  'Starship': 'Starship',
  'Falcon 1': 'Falcon 1',
  'Falcon 9 Block 5': 'Falcon 9 Block 5',
  'Falcon 9 v1.1': 'Falcon 9 v1.1',
  'Falcon 9 Full Thrust': 'Falcon 9 Full Thrust'
}

function formatDate(dateUtc: string): string {
  return new Date(dateUtc).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function getRocketDisplayName(rocketName: string | null | undefined): string {
  if (!rocketName) return 'Unknown Rocket'
  
  if (ROCKET_DISPLAY_NAMES[rocketName]) {
    return ROCKET_DISPLAY_NAMES[rocketName]
  }
  
  if (rocketName.includes('Falcon Heavy')) return 'Falcon Heavy'
  if (rocketName.includes('Starship')) return 'Starship'
  if (rocketName.includes('Falcon 1')) return 'Falcon 1'
  if (rocketName.includes('Falcon 9')) return 'Falcon 9'
  
  return rocketName
}

function mapLaunch(launch: LL2Launch): Mission {
  const rocketName = launch.rocket?.configuration?.name || 'Unknown'
  
  return {
    id: launch.id,
    name: launch.name,
    date: formatDate(launch.net),
    description: launch.mission?.description || 'No mission description available.',
    image: launch.image!.image_url!,
    rocketName: getRocketDisplayName(rocketName)
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
    // Storage unavailable or full
  }
}

function loadFallbackData(): void {
  try {
    const fallbackMissions: Mission[] = (missionsData as Mission[]).slice(0, MISSION_COUNT)
    missions.value = fallbackMissions
    writeCache(fallbackMissions)
    console.log('Loaded missions from fallback data')
  } catch (err) {
    console.error('Failed to load fallback data:', err)
    error.value = true
  }
}

async function loadMissions(): Promise<void> {
  // Try cache first
  const cached = readCache()
  if (cached) {
    missions.value = cached
    loading.value = false
    return
  }

  try {
    // Try to load from API
    const params = new URLSearchParams({
      lsp__name: 'SpaceX',
      mode: 'detailed',
      limit: '150',
      ordering: '-net',
    })
    const res = await fetch(`https://ll.thespacedevs.com/2.3.0/launches/previous/?${params}`)
    if (!res.ok) throw new Error(`Launch Library API responded ${res.status}`)
    const data: LL2Response = await res.json()

    const seenImages = new Set<string>()
    const rocketCounts = new Map<string, number>()
    const MAX_PER_ROCKET = 2

    const withImages = data.results
      .filter((launch): launch is LL2Launch & { image: { image_url: string } } => {
        const url = launch.image?.image_url
        if (!url || seenImages.has(url)) return false

        const rocketName = getRocketDisplayName(launch.rocket?.configuration?.name)
        const count = rocketCounts.get(rocketName) || 0
        if (count >= MAX_PER_ROCKET) return false

        seenImages.add(url)
        rocketCounts.set(rocketName, count + 1)
        return true
      })
      .slice(0, MISSION_COUNT)
      .map(mapLaunch)

    if (withImages.length > 0) {
      missions.value = withImages
      writeCache(withImages)
      console.log('Loaded missions from API')
    } else {
      // No images from API, use fallback
      console.warn('No missions with images from API, using fallback data')
      loadFallbackData()
    }
  } catch (err) {
    console.error('Failed to load from API, using fallback data:', err)
    // Use fallback data on any API error
    loadFallbackData()
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
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.mission-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mission-card__image-wrapper {
  position: relative;
  overflow: hidden;
}

.mission-card__image {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  display: block;
  background: var(--color-bg-raised);
  transition: transform 0.3s ease;
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
