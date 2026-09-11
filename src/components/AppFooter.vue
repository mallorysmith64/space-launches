<template>
  <footer class="footer">
    <div class="container footer__inner">
      <router-link to="/admin" class="footer__admin-link"> Admin Login </router-link>
    </div>
  </footer>
</template>

<script setup lang="ts"></script>

<style scoped>
.footer {
  background: var(--color-bg-raised);
  border-top: 1px solid var(--color-border);
  margin-top: 80px;
  padding: 40px 20px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
}

.footer__inner {
  display: flex;
  justify-content: flex-start;
}

.footer__admin-link {
  color: var(--color-accent, #ff6a3d);
  text-decoration: none;
  font-size: 14px;
  transition: opacity 0.2s ease;
}

.footer__admin-link:hover {
  opacity: 0.8;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .footer {
    padding: 30px 20px;
    margin-top: 60px;
  }

  .footer__admin-link {
    font-size: 13px;
  }
}
</style>
