<template>
  <header class="nav">
    <div class="nav__inner container">
      <router-link to="/" class="nav__brand" @click="closeMenu">
        <span class="nav__brand-mark">SX</span>
        <span class="nav__brand-text">SPACEX <span class="dim">// MISSIONS</span></span>
      </router-link>

      <button class="nav__toggle" @click="open = !open" :aria-expanded="open" aria-label="Toggle navigation">
        <span :class="{ 'is-open': open }"></span>
      </button>

      <nav class="nav__links" :class="{ 'is-open': open }">
        <router-link v-for="link in links" :key="link.to" :to="link.to" class="nav__link" @click="closeMenu">
          {{ link.label }}
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const open = ref(false)
function closeMenu() {
  open.value = false
}

// Nav is limited to what an informational SpaceX site actually needs:
// the launch feed (the site's core content), the vehicles that fly the
// missions, and a short primer for first-time visitors.
const links = [
  { to: '/', label: 'Home' },
  { to: '/launches', label: 'Launches' },
  { to: '/rockets', label: 'Rockets' },
  { to: '/about', label: 'About' }
]
</script>

<style scoped>
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  z-index: 100;
  background: rgba(10, 13, 18, 0.82);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
}

.nav__inner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav__brand {
  display: flex;
  align-items: center;
  gap: 10px;
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
}

.nav__brand-text {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 0.08em;
  color: var(--color-text);
}
.nav__brand-text .dim { color: var(--color-text-dim); }

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
  transition: color 0.15s ease, border-color 0.15s ease;
}

.nav__link:hover {
  color: var(--color-text);
}

.nav__link.router-link-exact-active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

.nav__toggle {
  display: none;
  width: 34px;
  height: 34px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  position: relative;
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
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.nav__toggle span { top: 16px; }
.nav__toggle span::before { top: -6px; }
.nav__toggle span::after { top: 6px; }
.nav__toggle span.is-open { background: transparent; }
.nav__toggle span.is-open::before { transform: translateY(6px) rotate(45deg); }
.nav__toggle span.is-open::after { transform: translateY(-6px) rotate(-45deg); }

@media (max-width: 720px) {
  .nav__toggle { display: block; }

  .nav__links {
    position: absolute;
    top: var(--nav-height);
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: flex-start;
    gap: 0;
    background: var(--color-bg-raised);
    border-bottom: 1px solid var(--color-border);
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.2s ease;
  }
  .nav__links.is-open { max-height: 260px; }
  .nav__link { width: 100%; padding: 14px 24px; border-bottom: 1px solid var(--color-border); }
}
</style>
