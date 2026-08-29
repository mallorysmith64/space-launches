<template>
  <div class="admin-login">
    <div class="login-container">
      <div class="login-card">
        <h1 class="login-title">Admin Access</h1>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username" class="form-label">Username</label>
            <input
              id="username"
              v-model="username"
              type="text"
              class="form-input"
              placeholder="admin"
              required
              :disabled="loading"
              autocomplete="username"
            />
          </div>

          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              class="form-input"
              placeholder="••••••••"
              required
              :disabled="loading"
              autocomplete="current-password"
            />
          </div>

          <div v-if="error" class="error-message"><strong>Error:</strong> {{ error }}</div>

          <div v-if="debugInfo" class="debug-info">
            {{ debugInfo }}
          </div>

          <button
            type="submit"
            class="btn btn--primary"
            :disabled="loading || !username || !password"
          >
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>

        <div class="login-hint">
          <p><strong>Demo credentials:</strong></p>
          <p>Username: <code>admin</code></p>
          <p>Password: <code>password</code></p>
        </div>

        <div class="server-status">
          <p>
            <span :class="serverStatusClass">●</span>
            Flask server: {{ serverStatus }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const debugInfo = ref('')
const serverStatus = ref('checking...')

const serverStatusClass = computed(() => {
  if (serverStatus.value === 'online') return 'status-online'
  if (serverStatus.value === 'offline') return 'status-offline'
  return 'status-checking'
})

// Check if Flask server is running on startup
async function checkServerStatus() {
  try {
    const response = await fetch('http://localhost:5000/api/admin/status', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    })
    serverStatus.value = response.ok ? 'online' : 'offline'
  } catch (err) {
    serverStatus.value = 'offline'
    console.error('Server status check failed:', err)
  }
}

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = 'Please enter username and password'
    return
  }

  loading.value = true
  error.value = ''
  debugInfo.value = ''

  try {
    const credentials = {
      username: username.value,
      password: password.value,
    }

    const response = await fetch('http://localhost:5000/api/admin/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Critical: sends session cookies
      body: JSON.stringify(credentials),
    })

    // Check if response has content
    const responseText = await response.text()

    // Try to parse as JSON
    let data
    try {
      data = JSON.parse(responseText)
    } catch (parseErr) {
      error.value = `Server returned invalid JSON. Status: ${response.status}`
      serverStatus.value = 'offline'
      return
    }

    if (response.ok && data.status === 'success') {
      // Login successful - redirect to dashboard
      router.push('/admin/dashboard')
    } else {
      error.value = data.message || 'Login failed'
    }
  } catch (err: any) {
    console.error('Login error:', err)

    // Provide specific error messages
    if (err.message.includes('Failed to fetch')) {
      error.value =
        "Cannot connect to Flask server. Make sure it's running on http://localhost:5000"
      serverStatus.value = 'offline'
    } else if (err instanceof TypeError) {
      error.value = `Network error: ${err.message}`
      serverStatus.value = 'offline'
    } else {
      error.value = `Error: ${err.message || 'Unknown error'}`
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkServerStatus()
})
</script>

<style scoped>
.admin-login {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background:
    linear-gradient(135deg, rgba(10, 13, 18, 0.4) 0%, rgba(20, 25, 40, 0.3) 100%),
    url('https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920&q=80') center/cover
      no-repeat;
  background-attachment: fixed;
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-card {
  background: var(--color-bg-raised);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 40px;
  backdrop-filter: blur(12px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 32px;
  text-align: center;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-cyan) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-dim);
}

.form-input {
  padding: 12px 16px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 14px;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-cyan);
  box-shadow: 0 0 0 3px rgba(79, 209, 255, 0.1);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  padding: 12px 16px;
  background: rgba(255, 84, 112, 0.1);
  border: 1px solid rgba(255, 84, 112, 0.3);
  border-radius: 8px;
  color: var(--color-fail);
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
}

.debug-info {
  padding: 10px 14px;
  background: rgba(79, 209, 255, 0.08);
  border: 1px solid rgba(79, 209, 255, 0.2);
  border-radius: 8px;
  color: var(--color-cyan);
  font-size: 12px;
  font-family: var(--font-mono);
  line-height: 1.4;
}

.login-hint {
  margin-top: 24px;
  padding: 16px;
  background: rgba(58, 219, 118, 0.05);
  border: 1px solid rgba(58, 219, 118, 0.2);
  border-radius: 8px;
}

.login-hint p {
  margin: 0;
  color: var(--color-text-dim);
  font-size: 12px;
  font-family: var(--font-mono);
  line-height: 1.6;
}

.login-hint code {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--color-cyan);
  font-weight: 600;
}

.server-status {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(18, 22, 31, 0.5);
  border-radius: 8px;
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--color-text-dim);
}

.server-status p {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-online {
  color: var(--color-success);
  font-size: 16px;
}

.status-offline {
  color: var(--color-fail);
  font-size: 16px;
  animation: pulse 1.5s ease-in-out infinite;
}

.status-checking {
  color: var(--color-text-dim);
  font-size: 16px;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 0.04em;
  padding: 12px 20px;
  border-radius: 10px;
  border: 1px solid transparent;
  cursor: pointer;
  transition:
    transform 0.15s ease,
    background 0.15s ease,
    box-shadow 0.15s ease;
  width: 100%;
}

.btn:active:not(:disabled) {
  transform: scale(0.97);
}

.btn--primary {
  background: var(--color-accent);
  color: #100905;
  font-weight: 600;
  box-shadow: 0 0 20px rgba(255, 106, 61, 0.25);
}

.btn--primary:hover:not(:disabled) {
  background: #ff8158;
  box-shadow: 0 0 30px rgba(255, 106, 61, 0.4);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 500px) {
  .login-card {
    padding: 28px;
  }

  .login-title {
    font-size: 22px;
    margin-bottom: 24px;
  }

  .login-hint {
    margin-top: 20px;
    padding: 12px;
  }
}
</style>
