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
          <button @click="openEditModal(mission)" class="mission-card__edit-btn">Edit Image</button>
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

    <!-- Edit Image Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <div class="modal__header">
          <h2>Update Image for {{ editingMission?.name }}</h2>
          <button @click="closeEditModal" class="modal__close-btn">✕</button>
        </div>

        <div class="modal__body">
          <!-- Current Image Preview -->
          <div class="modal__preview-section">
            <h3>Current Image</h3>
            <img
              :src="editingMission?.image"
              :alt="editingMission?.name"
              class="modal__preview-image"
            />
          </div>

          <!-- File Upload -->
          <div class="modal__upload-section">
            <label for="image-input" class="modal__file-label"> Choose JPEG Image (Max 5MB) </label>
            <input
              id="image-input"
              ref="fileInput"
              type="file"
              accept=".jpeg,.jpg"
              class="modal__file-input"
              @change="onFileSelected"
            />

            <!-- New Image Preview -->
            <div v-if="previewUrl" class="modal__new-preview">
              <h3>New Image Preview</h3>
              <img :src="previewUrl" :alt="'Preview'" class="modal__preview-image" />
            </div>

            <!-- Error Message -->
            <div v-if="uploadError" class="modal__error">
              {{ uploadError }}
            </div>

            <!-- Success Message -->
            <div v-if="uploadSuccess" class="modal__success">
              {{ uploadSuccess }}
            </div>
          </div>
        </div>

        <div class="modal__footer">
          <button
            @click="closeEditModal"
            class="modal__btn modal__btn--cancel"
            :disabled="isUploading"
          >
            Cancel
          </button>
          <button
            @click="saveImage"
            class="modal__btn modal__btn--save"
            :disabled="!selectedFile || isUploading"
          >
            {{ isUploading ? 'Uploading...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import missionsData from '../data/spacex-mission-data.json'
import { useRouter } from 'vue-router'

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
const isLoading = ref(false)

// Edit modal state
const showEditModal = ref(false)
const editingMission = ref<Mission | null>(null)
const selectedFile = ref<File | null>(null)
const previewUrl = ref<string>('')
const isUploading = ref(false)
const uploadError = ref<string>('')
const uploadSuccess = ref<string>('')
const fileInput = ref<HTMLInputElement>()

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

/**
 * Opens edit modal for a specific mission
 */
function openEditModal(mission: Mission): void {
  editingMission.value = mission
  showEditModal.value = true
  selectedFile.value = null
  previewUrl.value = ''
  uploadError.value = ''
  uploadSuccess.value = ''
}

/**
 * Closes edit modal and resets state
 */
function closeEditModal(): void {
  showEditModal.value = false
  editingMission.value = null
  selectedFile.value = null
  previewUrl.value = ''
  uploadError.value = ''
  uploadSuccess.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

/**
 * Handles file selection and generates preview
 */
function onFileSelected(event: Event): void {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  uploadError.value = ''
  uploadSuccess.value = ''

  if (!file) return

  // Validate file type
  if (!file.type.includes('jpeg') && !file.type.includes('jpg')) {
    uploadError.value = 'Cannot upload image: Only JPEG files are allowed'
    selectedFile.value = null
    previewUrl.value = ''
    return
  }

  // Validate file size (5MB = 5242880 bytes)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    uploadError.value = 'Cannot upload image: File size must be under 5MB'
    selectedFile.value = null
    previewUrl.value = ''
    return
  }

  // Generate preview
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)

  selectedFile.value = file
}

/**
 * Saves image to backend and updates mission
 */
async function saveImage(): Promise<void> {
  if (!selectedFile.value || !editingMission.value) return

  isUploading.value = true
  uploadError.value = ''
  uploadSuccess.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('missionId', editingMission.value.id)
    formData.append('missionTitle', editingMission.value.name)

    const response = await fetch('/api/admin/upload-image', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })

    const data = await response.json()

    if (!response.ok) {
      uploadError.value = data.message || 'Cannot upload image'
      return
    }

    // Update the mission's image URL with the new path from backend
    if (data.imagePath) {
      editingMission.value.image = data.imagePath
      // Update in missions array
      const missionIndex = missions.value.findIndex((m) => m.id === editingMission.value?.id)
      if (missionIndex !== -1) {
        missions.value[missionIndex].image = data.imagePath
      }
    }

    uploadSuccess.value = 'Image successfully updated'

    // Close modal after 1.5 seconds
    setTimeout(() => {
      closeEditModal()
    }, 1500)
  } catch (err) {
    console.error('Upload error:', err)
    uploadError.value = 'Cannot upload image'
  } finally {
    isUploading.value = false
  }
}

/**
 * Handles user logout by clearing session and redirecting to login
 */
async function handleLogout(): Promise<void> {
  isLoading.value = true
  try {
    // Clear auth token from localStorage (adjust key name if needed)
    localStorage.removeItem('authToken')

    // Redirect to login page
    await router.push('/login')
  } catch (err) {
    console.error('Logout failed:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  missions.value = loadMissions()
})
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-header {
  background: var(--color-bg-raised);
  border-bottom: 1px solid var(--color-border);
  padding: 20px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
}

.logout-btn {
  padding: 10px 20px;
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  border-radius: var(--radius);
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.logout-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.logout-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mission-gallery__status {
  margin-top: 32px;
  color: var(--color-text-dim);
  font-size: 14px;
}

.mission-gallery__grid {
  margin-top: 40px;
  margin-left: 20px;
  margin-right: 20px;
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

.mission-card__edit-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(10, 165, 233, 0.9);
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  opacity: 0;
}

.mission-card__image-wrapper:hover .mission-card__edit-btn {
  opacity: 1;
}

.mission-card__edit-btn:hover {
  background: rgba(10, 165, 233, 1);
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--color-bg-raised);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal__header {
  padding: 20px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal__header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.modal__close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-text-dim);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.modal__close-btn:hover {
  color: var(--color-text);
}

.modal__body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal__preview-section {
  margin-bottom: 24px;
}

.modal__preview-section h3,
.modal__new-preview h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modal__preview-image {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.modal__upload-section {
  margin-bottom: 24px;
}

.modal__file-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modal__file-input {
  display: block;
  width: 100%;
  padding: 12px;
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  background: var(--color-bg);
  color: var(--color-text-dim);
}

.modal__file-input:hover {
  border-color: var(--color-accent, #0ea5e9);
}

.modal__new-preview {
  margin-top: 20px;
}

.modal__error {
  margin-top: 16px;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #dc2626;
  font-size: 14px;
}

.modal__success {
  margin-top: 16px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 6px;
  color: #16a34a;
  font-size: 14px;
}

.modal__footer {
  padding: 20px;
  border-top: 1px solid var(--color-border);
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal__btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.modal__btn--cancel {
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.modal__btn--cancel:hover:not(:disabled) {
  opacity: 0.8;
}

.modal__btn--save {
  background: var(--color-accent, #0ea5e9);
  color: white;
}

.modal__btn--save:hover:not(:disabled) {
  opacity: 0.9;
}

.modal__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
