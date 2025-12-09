// seed_toggle.js
// Simple script to toggle simulation setting via HTTP POST if you want.
// You can ignore this file or use it in tests.
const axios = require('axios');

async function toggle() {
  try {
    const r = await axios.post('http://localhost:4000/api/toggle_failure');
    console.log('Toggled simulateFailure:', r.data);
  } catch (err) {
    console.error(err.message);
  }
}

toggle();
