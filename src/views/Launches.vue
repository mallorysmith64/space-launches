<template>
  <section class="section container">
    <p class="eyebrow">Launch log</p>
    <h1 class="section-title">All missions</h1>
    <p class="section-lede">Browse every tracked SpaceX flight, or filter down to just what's upcoming.</p>

    <div class="tabs" role="tablist">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="tab"
        :class="{ 'tab--active': filter === tab.value }"
        role="tab"
        :aria-selected="filter === tab.value"
        @click="setFilter(tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="error" class="state">
      Couldn't load launch data. <button class="btn btn--ghost" @click="load">Retry</button>
    </div>

    <div v-else class="grid">
      <template v-if="loading">
        <div class="skeleton" v-for="n in 9" :key="n"></div>
      </template>
      <LaunchCard v-else v-for="launch in launches" :key="launch.id" :launch="launch" />
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import LaunchCard from '../components/LaunchCard.vue'

const tabs = [
  { label: 'All', value: 'all' },
  { label: 'Upcoming', value: 'upcoming' },
  { label: 'Past', value: 'past' }
]

const filter = ref('all')
const launches = ref([])
const loading = ref(true)
const error = ref(false)

async function load() {
  loading.value = true
  error.value = false
  try {
    const res = await fetch(`/api/launches?type=${filter.value}&limit=60`)
    if (!res.ok) throw new Error('bad response')
    const data = await res.json()
    launches.value = data.results ?? []
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

function setFilter(value) {
  filter.value = value
}

watch(filter, load)
onMounted(load)
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 8px;
  margin: 32px 0 28px;
}

.tab {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 9px 16px;
  border-radius: 100px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-dim);
  cursor: pointer;
  transition: all 0.15s ease;
}
.tab:hover { color: var(--color-text); }
.tab--active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #100905;
  font-weight: 600;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}

.skeleton {
  height: 220px;
  border-radius: var(--radius);
  background: var(--color-bg-raised);
  border: 1px solid var(--color-border);
}

.state {
  color: var(--color-text-dim);
  font-family: var(--font-mono);
  font-size: 14px;
  margin-top: 24px;
}
</style>
