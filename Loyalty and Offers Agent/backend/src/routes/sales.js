// src/routes/sales.js
const express = require('express');
const router = express.Router();
const axios = require('axios');

// POST /sales/checkout
router.post('/checkout', async (req, res) => {
  try {
    const { customerId, cartId, promoCode } = req.body;
    if (!customerId || !cartId) return res.status(400).json({ error: 'customerId and cartId required' });

    const serverBase = `http://localhost:${process.env.PORT || 3000}`;
    // Call loyalty endpoint (same server)
    const result = (await axios.post(`${serverBase}/loyalty/compute`, { customerId, cartId, promoCode })).data;

    const message = {
      text: `I found ${result.personalized_offer ? 'a special offer and ' : ''}your final payable is ₹${result.final_amount}.`,
      breakdown: result
    };

    res.json({ ok: true, message });
  } catch (err) {
    console.error('Sales checkout error:', err.response ? err.response.data : err.message);
    res.status(500).json({ error: 'sales checkout error' });
  }
});

module.exports = router;
