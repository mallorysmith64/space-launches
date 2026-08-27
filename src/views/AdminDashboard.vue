<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h1 class="dashboard-title">Admin Dashboard</h1>
      <button @click="handleLogout" class="logout-button">Logout</button>
    </div>

    <div class="dashboard-content">
      <p class="welcome-message">Welcome to the Admin Portal</p>
      <p class="subtitle">You are logged in successfully.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const handleLogout = async () => {
  // Navigate to Flask logout endpoint
  window.location.href = 'http://localhost:5000/admin/logout'
}
</script>

<style scoped>
.admin-dashboard {
  min-height: calc(100vh - var(--nav-height));
  padding: 40px 20px;
  background: linear-gradient(135deg, rgba(10, 13, 18, 0.8) 0%, rgba(18, 22, 31, 0.8) 100%);
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(79, 209, 255, 0.2);
}

.dashboard-title {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--color-text);
  text-shadow: 0 0 20px rgba(79, 209, 255, 0.15);
}

.logout-button {
  padding: 10px 20px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #100905;
  background: var(--color-accent);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition:
    box-shadow 0.3s ease,
    transform 0.2s ease;
  box-shadow: 0 0 16px rgba(255, 106, 61, 0.3);
}

.logout-button:hover {
  box-shadow: 0 0 24px rgba(255, 106, 61, 0.5);
  transform: translateY(-2px);
}

.logout-button:active {
  transform: translateY(0);
}

.dashboard-content {
  max-width: 600px;
  padding: 40px;
  background: rgba(18, 22, 31, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(79, 209, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.welcome-message {
  margin: 0 0 16px;
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
  text-shadow: 0 0 12px rgba(79, 209, 255, 0.1);
}

.subtitle {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 14px;
  letter-spacing: 0.04em;
  color: var(--color-text-dim);
}

@media (max-width: 720px) {
  .admin-dashboard {
    padding: 24px 16px;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 24px;
  }

  .dashboard-title {
    font-size: 24px;
  }

  .dashboard-content {
    padding: 24px;
  }

  .welcome-message {
    font-size: 18px;
  }
}
</style>
