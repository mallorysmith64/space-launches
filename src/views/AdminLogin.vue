<template>
  <div class="admin-login">
    <div class="login-container">
      <h1 class="login-title">Admin Login</h1>

      <form action="/admin" method="POST" class="login-form">
        <div class="form-group">
          <label for="username" class="form-label">Username</label>
          <input
            id="username"
            name="username"
            type="text"
            class="form-input"
            placeholder="Enter your username"
            required
          />
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            class="form-input"
            placeholder="Enter your password"
            required
          />
        </div>

        <button type="submit" class="login-button">Login</button>
      </form>

      <div class="login-footer">
        <router-link to="/" class="back-link">Back to Home</router-link>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: 'AdminLogin',
}
</script>

<style scoped>
.admin-login {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--nav-height));
  padding: 32px 16px;
  background: linear-gradient(135deg, rgba(10, 13, 18, 0.8) 0%, rgba(18, 22, 31, 0.8) 100%);
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: rgba(18, 22, 31, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(79, 209, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.login-title {
  margin: 0 0 32px;
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--color-text);
  text-align: center;
  text-shadow: 0 0 20px rgba(79, 209, 255, 0.15);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-text-dim);
}

.form-input {
  padding: 12px 16px;
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--color-text);
  background: rgba(79, 209, 255, 0.05);
  border: 1px solid rgba(79, 209, 255, 0.2);
  border-radius: 6px;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-cyan);
  background: rgba(79, 209, 255, 0.1);
  box-shadow: 0 0 12px rgba(79, 209, 255, 0.2);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.login-button {
  padding: 12px 24px;
  font-family: var(--font-mono);
  font-size: 13px;
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

.login-button:hover {
  box-shadow: 0 0 24px rgba(255, 106, 61, 0.5);
  transform: translateY(-2px);
}

.login-button:active {
  transform: translateY(0);
}

.login-footer {
  text-align: center;
}

.back-link {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-text-dim);
  text-decoration: none;
  transition:
    color 0.2s ease,
    text-shadow 0.2s ease;
}

.back-link:hover {
  color: var(--color-text);
  text-shadow: 0 0 12px rgba(79, 209, 255, 0.3);
}

@media (max-width: 720px) {
  .admin-login {
    min-height: calc(100vh - var(--nav-height));
    padding: 16px;
  }

  .login-container {
    padding: 32px 24px;
  }

  .login-title {
    font-size: 24px;
    margin-bottom: 24px;
  }
}
</style>
