<template>
  <div class="admin-container">
    <!-- Header matching homepage style -->
    <div class="admin-header">
      <div class="header-content">
        <h1 class="admin-title">Admin Dashboard</h1>
        <button @click="handleLogout" class="logout-btn" :disabled="isLoading">
          {{ isLoading ? 'Logging out...' : 'Logout' }}
        </button>
      </div>
    </div>

    <!-- Admin section matching MissionGallery structure -->
    <section class="section container admin-section">
      <p class="eyebrow">Mission control</p>
      <h2 class="section-title">Edit missions, images & details.</h2>
      <p class="section-lede">
        Update mission photos, names, dates, and descriptions. Changes will appear on the homepage.
      </p>

      <!-- Loading state -->
      <div v-if="missions.length === 0 && loading" class="admin-status">Loading missions…</div>
      <div v-else-if="error && missions.length === 0" class="admin-status">
        Couldn't load missions. Try refreshing the page.
      </div>

      <!-- Editable missions grid -->
      <div v-else class="missions-grid">
        <div
          v-for="mission in missions"
          :key="mission.id"
          class="mission-edit-card"
          :class="{ 'mission-edit-card--editing': editingId === mission.id }"
        >
          <!-- View Mode -->
          <div v-if="editingId !== mission.id" class="mission-edit-card__view">
            <div class="mission-edit-card__image-wrapper">
              <img :src="mission.image" :alt="mission.name" class="mission-edit-card__image" />
              <div class="mission-edit-card__rocket-badge">{{ mission.rocketName }}</div>
            </div>
            <div class="mission-edit-card__body">
              <h3 class="mission-edit-card__title">{{ mission.name }}</h3>
              <p class="mission-edit-card__date">{{ mission.date }}</p>
              <p class="mission-edit-card__rocket">{{ mission.rocketName }}</p>
              <p class="mission-edit-card__desc">{{ mission.description }}</p>
            </div>
            <button @click="startEdit(mission)" class="mission-edit-card__edit-btn">Edit</button>
          </div>

          <!-- Edit Mode -->
          <div v-else class="mission-edit-card__edit">
            <div class="edit-form">
              <div class="form-group">
                <label>Image URL</label>
                <input v-model="editForm.image" type="text" placeholder="https://..." />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Title</label>
                  <input v-model="editForm.name" type="text" />
                </div>
                <div class="form-group">
                  <label>Date</label>
                  <input v-model="editForm.date" type="text" placeholder="Month DD, YYYY" />
                </div>
              </div>

              <div class="form-group">
                <label>Description</label>
                <textarea v-model="editForm.description" rows="4"></textarea>
              </div>

              <div class="form-actions">
                <button @click="saveEdit" class="btn-save">Save</button>
                <button @click="cancelEdit" class="btn-cancel">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import missionsData from '../data/spacex-mission-data.json'

// Launch Library API interfaces
interface RocketConfiguration {
  name: string | null
}

interface Rocket {
  configuration: RocketConfiguration | null
}

interface LaunchImage {
  image_url: string | null
}

interface LaunchMission {
  description: string | null
}

interface LaunchLibraryLaunch {
  id: string
  name: string
  net: string
  mission?: LaunchMission | null
  rocket?: Rocket | null
  image?: LaunchImage | null
}

interface LaunchLibraryResponse {
  results: LaunchLibraryLaunch[]
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

const router = useRouter()
const missions = ref<Mission[]>([])
const loading = ref(false)
const error = ref(false)
const isLoading = ref(false)
const editingId = ref<string | null>(null)
const editForm = reactive({
  image: '',
  name: '',
  date: '',
  description: '',
})

const MISSION_COUNT = 15
const CACHE_KEY = 'spacex-mission-gallery'
const CACHE_TTL_MS = 1000 * 60 * 60 // 1 hour

const ROCKET_DISPLAY_NAMES: Record<string, string> = {
  'Falcon 9': 'Falcon 9',
  'Falcon Heavy': 'Falcon Heavy',
  Starship: 'Starship',
  'Falcon 1': 'Falcon 1',
  'Falcon 9 Block 5': 'Falcon 9 Block 5',
  'Falcon 9 v1.1': 'Falcon 9 v1.1',
  'Falcon 9 Full Thrust': 'Falcon 9 Full Thrust',
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
  if (ROCKET_DISPLAY_NAMES[rocketName]) return ROCKET_DISPLAY_NAMES[rocketName]
  if (rocketName.includes('Falcon Heavy')) return 'Falcon Heavy'
  if (rocketName.includes('Starship')) return 'Starship'
  if (rocketName.includes('Falcon 1')) return 'Falcon 1'
  if (rocketName.includes('Falcon 9')) return 'Falcon 9'
  return rocketName
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

function loadFallbackData(): Mission[] {
  try {
    return (missionsData as Mission[]).slice(0, MISSION_COUNT)
  } catch (err) {
    console.error('Failed to load fallback data:', err)
    return []
  }
}

async function fetchFromBackend(): Promise<Mission[] | null> {
  try {
    const response = await fetch('/api/spacex/missions?limit=' + MISSION_COUNT)
    if (!response.ok) throw new Error(`Backend responded with ${response.status}`)
    return await response.json()
  } catch (err) {
    console.warn('Failed to fetch from backend:', err)
    return null
  }
}

async function fetchFromLaunchLibrary(): Promise<Mission[] | null> {
  try {
    const params = new URLSearchParams({
      lsp__name: 'SpaceX',
      mode: 'detailed',
      limit: '150',
      ordering: '-net',
    })
    const res = await fetch(`https://ll.thespacedevs.com/2.3.0/launches/previous/?${params}`)
    if (!res.ok) throw new Error(`Launch Library API responded ${res.status}`)
    const data = (await res.json()) as LaunchLibraryResponse

    const seenImages = new Set<string>()
    const rocketCounts = new Map<string, number>()
    const MAX_PER_ROCKET = 2

    return data.results
      .filter((launch: LaunchLibraryLaunch) => {
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
      .map((launch: LaunchLibraryLaunch) => ({
        id: launch.id,
        name: launch.name,
        date: formatDate(launch.net),
        description: launch.mission?.description || 'No mission description available.',
        image: launch.image!.image_url!,
        rocketName: getRocketDisplayName(launch.rocket?.configuration?.name),
      }))
  } catch (err) {
    console.warn('Failed to fetch from Launch Library:', err)
    return null
  }
}

async function loadMissionsInBackground(): Promise<void> {
  // Try backend first (faster), then Launch Library API
  let newData = await fetchFromBackend()

  if (!newData) {
    newData = await fetchFromLaunchLibrary()
  }

  if (newData && newData.length > 0) {
    missions.value = newData
    writeCache(newData)
    console.log('Missions loaded from backend/Launch Library')
  }
}

async function initializeMissions(): Promise<void> {
  // PHASE 1: Display cached or fallback data immediately (non-blocking)
  const cached = readCache()
  if (cached && cached.length > 0) {
    missions.value = cached
    console.log('Displaying cached missions immediately')
  } else {
    const fallback = loadFallbackData()
    if (fallback.length > 0) {
      missions.value = fallback
      console.log('Displaying fallback missions immediately')
    } else {
      loading.value = true
    }
  }

  // PHASE 2: Fetch fresh data in background (non-blocking)
  loadMissionsInBackground()
    .catch((err) => {
      console.error('Background fetch failed:', err)
      if (missions.value.length === 0) {
        error.value = true
      }
    })
    .finally(() => {
      loading.value = false
    })
}

function startEdit(mission: Mission) {
  editingId.value = mission.id
  editForm.image = mission.image
  editForm.name = mission.name
  editForm.date = mission.date
  editForm.description = mission.description
}

function saveEdit() {
  if (!editingId.value) return

  const index = missions.value.findIndex((m) => m.id === editingId.value)
  if (index !== -1) {
    const currentMission = missions.value[index]
    if (!currentMission) return

    const updatedMission: Mission = {
      id: currentMission.id,
      name: editForm.name,
      date: editForm.date,
      description: editForm.description,
      image: editForm.image,
      rocketName: currentMission.rocketName,
      missionType: currentMission.missionType,
    }
    missions.value[index] = updatedMission
  }

  editingId.value = null
}

function cancelEdit() {
  editingId.value = null
}

const handleLogout = async () => {
  isLoading.value = true
  try {
    const response = await fetch('/api/admin/logout', {
      method: 'GET',
      credentials: 'include',
    })

    if (response.ok) {
      await router.push('/login')
    } else {
      await router.push('/login')
    }
  } catch (err) {
    console.error('Logout error:', err)
    await router.push('/login')
  } finally {
    isLoading.value = false
  }
}

onMounted(initializeMissions)
</script>

<style scoped>
/* Layout */
.admin-container {
  min-height: calc(100vh - var(--nav-height));
  background: var(--color-bg);
}

.admin-header {
  padding: 40px 0;
  border-bottom: 1px solid var(--color-border);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.admin-title {
  margin: 0;
  font-size: clamp(28px, 4vw, 48px);
  font-weight: 700;
  line-height: 1.1;
}

.logout-btn {
  padding: 10px 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: white;
  background: var(--color-accent);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.logout-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Admin section */
.admin-section {
  padding-top: 40px;
  padding-bottom: 60px;
}

.admin-status {
  margin-top: 32px;
  color: var(--color-text-dim);
  font-size: 14px;
}

.missions-grid {
  margin-top: 40px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

/* Mission edit card */
.mission-edit-card {
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

.mission-edit-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mission-edit-card--editing {
  transform: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mission-edit-card__view {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.mission-edit-card__image-wrapper {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
}

.mission-edit-card__image {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.mission-edit-card:hover .mission-edit-card__image {
  transform: scale(1.05);
}

.mission-edit-card__rocket-badge {
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

.mission-edit-card__body {
  padding: 18px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.mission-edit-card__title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.mission-edit-card__date {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 4px 0 0 0;
}

.mission-edit-card__rocket {
  margin-top: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mission-edit-card__desc {
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

.mission-edit-card__edit-btn {
  align-self: flex-end;
  margin: 12px 18px 18px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  background: var(--color-accent);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mission-edit-card__edit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Edit mode */
.mission-edit-card__edit {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text);
}

.form-group input,
.form-group textarea {
  padding: 8px 12px;
  font-size: 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  color: var(--color-text);
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
  padding-top: 12px;
}

.btn-save,
.btn-cancel {
  flex: 1;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-save {
  color: white;
  background: var(--color-accent);
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn-cancel {
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover {
  background: var(--color-bg-raised);
}

/* Responsive */
@media (max-width: 720px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .admin-title {
    font-size: 28px;
  }

  .missions-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
