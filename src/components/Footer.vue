<template>
  <footer class="footer">
    <div class="footer__inner container">
      <div class="footer__content">
        <p class="footer__text">Spacex Launches</p>
      </div>
      <nav class="footer__nav">
        <router-link to="/admin" class="footer__link"> Admin Login </router-link>
      </nav>
    </div>
  </footer>
</template>

<script lang="ts">
export default {
  name: 'AppFooter',
}
</script>

<style scoped>
.footer {
  position: relative;
  margin-top: auto;
  background: rgba(10, 13, 18, 0.25);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-top: 1px solid rgba(79, 209, 255, 0.1);
}

.footer__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32px 0;
  min-height: 80px;
}

.footer__content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.footer__text {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 0.08em;
  color: var(--color-text-dim);
  margin: 0;
}

.footer__nav {
  display: flex;
  align-items: center;
  gap: 28px;
}

.footer__link {
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
  text-decoration: none;
}

.footer__link:hover {
  color: var(--color-text);
  text-shadow: 0 0 12px rgba(79, 209, 255, 0.3);
}

.footer__link.router-link-exact-active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
  text-shadow: 0 0 12px rgba(255, 106, 61, 0.3);
}

@media (max-width: 720px) {
  .footer__inner {
    flex-direction: column;
    gap: 16px;
    padding: 24px 0;
    min-height: auto;
  }

  .footer__content {
    width: 100%;
    justify-content: center;
  }

  .footer__nav {
    width: 100%;
    justify-content: center;
  }

  .footer__link {
    padding: 8px 4px;
  }
}
</style>
