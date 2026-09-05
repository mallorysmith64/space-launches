<template>
  <header class="nav">
    <div class="nav__inner container">
      <router-link to="/" class="nav__brand" @click="closeMenu">
        <span class="nav__brand-text">SpaceX Launches <span class="dim"></span></span>
      </router-link>

      <button
        class="nav__toggle"
        @click="open = !open"
        :aria-expanded="open"
        aria-label="Toggle navigation"
      >
        <span :class="{ 'is-open': open }"></span>
      </button>

      <nav class="nav__links" :class="{ 'is-open': open }">
        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="nav__link"
          @click="closeMenu"
        >
          {{ link.label }}
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script lang="ts">
export default {
  name: 'AppNavbar',
}
</script>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const open = ref(false)
const route = useRoute()

function closeMenu() {
  open.value = false
}

// Nav is limited to what an informational SpaceX site actually needs:
// the launch feed (the site's core content), the vehicles that fly the
// missions, and a short primer for first-time visitors.
const allLinks = [{ to: '/about', label: 'About' }]

// Hide About link on admin screen
const links = computed(() => {
  if (route.path.startsWith('/admin')) {
    return []
  }
  return allLinks
})
</script>

<style scoped>
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  z-index: 100;
  /* Fully transparent - background image shows through */
  background: transparent;
}

.nav__inner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2.4em;
}

.nav__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: filter 0.3s ease;
}

.nav__brand:hover {
  filter: drop-shadow(0 0 12px rgba(255, 106, 61, 0.4));
}

.nav__brand-mark {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 7px;
  background: var(--color-accent);
  color: #100905;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 12px;
  box-shadow: 0 0 16px rgba(255, 106, 61, 0.3);
  transition: box-shadow 0.3s ease;
}

.nav__brand-mark:hover {
  box-shadow: 0 0 24px rgba(255, 106, 61, 0.6);
}

.nav__brand-text {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 0.08em;
  color: var(--color-text);
  /* Enhanced text shadow for better contrast against background image */
  text-shadow:
    0 2px 12px rgba(0, 0, 0, 0.6),
    0 0 20px rgba(79, 209, 255, 0.2);
}

.nav__brand-text .dim {
  color: var(--color-text-dim);
}

.nav__links {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav__link {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-text-dim);
  padding: 6px 2px;
  border-bottom: 2px solid transparent;
  transition:
    color 0.15s ease,
    border-color 0.15s ease,
    text-shadow 0.15s ease;
  /* Text shadow for visibility against background */
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.nav__link:hover {
  color: var(--color-text);
  text-shadow:
    0 2px 8px rgba(0, 0, 0, 0.5),
    0 0 12px rgba(79, 209, 255, 0.3);
}

.nav__link.router-link-exact-active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
  text-shadow:
    0 2px 8px rgba(0, 0, 0, 0.5),
    0 0 12px rgba(255, 106, 61, 0.3);
}

.nav__toggle {
  display: none;
  width: 34px;
  height: 34px;
  border: 1px solid rgba(79, 209, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  position: relative;
  transition:
    border-color 0.2s ease,
    background 0.2s ease;
}

.nav__toggle:hover {
  border-color: var(--color-cyan);
  background: rgba(79, 209, 255, 0.08);
}

.nav__toggle span,
.nav__toggle span::before,
.nav__toggle span::after {
  content: '';
  position: absolute;
  left: 8px;
  right: 8px;
  height: 2px;
  background: var(--color-text);
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
}

.nav__toggle span {
  top: 16px;
}

.nav__toggle span::before {
  top: -6px;
}

.nav__toggle span::after {
  top: 6px;
}

.nav__toggle span.is-open {
  background: transparent;
}

.nav__toggle span.is-open::before {
  transform: translateY(6px) rotate(45deg);
}

.nav__toggle span.is-open::after {
  transform: translateY(-6px) rotate(-45deg);
}

@media (max-width: 720px) {
  .nav__toggle {
    display: block;
  }

  .nav__links {
    position: absolute;
    top: var(--nav-height);
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: flex-start;
    gap: 0;
    /* Mobile menu still has a background for readability */
    background: rgba(18, 22, 31, 0.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(79, 209, 255, 0.1);
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.2s ease;
  }

  .nav__links.is-open {
    max-height: 260px;
  }

  .nav__link {
    width: 100%;
    padding: 14px 24px;
    border-bottom: 1px solid rgba(79, 209, 255, 0.05);
    text-shadow: none;
  }
}
</style>
