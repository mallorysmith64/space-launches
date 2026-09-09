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

    <!-- Mission grid header with Add New action -->
    <header class="mission-gallery__header">
      <button @click="openAddModal" class="add-mission-btn" type="button">+ Add New Mission</button>
    </header>

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
          <div class="mission-card__action-buttons">
            <button
              @click="openEditModal(mission)"
              class="mission-card__edit-btn"
              title="Edit Mission"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button
              @click="openDeleteModal(mission)"
              class="mission-card__delete-btn"
              title="Delete Mission"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path>
                <path d="M10 11v6"></path>
                <path d="M14 11v6"></path>
                <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"></path>
              </svg>
            </button>
          </div>
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
          <h2>Update Mission</h2>
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

          <!-- Title Edit Section -->
          <div class="modal__title-section">
            <label for="title-input" class="modal__title-label">Mission Title</label>
            <input
              id="title-input"
              v-model="editingTitle"
              type="text"
              class="modal__title-input"
              placeholder="Enter mission title"
            />
          </div>

          <!-- Date Edit Section -->
          <div class="modal__date-section">
            <label for="date-input" class="modal__date-label">Mission Date</label>
            <input
              id="date-input"
              v-model="editingDate"
              type="text"
              class="modal__date-input"
              placeholder="Enter mission date (e.g., January 15, 2024)"
            />
          </div>

          <!-- Rocket Type Edit Section -->
          <div class="modal__rocket-type-section">
            <label for="rocket-type-input" class="modal__rocket-type-label">Rocket Type</label>
            <input
              id="rocket-type-input"
              v-model="editingRocketType"
              type="text"
              class="modal__rocket-type-input"
              placeholder="Enter rocket type (e.g., Falcon 9, Falcon Heavy)"
            />
          </div>

          <!-- Mission Type Edit Section -->
          <div class="modal__mission-type-section">
            <label for="mission-type-input" class="modal__mission-type-label">Mission Type</label>
            <input
              id="mission-type-input"
              v-model="editingMissionType"
              type="text"
              class="modal__mission-type-input"
              placeholder="Enter mission type (e.g., Resupply, Crewed, Science)"
            />
          </div>

          <!-- Description Edit Section -->
          <div class="modal__description-section">
            <label for="description-input" class="modal__description-label">Description</label>
            <textarea
              id="description-input"
              v-model="editingDescription"
              class="modal__description-input"
              placeholder="Enter mission description"
              rows="4"
            ></textarea>
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
            :disabled="
              (!selectedFile &&
                editingTitle === editingMission?.name &&
                editingDescription === editingMission?.description &&
                editingDate === editingMission?.date &&
                editingRocketType === editingMission?.rocketName &&
                editingMissionType === (editingMission?.missionType || '')) ||
              isUploading
            "
          >
            {{ isUploading ? 'Updating...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add New Mission Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal">
        <div class="modal__header">
          <h2>Add New Mission</h2>
          <button @click="closeAddModal" class="modal__close-btn">✕</button>
        </div>

        <div class="modal__body">
          <!-- Image Upload -->
          <div class="modal__upload-section">
            <label for="new-image-input" class="modal__file-label">
              Choose JPEG Image (Max 5MB) <span class="modal__required">*</span>
            </label>
            <input
              id="new-image-input"
              ref="newFileInput"
              type="file"
              accept=".jpeg,.jpg"
              class="modal__file-input"
              @change="onNewFileSelected"
            />

            <!-- New Image Preview -->
            <div v-if="newPreviewUrl" class="modal__new-preview">
              <h3>Image Preview</h3>
              <img :src="newPreviewUrl" :alt="'Preview'" class="modal__preview-image" />
            </div>

            <!-- Error Message -->
            <p v-if="newUploadError" class="modal__field-error">{{ newUploadError }}</p>
          </div>

          <!-- Title -->
          <div class="modal__title-section">
            <label for="new-title-input" class="modal__title-label">
              Mission Title <span class="modal__required">*</span>
            </label>
            <input
              id="new-title-input"
              v-model="newTitle"
              type="text"
              class="modal__title-input"
              placeholder="Enter mission title"
              @input="newTitleError = ''"
            />
            <p v-if="newTitleError" class="modal__field-error">{{ newTitleError }}</p>
          </div>

          <!-- Date -->
          <div class="modal__date-section">
            <label for="new-date-input" class="modal__date-label">
              Mission Date <span class="modal__required">*</span>
            </label>
            <input
              id="new-date-input"
              v-model="newDate"
              type="text"
              class="modal__date-input"
              placeholder="Enter mission date (e.g., January 15, 2024)"
              @input="newDateError = ''"
            />
            <p v-if="newDateError" class="modal__field-error">{{ newDateError }}</p>
          </div>

          <!-- Rocket Type -->
          <div class="modal__rocket-type-section">
            <label for="new-rocket-type-input" class="modal__rocket-type-label">
              Rocket Type <span class="modal__required">*</span>
            </label>
            <input
              id="new-rocket-type-input"
              v-model="newRocketType"
              type="text"
              class="modal__rocket-type-input"
              placeholder="Enter rocket type (e.g., Falcon 9, Falcon Heavy)"
              @input="newRocketTypeError = ''"
            />
            <p v-if="newRocketTypeError" class="modal__field-error">{{ newRocketTypeError }}</p>
          </div>

          <!-- Mission Type -->
          <div class="modal__mission-type-section">
            <label for="new-mission-type-input" class="modal__mission-type-label">
              Mission Type <span class="modal__required">*</span>
            </label>
            <input
              id="new-mission-type-input"
              v-model="newMissionType"
              type="text"
              class="modal__mission-type-input"
              placeholder="Enter mission type (e.g., Resupply, Crewed, Science)"
              @input="newMissionTypeError = ''"
            />
            <p v-if="newMissionTypeError" class="modal__field-error">{{ newMissionTypeError }}</p>
          </div>

          <!-- Description -->
          <div class="modal__description-section">
            <label for="new-description-input" class="modal__description-label">
              Description <span class="modal__required">*</span>
            </label>
            <textarea
              id="new-description-input"
              v-model="newDescription"
              class="modal__description-input"
              placeholder="Enter mission description"
              rows="4"
              @input="newDescriptionError = ''"
            ></textarea>
            <p v-if="newDescriptionError" class="modal__field-error">{{ newDescriptionError }}</p>
          </div>

          <!-- Form-level Error / Success -->
          <div v-if="newSaveError" class="modal__error">{{ newSaveError }}</div>
          <div v-if="newSaveSuccess" class="modal__success">{{ newSaveSuccess }}</div>
        </div>

        <div class="modal__footer">
          <button
            @click="closeAddModal"
            class="modal__btn modal__btn--cancel"
            :disabled="isCreating"
          >
            Cancel
          </button>
          <button
            @click="saveNewMission"
            class="modal__btn modal__btn--save"
            :disabled="isCreating"
          >
            {{ isCreating ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal modal--confirm">
        <div class="modal__header">
          <h2>Delete Mission</h2>
          <button @click="closeDeleteModal" class="modal__close-btn">✕</button>
        </div>

        <div class="modal__body">
          <p class="modal__confirm-text">
            Are you sure you want to delete
            <strong>{{ missionToDelete?.name }}</strong
            >? This action cannot be undone.
          </p>
          <div v-if="deleteError" class="modal__error">{{ deleteError }}</div>
        </div>

        <div class="modal__footer">
          <button
            @click="closeDeleteModal"
            class="modal__btn modal__btn--cancel"
            :disabled="isDeleting"
          >
            Cancel
          </button>
          <button
            @click="confirmDeleteMission"
            class="modal__btn modal__btn--delete"
            :disabled="isDeleting"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete' }}
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

interface ApiResponse {
  message?: string
  imagePath?: string
  error?: string
  mission?: Mission
}

// API Base URL - point to Flask backend on port 5000
const API_BASE_URL = 'http://localhost:5000'

const router = useRouter()
const missions = ref<Mission[]>([])
const isLoading = ref(false)

// Edit modal state
const showEditModal = ref(false)
const editingMission = ref<Mission | null>(null)
const editingTitle = ref('')
const editingDescription = ref('')
const editingDate = ref('')
const editingRocketType = ref('')
const editingMissionType = ref('')
const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const isUploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref('')
const fileInput = ref<HTMLInputElement | undefined>(undefined)

// Add New Mission modal state
const showAddModal = ref(false)
const newTitle = ref('')
const newDate = ref('')
const newRocketType = ref('')
const newMissionType = ref('')
const newDescription = ref('')
const newSelectedFile = ref<File | null>(null)
const newPreviewUrl = ref('')
const newUploadError = ref('')
const newFileInput = ref<HTMLInputElement | undefined>(undefined)

// Add New Mission per-field validation errors
const newTitleError = ref('')
const newDateError = ref('')
const newRocketTypeError = ref('')
const newMissionTypeError = ref('')
const newDescriptionError = ref('')

// Add New Mission save state
const isCreating = ref(false)
const newSaveError = ref('')
const newSaveSuccess = ref('')

// Delete Mission modal state
const showDeleteModal = ref(false)
const missionToDelete = ref<Mission | null>(null)
const isDeleting = ref(false)
const deleteError = ref('')

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
  editingTitle.value = mission.name
  editingDescription.value = mission.description
  editingDate.value = mission.date
  editingRocketType.value = mission.rocketName
  editingMissionType.value = mission.missionType || ''
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
  editingTitle.value = ''
  editingDescription.value = ''
  editingDate.value = ''
  editingRocketType.value = ''
  editingMissionType.value = ''
  selectedFile.value = null
  previewUrl.value = ''
  uploadError.value = ''
  uploadSuccess.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

/**
 * Opens the Add New Mission modal with empty fields
 */
function openAddModal(): void {
  newTitle.value = ''
  newDate.value = ''
  newRocketType.value = ''
  newMissionType.value = ''
  newDescription.value = ''
  newSelectedFile.value = null
  newPreviewUrl.value = ''
  newUploadError.value = ''
  newTitleError.value = ''
  newDateError.value = ''
  newRocketTypeError.value = ''
  newMissionTypeError.value = ''
  newDescriptionError.value = ''
  newSaveError.value = ''
  newSaveSuccess.value = ''
  showAddModal.value = true
}

/**
 * Closes the Add New Mission modal and resets its fields
 */
function closeAddModal(): void {
  showAddModal.value = false
  newTitle.value = ''
  newDate.value = ''
  newRocketType.value = ''
  newMissionType.value = ''
  newDescription.value = ''
  newSelectedFile.value = null
  newPreviewUrl.value = ''
  newUploadError.value = ''
  newTitleError.value = ''
  newDateError.value = ''
  newRocketTypeError.value = ''
  newMissionTypeError.value = ''
  newDescriptionError.value = ''
  newSaveError.value = ''
  newSaveSuccess.value = ''
  if (newFileInput.value) {
    newFileInput.value.value = ''
  }
}

/**
 * Handles file selection and generates preview for the Add New Mission modal
 */
function onNewFileSelected(event: Event): void {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  newUploadError.value = ''

  if (!file) return

  // Validate file type
  if (!file.type.includes('jpeg') && !file.type.includes('jpg')) {
    newUploadError.value = 'Cannot upload image: Only JPEG files are allowed'
    newSelectedFile.value = null
    newPreviewUrl.value = ''
    return
  }

  // Validate file size (5MB = 5242880 bytes)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    newUploadError.value = 'Cannot upload image: File size must be under 5MB'
    newSelectedFile.value = null
    newPreviewUrl.value = ''
    return
  }

  // Generate preview
  const reader = new FileReader()
  reader.onload = (e) => {
    newPreviewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)

  newSelectedFile.value = file
}

/**
 * Validates all required fields for the Add New Mission form.
 * Sets the relevant error ref for any field that's missing and
 * returns whether the form as a whole is valid.
 */
function validateAddForm(): boolean {
  let isValid = true

  if (!newTitle.value.trim()) {
    newTitleError.value = 'Mission title is required'
    isValid = false
  }

  if (!newDate.value.trim()) {
    newDateError.value = 'Mission date is required'
    isValid = false
  }

  if (!newRocketType.value.trim()) {
    newRocketTypeError.value = 'Rocket type is required'
    isValid = false
  }

  if (!newMissionType.value.trim()) {
    newMissionTypeError.value = 'Mission type is required'
    isValid = false
  }

  if (!newDescription.value.trim()) {
    newDescriptionError.value = 'Description is required'
    isValid = false
  }

  if (!newSelectedFile.value) {
    newUploadError.value = 'An image is required'
    isValid = false
  }

  return isValid
}

/**
 * Validates and saves a new mission, uploading its image to /src/images
 * and appending the mission to the backing JSON data.
 */
async function saveNewMission(): Promise<void> {
  newSaveError.value = ''
  newSaveSuccess.value = ''

  if (!validateAddForm()) {
    return
  }

  isCreating.value = true

  try {
    const formData = new FormData()
    formData.append('file', newSelectedFile.value as File)
    formData.append('title', newTitle.value.trim())
    formData.append('date', newDate.value.trim())
    formData.append('rocketType', newRocketType.value.trim())
    formData.append('missionType', newMissionType.value.trim())
    formData.append('description', newDescription.value.trim())

    const response = await fetch(`${API_BASE_URL}/api/admin/create-mission`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })

    const data = await parseResponseJson(response)

    if (!response.ok) {
      newSaveError.value = data.message || data.error || 'Failed to create mission'
      return
    }

    if (data.mission) {
      missions.value.unshift(data.mission)
    }

    newSaveSuccess.value = 'Mission successfully created'

    // Close modal after a short delay so the success message is visible
    setTimeout(() => {
      closeAddModal()
    }, 1200)
  } catch (err) {
    console.error('Create mission error:', err)
    if (err instanceof TypeError) {
      newSaveError.value =
        'Network error: Cannot connect to server. Make sure the backend is running on http://localhost:5000'
    } else {
      newSaveError.value =
        err instanceof Error ? err.message : 'An error occurred while creating the mission'
    }
  } finally {
    isCreating.value = false
  }
}

/**
 * Opens the delete confirmation modal for a specific mission
 */
function openDeleteModal(mission: Mission): void {
  missionToDelete.value = mission
  deleteError.value = ''
  showDeleteModal.value = true
}

/**
 * Closes the delete confirmation modal and resets its state
 */
function closeDeleteModal(): void {
  showDeleteModal.value = false
  missionToDelete.value = null
  deleteError.value = ''
}

/**
 * Confirms deletion of the selected mission: removes it from the backend
 * (JSON data + image file) and, on success, from the local missions list.
 */
async function confirmDeleteMission(): Promise<void> {
  if (!missionToDelete.value) return

  isDeleting.value = true
  deleteError.value = ''

  try {
    const response = await fetch(`${API_BASE_URL}/api/admin/delete-mission`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ missionId: missionToDelete.value.id }),
    })

    const data = await parseResponseJson(response)

    if (!response.ok) {
      deleteError.value = data.message || data.error || 'Failed to delete mission'
      return
    }

    missions.value = missions.value.filter((m) => m.id !== missionToDelete.value!.id)
    closeDeleteModal()
  } catch (err) {
    console.error('Delete mission error:', err)
    if (err instanceof TypeError) {
      deleteError.value =
        'Network error: Cannot connect to server. Make sure the backend is running on http://localhost:5000'
    } else {
      deleteError.value =
        err instanceof Error ? err.message : 'An error occurred while deleting the mission'
    }
  } finally {
    isDeleting.value = false
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
 * Safely parse JSON response with fallback for non-JSON responses
 */
async function parseResponseJson(response: Response): Promise<ApiResponse> {
  try {
    const contentType = response.headers.get('content-type')

    // Check if response is actually JSON
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    } else {
      // Return error object for non-JSON responses (like HTML error pages)
      return {
        error: `Server error: ${response.status} ${response.statusText}`,
        message: `Server error: ${response.status} ${response.statusText}`,
      }
    }
  } catch (err) {
    console.error('Failed to parse response:', err)
    return {
      error: 'Failed to parse server response',
      message: 'Failed to parse server response',
    }
  }
}

/**
 * Saves image and/or title to backend and updates mission
 */
async function saveImage(): Promise<void> {
  if (!editingMission.value) return

  isUploading.value = true
  uploadError.value = ''
  uploadSuccess.value = ''

  try {
    const formData = new FormData()
    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    }
    formData.append('missionId', editingMission.value.id)
    formData.append('missionTitle', editingMission.value.name)
    formData.append('newTitle', editingTitle.value)
    formData.append('newDescription', editingDescription.value)
    formData.append('newDate', editingDate.value)
    formData.append('newRocketType', editingRocketType.value)
    formData.append('newMissionType', editingMissionType.value)

    console.log('Sending update to backend:', {
      missionId: editingMission.value.id,
      hasFile: !!selectedFile.value,
      newTitle: editingTitle.value,
      newDescription: editingDescription.value,
      newDate: editingDate.value,
      newRocketType: editingRocketType.value,
      newMissionType: editingMissionType.value,
    })

    // Use full API URL pointing to Flask backend on port 5000
    const response = await fetch(`${API_BASE_URL}/api/admin/upload-image`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })

    // Safely parse response as JSON with fallback
    const data = await parseResponseJson(response)

    console.log('Response from backend:', {
      status: response.status,
      statusText: response.statusText,
      data: data,
    })

    if (!response.ok) {
      // Use message field if available, otherwise use error field or generic message
      uploadError.value = data.message || data.error || 'Failed to upload image'

      // Log more details for debugging
      if (!response.ok) {
        console.error('Upload failed:', {
          status: response.status,
          statusText: response.statusText,
          data: data,
        })
      }
      return
    }

    // Update the mission's image URL, title, description, and date with the new values
    if (editingMission.value?.id) {
      if (data.imagePath) {
        editingMission.value.image = data.imagePath
      }
      editingMission.value.name = editingTitle.value
      editingMission.value.description = editingDescription.value
      editingMission.value.date = editingDate.value

      const missionsList = missions.value
      if (missionsList) {
        const missionIndex = missionsList.findIndex((m) => m.id === editingMission.value!.id)
        if (missionIndex !== -1 && missionsList[missionIndex]) {
          if (data.imagePath) {
            missionsList[missionIndex].image = data.imagePath
          }
          missionsList[missionIndex].name = editingTitle.value
          missionsList[missionIndex].description = editingDescription.value
          missionsList[missionIndex].date = editingDate.value
        }
      }
    }

    uploadSuccess.value = 'Mission successfully updated'

    // Close modal after 1.5 seconds
    setTimeout(() => {
      closeEditModal()
    }, 1500)
  } catch (err) {
    console.error('Upload error details:', err)
    if (err instanceof TypeError) {
      uploadError.value =
        'Network error: Cannot connect to server. Make sure the backend is running on http://localhost:5000'
    } else {
      uploadError.value = err instanceof Error ? err.message : 'An error occurred during upload'
    }
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

    // Redirect to homepage
    await router.push({ name: 'home' })
  } catch (err) {
    console.error('Logout error:', err)
  } finally {
    isLoading.value = false
  }
}

/**
 * On component mount, load missions from JSON
 */
onMounted(() => {
  missions.value = loadMissions()
})
</script>

<style scoped>
:root {
  --color-text: #333;
  --color-text-dim: #666;
  --color-bg: #f5f5f5;
  --color-bg-raised: #ffffff;
  --color-border: #e0e0e0;
  --color-accent: #0ea5e9;
  --radius: 8px;
}

.admin-container {
  min-height: 100vh;
  background: var(--color-bg);
}

.admin-header {
  background: var(--color-bg-raised);
  border-bottom: 1px solid var(--color-border);
  padding: 20px 0;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.admin-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text);
}

.logout-btn {
  background: var(--color-accent);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
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

.mission-gallery__header {
  margin-top: 40px;
  margin-left: 20px;
  margin-right: 20px;
  display: flex;
  justify-content: flex-end;
}

.add-mission-btn {
  background: var(--color-accent);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.add-mission-btn:hover {
  opacity: 0.8;
}

.mission-gallery__status {
  margin-top: 32px;
  color: var(--color-text-dim);
  font-size: 14px;
}

.mission-gallery__grid {
  margin-top: 20px;
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

.mission-card__action-buttons {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.mission-card__image-wrapper:hover .mission-card__action-buttons {
  opacity: 1;
}

.mission-card__edit-btn {
  background: rgba(10, 165, 233, 0.9);
  color: white;
  border: none;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mission-card__edit-btn:hover {
  background: rgba(10, 165, 233, 1);
}

.mission-card__delete-btn {
  background: rgba(220, 38, 38, 0.9);
  color: white;
  border: none;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mission-card__delete-btn:hover {
  background: rgba(220, 38, 38, 1);
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

.modal--confirm {
  max-width: 420px;
}

.modal__confirm-text {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text);
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

.modal__required {
  color: #dc2626;
}

.modal__field-error {
  margin: 6px 0 0 0;
  color: #dc2626;
  font-size: 13px;
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

.modal__btn--delete {
  background: #dc2626;
  color: white;
}

.modal__btn--delete:hover:not(:disabled) {
  opacity: 0.9;
}

.modal__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal__title-section {
  margin-bottom: 24px;
}

.modal__title-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modal__title-input {
  display: block;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.modal__title-input:focus {
  outline: none;
  border-color: var(--color-cyan);
  box-shadow: 0 0 0 2px rgba(79, 209, 255, 0.1);
}

.modal__title-input::placeholder {
  color: var(--color-text-dim);
}

.modal__description-section {
  margin-top: 20px;
}

.modal__description-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modal__description-input {
  display: block;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.5;
  transition: border-color 0.2s ease;
  resize: vertical;
}

.modal__description-input:focus {
  outline: none;
  border-color: var(--color-cyan);
  box-shadow: 0 0 0 2px rgba(79, 209, 255, 0.1);
}

.modal__description-input::placeholder {
  color: var(--color-text-dim);
}

.modal__date-section {
  margin-top: 20px;
}

.modal__date-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modal__date-input {
  display: block;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.modal__date-input:focus {
  outline: none;
  border-color: var(--color-cyan);
  box-shadow: 0 0 0 2px rgba(79, 209, 255, 0.1);
}

.modal__date-input::placeholder {
  color: var(--color-text-dim);
}

.modal__rocket-type-section {
  margin-top: 20px;
}

.modal__rocket-type-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modal__rocket-type-input {
  display: block;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.modal__rocket-type-input:focus {
  outline: none;
  border-color: var(--color-cyan);
  box-shadow: 0 0 0 2px rgba(79, 209, 255, 0.1);
}

.modal__rocket-type-input::placeholder {
  color: var(--color-text-dim);
}

.modal__mission-type-section {
  margin-top: 20px;
}

.modal__mission-type-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modal__mission-type-input {
  display: block;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.modal__mission-type-input:focus {
  outline: none;
  border-color: var(--color-cyan);
  box-shadow: 0 0 0 2px rgba(79, 209, 255, 0.1);
}

.modal__mission-type-input::placeholder {
  color: var(--color-text-dim);
}
</style>
