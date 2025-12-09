// src/routes/loyalty.js
const express = require('express');
const router = express.Router();
const { computePricing } = require('../services/loyaltyService');
const pool = require('../db');

// POST /loyalty/compute
router.post('/compute', async (req, res) => {
  try {
    const { customerId, cartId, promoCode } = req.body;
    if (!customerId || !cartId) {
      return res.status(400).json({ error: 'customerId and cartId required' });
    }
    const result = await computePricing({ customerId, cartId, promoCode, applyLoyalty: true });
    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'pricing error' });
  }
});

// POST /loyalty/apply (after order success) - deduct loyalty points and credit points
router.post('/apply', async (req, res) => {
  try {
    const { customerId, loyalty_used = 0, order_amount = 0 } = req.body;
    if (!customerId) return res.status(400).json({ error: 'customerId required' });

    if (loyalty_used > 0) {
      await pool.query('UPDATE customers SET loyalty_points = GREATEST(0, loyalty_points - ?) WHERE id = ?', [loyalty_used, customerId]);
    }
    const pointsEarned = Math.floor(order_amount / 100);
    if (pointsEarned > 0) {
      await pool.query('UPDATE customers SET loyalty_points = loyalty_points + ? WHERE id = ?', [pointsEarned, customerId]);
    }
    const [rows] = await pool.query('SELECT loyalty_points FROM customers WHERE id = ?', [customerId]);
    res.json({ message: 'Loyalty updated', pointsEarned, currentPoints: rows[0].loyalty_points });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'apply loyalty error' });
  }
});

module.exports = router;
