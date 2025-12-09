const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: '',
  database: 'retail_agent'
});

// Test connection
pool.getConnection()
  .then(() => console.log("✅ MySQL Connected"))
  .catch(err => console.error("❌ MySQL Connection Failed:", err));

module.exports = pool;
