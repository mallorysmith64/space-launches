<template>
  <section class="carousel-section">
    <div class="container carousel-section__head">
      <div>
        <p class="eyebrow">Launch feed</p>
        <h2 class="section-title">Recent &amp; upcoming flights</h2>
      </div>
      <div class="carousel-section__nav">
        <button class="nav-btn" @click="scrollByCard(-1)" :disabled="atStart" aria-label="Previous launch">←</button>
        <button class="nav-btn" @click="scrollByCard(1)" :disabled="atEnd" aria-label="Next launch">→</button>
      </div>
    </div>

    <div v-if="error" class="container carousel-state">
      <p>Couldn't load launch data right now. <button class="btn btn--ghost" @click="load">Retry</button></p>
    </div>

    <div
      v-else
      class="track"
      ref="trackEl"
      role="region"
      aria-label="Launch carousel, scrollable"
      tabindex="0"
      @keydown.left="scrollByCard(-1)"
      @keydown.right="scrollByCard(1)"
      @pointerenter="paused = true"
      @pointerleave="paused = false"
      @focusin="paused = true"
      @focusout="paused = false"
    >
      <template v-if="loading">
        <div class="track__item track__item--skeleton" v-for="n in 5" :key="n">
          <div class="skeleton-card"></div>
        </div>
      </template>

      <template v-else>
        <div class="track__item" v-for="launch in launches" :key="launch.id">
          <LaunchCard :launch="launch" />
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import LaunchCard from './LaunchCard.vue'

const launches = ref([])
const loading = ref(true)
const error = ref(false)
const trackEl = ref(null)
const atStart = ref(true)
const atEnd = ref(false)
const paused = ref(false)

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
let autoplayTimer = null
let resizeObserver = null

async function load() {
  loading.value = true
  error.value = false
  try {
    const res = await fetch('/api/launches?type=all&limit=20')
    if (!res.ok) throw new Error('bad response')
    const data = await res.json()
    launches.value = data.results ?? []
  } catch {
    error.value = true
  } finally {
    loading.value = false
    await nextTick()
    updateEdgeState()
  }
}

function cardWidth() {
  const first = trackEl.value?.querySelector('.track__item')
  return first ? first.getBoundingClientRect().width + 16 : 320
}

function scrollByCard(direction) {
  if (!trackEl.value) return
  trackEl.value.scrollBy({ left: direction * cardWidth(), behavior: 'smooth' })
}

function updateEdgeState() {
  const el = trackEl.value
  if (!el) return
  atStart.value = el.scrollLeft <= 4
  atEnd.value = el.scrollLeft + el.clientWidth >= el.scrollWidth - 4
}

function autoplayTick() {
  if (paused.value || !trackEl.value) return
  if (atEnd.value) {
    trackEl.value.scrollTo({ left: 0, behavior: 'smooth' })
  } else {
    scrollByCard(1)
  }
}

onMounted(async () => {
  await load()
  trackEl.value?.addEventListener('scroll', updateEdgeState, { passive: true })

  // Native scroll-snap + CSS handles the heavy lifting; JS only nudges
  // autoplay every few seconds, and never runs if the user prefers
  // reduced motion or already has focus/pointer on the track.
  if (!prefersReducedMotion) {
    autoplayTimer = setInterval(autoplayTick, 4500)
  }

  resizeObserver = new ResizeObserver(updateEdgeState)
  if (trackEl.value) resizeObserver.observe(trackEl.value)
})

onBeforeUnmount(() => {
  trackEl.value?.removeEventListener('scroll', updateEdgeState)
  if (autoplayTimer) clearInterval(autoplayTimer)
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.carousel-section {
  padding: 56px 0 80px;
}

.carousel-section__head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.carousel-section__nav {
  display: flex;
  gap: 8px;
}

.nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-raised);
  color: var(--color-text);
  font-family: var(--font-mono);
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease, opacity 0.15s ease;
}
.nav-btn:hover:not(:disabled) { border-color: var(--color-cyan); color: var(--color-cyan); }
.nav-btn:disabled { opacity: 0.35; cursor: default; }

.track {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding: 4px 24px 12px;
  scrollbar-width: thin;
  outline: none;
}
.track:focus-visible { box-shadow: inset 0 0 0 2px var(--color-cyan); border-radius: 8px; }

.track::-webkit-scrollbar { height: 6px; }
.track::-webkit-scrollbar-thumb { background: var(--color-border); border-radius: 4px; }

.track__item {
  flex: 0 0 auto;
  width: min(300px, 82vw);
  scroll-snap-align: start;
}

.skeleton-card {
  height: 220px;
  border-radius: var(--radius);
  background: linear-gradient(90deg, var(--color-bg-raised) 0%, var(--color-bg-raised-2) 50%, var(--color-bg-raised) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.3s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.carousel-state {
  color: var(--color-text-dim);
  font-family: var(--font-mono);
  font-size: 14px;
}
</style>
