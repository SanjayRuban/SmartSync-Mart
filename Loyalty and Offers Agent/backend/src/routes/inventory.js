// src/routes/inventory.js
const express = require('express');
const router = express.Router();
const { getInventoryBySku, getTotalStock } = require('../services/inventoryService');

// GET /inventory/sku/:sku
router.get('/sku/:sku', async (req, res) => {
  try {
    const sku = req.params.sku;
    const rows = await getInventoryBySku(sku);
    res.json({ sku, locations: rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'inventory error' });
  }
});

// GET /inventory/sku/:sku/total
router.get('/sku/:sku/total', async (req, res) => {
  try {
    const sku = req.params.sku;
    const total = await getTotalStock(sku);
    res.json({ sku, total });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'inventory error' });
  }
});

module.exports = router;
