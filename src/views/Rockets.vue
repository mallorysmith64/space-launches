<template>
  <section class="section container">
    <p class="eyebrow">Vehicle roster</p>
    <h1 class="section-title">Rockets</h1>
    <p class="section-lede">The vehicles behind the missions in the launch log — from the workhorse Falcon 9 to Starship, still in active development.</p>

    <div v-if="error" class="state">
      Couldn't load rocket data. <button class="btn btn--ghost" @click="load">Retry</button>
    </div>

    <div v-else class="grid">
      <template v-if="loading">
        <div class="skeleton" v-for="n in 4" :key="n"></div>
      </template>

      <article class="rocket" v-else v-for="rocket in rockets" :key="rocket.id">
        <img v-if="rocket.image" :src="rocket.image" :alt="rocket.name" loading="lazy" decoding="async" class="rocket__img" />
        <div class="rocket__body">
          <div class="rocket__head">
            <h3>{{ rocket.name }}</h3>
            <span class="badge" :class="rocket.active ? 'badge--success' : ''">
              {{ rocket.active ? 'Active' : 'Retired' }}
            </span>
          </div>
          <p class="rocket__desc">{{ rocket.description }}</p>
          <dl class="rocket__stats">
            <div><dt>Height</dt><dd>{{ rocket.height_m ?? '—' }} m</dd></div>
            <div><dt>Mass</dt><dd>{{ formatMass(rocket.mass_kg) }}</dd></div>
            <div><dt>Success rate</dt><dd>{{ rocket.success_rate_pct ?? '—' }}%</dd></div>
            <div><dt>First flight</dt><dd>{{ rocket.first_flight ?? '—' }}</dd></div>
          </dl>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const rockets = ref([])
const loading = ref(true)
const error = ref(false)

function formatMass(kg) {
  if (!kg) return '—'
  return `${(kg / 1000).toLocaleString()} t`
}

async function load() {
  loading.value = true
  error.value = false
  try {
    const res = await fetch('/api/rockets')
    if (!res.ok) throw new Error('bad response')
    const data = await res.json()
    rockets.value = data.results ?? []
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.grid {
  margin-top: 32px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.rocket {
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-bg-raised);
  overflow: hidden;
}

.rocket__img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.rocket__body { padding: 20px; }

.rocket__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.rocket__head h3 { font-size: 19px; }

.rocket__desc {
  color: var(--color-text-dim);
  font-size: 14px;
  line-height: 1.6;
  margin-top: 10px;
}

.rocket__stats {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px 10px;
}
.rocket__stats dt {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-dim);
}
.rocket__stats dd {
  margin: 4px 0 0;
  font-family: var(--font-mono);
  font-size: 15px;
  color: var(--color-cyan);
}

.skeleton {
  height: 320px;
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
