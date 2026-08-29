<template>
  <div style="padding: 40px; max-width: 600px; margin: 0 auto;">
    <h1>Flask Connection Test</h1>
    
    <div style="margin: 20px 0; padding: 20px; background: #f0f0f0; border-radius: 8px;">
      <h2>Step 1: Test Basic Connection</h2>
      <button @click="testConnection" style="padding: 10px 20px; font-size: 16px;">
        {{ connectionLoading ? 'Testing...' : 'Test Flask Connection' }}
      </button>
      <pre v-if="connectionResult" style="background: #fff; padding: 10px; border-radius: 4px; overflow-x: auto;">{{ connectionResult }}</pre>
    </div>

    <div style="margin: 20px 0; padding: 20px; background: #f0f0f0; border-radius: 8px;">
      <h2>Step 2: Test Login</h2>
      <div>
        <input v-model="testUsername" type="text" placeholder="Username" style="padding: 8px; margin: 5px; width: 200px;" />
        <input v-model="testPassword" type="password" placeholder="Password" style="padding: 8px; margin: 5px; width: 200px;" />
      </div>
      <button @click="testLogin" style="padding: 10px 20px; font-size: 16px; margin-top: 10px;">
        {{ loginLoading ? 'Logging in...' : 'Test Login' }}
      </button>
      <pre v-if="loginResult" style="background: #fff; padding: 10px; border-radius: 4px; overflow-x: auto; color: #333;">{{ loginResult }}</pre>
    </div>

    <div style="margin: 20px 0; padding: 20px; background: #f0f0f0; border-radius: 8px;">
      <h2>Step 3: Browser Console</h2>
      <p>Open DevTools (F12) → Console tab to see detailed logs</p>
      <button @click="showConsoleHelp" style="padding: 10px 20px; font-size: 16px;">
        How to Use DevTools
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const connectionLoading = ref(false)
const connectionResult = ref('')
const loginLoading = ref(false)
const loginResult = ref('')
const testUsername = ref('admin')
const testPassword = ref('password')

async function testConnection() {
  connectionLoading.value = true
  connectionResult.value = ''

  try {
    console.log('🔍 Testing connection to http://localhost:5000/api/admin/status')
    
    const response = await fetch('http://localhost:5000/api/admin/status', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    })

    console.log('Response status:', response.status)
    console.log('Response headers:', {
      contentType: response.headers.get('content-type'),
    })

    const text = await response.text()
    console.log('Response text:', text)

    const data = JSON.parse(text)
    connectionResult.value = JSON.stringify(data, null, 2)
    console.log('✅ Connection successful!')
  } catch (err: any) {
    console.error('❌ Connection failed:', err)
    connectionResult.value = `ERROR: ${err.message}\n\nStack: ${err.stack}`
  } finally {
    connectionLoading.value = false
  }
}

async function testLogin() {
  loginLoading.value = true
  loginResult.value = ''

  try {
    console.log('🔐 Testing login with:', {
      username: testUsername.value,
      password: testPassword.value,
    })

    const response = await fetch('http://localhost:5000/api/admin/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        username: testUsername.value,
        password: testPassword.value,
      }),
    })

    console.log('Response status:', response.status)
    console.log('Response headers:', {
      contentType: response.headers.get('content-type'),
      setCookie: response.headers.get('set-cookie'),
    })

    const text = await response.text()
    console.log('Response text:', text)

    // Log what we're about to parse
    console.log('Text length:', text.length)
    console.log('Text is empty?', text === '')
    console.log('Text starts with:', text.substring(0, 50))

    if (!text) {
      loginResult.value = 'ERROR: Empty response from server'
      return
    }

    const data = JSON.parse(text)
    loginResult.value = JSON.stringify(data, null, 2)
    console.log('✅ Login successful!')
  } catch (err: any) {
    console.error('❌ Login failed:', err)
    loginResult.value = `ERROR: ${err.message}\n\nThis usually means the response was empty or invalid JSON`
  } finally {
    loginLoading.value = false
  }
}

function showConsoleHelp() {
  alert(`
How to use Browser DevTools:

1. Press F12 to open DevTools
2. Click the "Console" tab
3. Click one of the test buttons above
4. Watch the console for detailed logs
5. Look for messages starting with 🔍, 🔐, ✅, or ❌

The console will show:
- What URL is being called
- Response status code
- Response content
- Any error messages

Copy the console output if you need help debugging!
  `.trim())
}
</script>
