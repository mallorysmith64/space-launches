<template>
  <section class="section container mission-gallery">
    <p class="eyebrow">Mission gallery</p>
    <h2 class="section-title">Multiple missions, in pictures</h2>
    <p class="section-lede">A look back at different rockets and completed flights</p>

    <!-- Company and rocket filters -->
    <div class="mission-gallery__controls">
      <label for="company-select" class="mission-gallery__filter-label">Company</label>
      <select id="company-select" v-model="selectedCompany" class="mission-gallery__select">
        <option v-for="option in companyOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>

      <label for="rocket-select" class="mission-gallery__filter-label">Rocket</label>
      <select id="rocket-select" v-model="selectedRocket" class="mission-gallery__select">
        <option v-for="option in rocketOptions" :key="option" :value="option">
          {{ option === 'all' ? 'All rockets' : option }}
        </option>
      </select>
    </div>

    <!-- Show missions grid -->
    <div v-if="filteredMissions.length > 0" class="mission-gallery__grid">
      <article v-for="mission in filteredMissions" :key="mission.id" class="mission-card">
        <div class="mission-card__image-wrapper">
          <img
            :src="mission.image"
            :alt="mission.name"
            class="mission-card__image"
            loading="lazy"
            decoding="async"
          />
          <span class="mission-card__company-badge">{{ companyLabel(mission.company) }}</span>
        </div>
        <div class="mission-card__body">
          <h3 class="mission-card__title">{{ mission.name }}</h3>
          <p class="mission-card__date">{{ mission.date }}</p>
          <p class="mission-card__rocket">{{ mission.rocketName }}</p>
          <p class="mission-card__type" v-if="mission.missionType">{{ mission.missionType }}</p>
          <p
            class="mission-card__desc"
            :class="{ 'mission-card__desc--expanded': isExpanded(mission.id) }"
            :ref="(el) => setDescRef(mission.id, el)"
          >
            {{ mission.description }}
          </p>
          <button
            v-if="isTruncated(mission.id)"
            type="button"
            class="mission-card__desc-toggle"
            @click="toggleAllDescriptions"
          >
            {{ allExpanded ? 'Show less' : 'Show more' }}
          </button>
        </div>
      </article>
    </div>

    <div v-else class="mission-gallery__status">No mission images available.</div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import spacexMissionsData from '../data/spacex-mission-data.json'
import jaxaMissionsData from '../data/jaxa-mission-data.json'

type Company = 'spacex' | 'jaxa'

interface Mission {
  id: string
  name: string
  date: string
  description: string
  image: string
  rocketName: string
  missionType?: string
}

interface MissionWithCompany extends Mission {
  company: Company
}

const COMPANY_LABELS: Record<Company, string> = {
  spacex: 'SpaceX',
  jaxa: 'JAXA',
}

const companyOptions = [
  { value: 'all', label: 'All companies' },
  { value: 'spacex', label: 'SpaceX' },
  { value: 'jaxa', label: 'JAXA' },
]

const missions = ref<MissionWithCompany[]>([])
const selectedCompany = ref<'all' | Company>('all')
const selectedRocket = ref<'all' | string>('all')

// Tracks which mission cards have their full description expanded, keyed
// by mission id. Works the same for SpaceX and JAXA missions since both
// are rendered from the same combined, tagged list.
const expandedDescriptionIds = ref<Set<string>>(new Set())

// Tracks which descriptions are actually clipped by the 3-line clamp in
// .mission-card__desc, so the "Show more" toggle only appears where it's
// needed. Determined by measuring the real rendered element rather than
// guessing from character count, since the same description can wrap
// differently depending on card width.
const truncatedDescriptionIds = ref<Set<string>>(new Set())
const descEls = new Map<string, HTMLElement>()

function setDescRef(missionId: string, el: unknown): void {
  if (el instanceof HTMLElement) {
    descEls.set(missionId, el)
  } else {
    descEls.delete(missionId)
  }
}

function isTruncated(missionId: string): boolean {
  return truncatedDescriptionIds.value.has(missionId)
}

/**
 * Compares each description element's full content height (scrollHeight)
 * against its clamped visible height (clientHeight) to see if text is
 * actually being cut off. Skips elements that are currently expanded,
 * since removing the clamp makes them equal — the previously-detected
 * truncated state is preserved for those instead of being cleared.
 */
function checkTruncatedDescriptions(): void {
  const next = new Set(truncatedDescriptionIds.value)

  descEls.forEach((el, missionId) => {
    if (expandedDescriptionIds.value.has(missionId)) return

    const isOverflowing = el.scrollHeight - el.clientHeight > 1
    if (isOverflowing) {
      next.add(missionId)
    } else {
      next.delete(missionId)
    }
  })

  truncatedDescriptionIds.value = next
}

let resizeTimeout: ReturnType<typeof setTimeout> | undefined
function onWindowResize(): void {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(checkTruncatedDescriptions, 150)
}

function isExpanded(missionId: string): boolean {
  return expandedDescriptionIds.value.has(missionId)
}

function toggleDescription(missionId: string): void {
  const next = new Set(expandedDescriptionIds.value)
  if (next.has(missionId)) {
    next.delete(missionId)
  } else {
    next.add(missionId)
  }
  expandedDescriptionIds.value = next
}

/**
 * Expand or collapse all truncated descriptions at once.
 * Only affects cards that actually have truncated text.
 */
function toggleAllDescriptions(): void {
  const next = new Set(expandedDescriptionIds.value)

  // Get all truncated card IDs
  const truncatedIds = Array.from(truncatedDescriptionIds.value)

  if (allExpanded.value) {
    // If all are expanded, collapse all truncated cards
    truncatedIds.forEach((id) => next.delete(id))
  } else {
    // If not all are expanded, expand all truncated cards
    truncatedIds.forEach((id) => next.add(id))
  }

  expandedDescriptionIds.value = next
}

/**
 * Computed property to determine if all truncated cards are currently expanded
 */
const allExpanded = computed(() => {
  if (truncatedDescriptionIds.value.size === 0) return false
  return Array.from(truncatedDescriptionIds.value).every((id) =>
    expandedDescriptionIds.value.has(id),
  )
})

/**
 * Computed property to check if there are any expandable cards
 */
const hasExpandableCards = computed(() => truncatedDescriptionIds.value.size > 0)

// Eagerly import every image under src/images so Vite bundles them and
// rewrites each to a real, hashed build URL. The keys this produces look
// like "../images/jaxa/selene-kaguya.jpg" (relative to this file) — we
// normalize those to "/src/images/..." to match the JSON data's format.
const imageModules = import.meta.glob('../images/**/*.{png,jpg,jpeg,webp,svg}', {
  eager: true,
  import: 'default',
}) as Record<string, string>

const imageUrlByPath: Record<string, string> = Object.fromEntries(
  Object.entries(imageModules).map(([path, url]) => [path.replace('..', '/src'), url]),
)

// Fallback index: filename only (lowercased), so mismatches in directory
// structure or letter case between the JSON data and the actual files on
// disk don't break resolution.
const imageUrlByBasename: Record<string, string> = Object.fromEntries(
  Object.entries(imageModules).map(([path, url]) => {
    const basename = path.split('/').pop() ?? path
    return [basename.toLowerCase(), url]
  }),
)

if (import.meta.env.DEV) {
  console.log('[MissionGallery] Bundled image paths found:', Object.keys(imageModules))
}

function resolveImage(path: string): string {
  const exact = imageUrlByPath[path]
  if (exact) return exact

  const basename = path.split('/').pop() ?? path
  const byName = imageUrlByBasename[basename.toLowerCase()]
  if (byName) {
    console.warn(
      `[MissionGallery] Matched "${path}" by filename only — the folder or case in the JSON doesn't match the file on disk. Consider fixing the JSON path.`,
    )
    return byName
  }

  console.warn(`[MissionGallery] No bundled image found for path: "${path}"`)
  return path
}

function companyLabel(company: Company): string {
  return COMPANY_LABELS[company]
}

/**
 * Loads missions from the bundled JSON files for each company, tagging each
 * mission with its company so the dropdown can filter the combined list.
 * Within each company's data, only one mission per unique image URL is kept
 * (first occurrence wins) so no photo appears twice in the grid. Missions
 * are included even if their image URL turns out to be broken — we don't
 * have a way to verify reachability at build time, so we render them as-is
 * for now.
 */
function loadMissionsForCompany(data: Mission[], company: Company): MissionWithCompany[] {
  const seenImages = new Set<string>()
  const deduped: MissionWithCompany[] = []

  for (const mission of data) {
    if (!mission.image || seenImages.has(mission.image)) continue
    seenImages.add(mission.image)
    deduped.push({ ...mission, company, image: resolveImage(mission.image) })
  }

  return deduped
}

function loadMissions(): MissionWithCompany[] {
  try {
    return [
      ...loadMissionsForCompany(spacexMissionsData as Mission[], 'spacex'),
      ...loadMissionsForCompany(jaxaMissionsData as Mission[], 'jaxa'),
    ]
  } catch (err) {
    console.error('Failed to load mission data:', err)
    return []
  }
}

const rocketOptions = computed(() => {
  const missionsForCompany =
    selectedCompany.value === 'all'
      ? missions.value
      : missions.value.filter((mission) => mission.company === selectedCompany.value)

  const uniqueRockets = Array.from(
    new Set(missionsForCompany.map((mission) => mission.rocketName)),
  ).sort((a, b) => a.localeCompare(b))
  return ['all', ...uniqueRockets]
})

// If the company filter changes and the currently selected rocket isn't
// available for the new company (or "all" companies), fall back to "all"
// rather than silently showing zero results.
watch(rocketOptions, (options) => {
  if (!options.includes(selectedRocket.value)) {
    selectedRocket.value = 'all'
  }
})

const filteredMissions = computed(() => {
  return missions.value.filter((mission) => {
    const matchesCompany =
      selectedCompany.value === 'all' || mission.company === selectedCompany.value
    const matchesRocket =
      selectedRocket.value === 'all' || mission.rocketName === selectedRocket.value
    return matchesCompany && matchesRocket
  })
})

// Reset expanded descriptions when filters change
watch(filteredMissions, () => {
  expandedDescriptionIds.value = new Set()
})

onMounted(() => {
  missions.value = loadMissions()
  window.addEventListener('resize', onWindowResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onWindowResize)
  clearTimeout(resizeTimeout)
})

// Re-measure truncation any time the visible set of cards changes (initial
// load, or the company/rocket filters narrowing the list) — 'post' waits
// until Vue has updated the DOM so the elements reflect the new content.
watch(
  filteredMissions,
  () => {
    nextTick(checkTruncatedDescriptions)
  },
  { flush: 'post' },
)
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

.mission-gallery__controls {
  margin-top: 28px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.mission-gallery__filter-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mission-gallery__select {
  appearance: none;
  background: var(--color-bg-raised);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 8px 36px 8px 14px;
  font-size: 14px;
  font-weight: 500;
  color: inherit;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23888' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  transition: border-color 0.2s ease;
}

.mission-gallery__select:hover,
.mission-gallery__select:focus {
  border-color: var(--color-accent, #0ea5e9);
  outline: none;
}

.mission-gallery__grid {
  margin-top: 24px;
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

.mission-card__company-badge {
  position: absolute;
  top: 8px;
  right: 8px;
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

.mission-card__desc--expanded {
  display: block;
  -webkit-line-clamp: unset;
  overflow: visible;
  flex: none;
}

.mission-card__desc-toggle {
  align-self: flex-start;
  margin-top: 6px;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-accent, #0ea5e9);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  cursor: pointer;
}

.mission-card__desc-toggle:hover,
.mission-card__desc-toggle:focus {
  text-decoration: underline;
  outline: none;
}
</style>
