<template>
  <article class="card">
    <div class="card__patch">
      <img
        v-if="launch.patch_small"
        :src="launch.patch_small"
        :alt="`${launch.name} mission patch`"
        loading="lazy"
        decoding="async"
        width="88"
        height="88"
      />
      <div v-else class="card__patch-fallback" aria-hidden="true">SX</div>
    </div>

    <div class="card__body">
      <span class="badge" :class="statusClass">{{ statusLabel }}</span>
      <h3 class="card__title">{{ launch.name }}</h3>
      <p class="card__meta">{{ formattedDate }} · {{ launch.rocket_name }}</p>
      <p class="card__flight">Flight #{{ launch.flight_number ?? '—' }}</p>

      <a
        v-if="launch.webcast || launch.article"
        class="card__link"
        :href="launch.webcast || launch.article"
        target="_blank"
        rel="noopener noreferrer"
      >
        {{ launch.webcast ? 'Watch webcast' : 'Read more' }} →
      </a>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  launch: { type: Object, required: true }
})

const formattedDate = computed(() => {
  if (!props.launch.date_utc) return 'Date TBD'
  const d = new Date(props.launch.date_utc)
  const opts = { year: 'numeric', month: 'short', day: 'numeric' }
  if (props.launch.date_precision && props.launch.date_precision !== 'hour') {
    return d.toLocaleDateString(undefined, opts)
  }
  return d.toLocaleDateString(undefined, opts) + ', ' + d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
})

const statusLabel = computed(() => {
  if (props.launch.upcoming) return 'Upcoming'
  if (props.launch.success === true) return 'Success'
  if (props.launch.success === false) return 'Failed'
  return 'Unknown'
})

const statusClass = computed(() => {
  if (props.launch.upcoming) return 'badge--upcoming'
  if (props.launch.success === true) return 'badge--success'
  if (props.launch.success === false) return 'badge--fail'
  return ''
})
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: var(--color-bg-raised);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 20px;
  height: 100%;
}

.card__patch {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-bg-raised-2);
  display: grid;
  place-items: center;
}
.card__patch img { width: 100%; height: 100%; object-fit: contain; }
.card__patch-fallback {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-text-dim);
}

.card__title {
  font-size: 17px;
  font-weight: 600;
  margin-top: 8px;
  line-height: 1.3;
}

.card__meta {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-text-dim);
  margin: 6px 0 0;
}

.card__flight {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-text-dim);
  opacity: 0.7;
  margin: 2px 0 0;
}

.card__link {
  margin-top: auto;
  padding-top: 10px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-cyan);
}
.card__link:hover { text-decoration: underline; }
</style>
