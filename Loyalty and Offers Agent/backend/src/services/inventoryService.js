// src/services/inventoryService.js
const pool = require('../db');

async function getInventoryBySku(sku) {
  const [rows] = await pool.query('SELECT store, stock FROM inventory WHERE sku = ?', [sku]);
  return rows;
}

async function getTotalStock(sku) {
  const [rows] = await pool.query('SELECT COALESCE(SUM(stock),0) AS total FROM inventory WHERE sku = ?', [sku]);
  return rows[0].total || 0;
}

module.exports = { getInventoryBySku, getTotalStock };
