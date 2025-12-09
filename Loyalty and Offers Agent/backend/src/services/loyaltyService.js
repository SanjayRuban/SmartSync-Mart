// src/services/loyaltyService.js
const pool = require('../db');
const { getTotalStock } = require('./inventoryService');

async function getCustomer(customerId) {
  const [rows] = await pool.query('SELECT * FROM customers WHERE id = ?', [customerId]);
  return rows[0];
}

async function getCart(cartId) {
  const [rows] = await pool.query(
    'SELECT ci.*, p.category FROM cart_items ci JOIN products p ON ci.sku = p.sku WHERE cart_id = ?',
    [cartId]
  );
  return rows;
}

async function getPromotion(code) {
  const [rows] = await pool.query('SELECT * FROM promotions WHERE code = ?', [code]);
  return rows[0];
}

async function computePricing({ customerId, cartId, promoCode = null, applyLoyalty = true }) {
  const customer = await getCustomer(customerId);
  const items = await getCart(cartId);
  let subtotal = 0;
  items.forEach(i => {
    subtotal += parseFloat(i.price_at_add) * i.qty;
  });

  // Validate promo
  let promoDiscount = 0;
  let promo = null;
  if (promoCode) {
    promo = await getPromotion(promoCode);
    if (promo) {
      const minOK = (!promo.min_cart_value) || subtotal >= parseFloat(promo.min_cart_value);
      const notExpired = !promo.expires_at || new Date(promo.expires_at) > new Date();
      if (minOK && notExpired) {
        if (promo.type === 'PERCENT') {
          if (promo.category_restriction) {
            let eligible = 0;
            items.forEach(i => {
              if (i.category && i.category.toLowerCase() === promo.category_restriction.toLowerCase()) {
                eligible += parseFloat(i.price_at_add) * i.qty;
              }
            });
            promoDiscount = eligible * (promo.value / 100.0);
          } else {
            promoDiscount = subtotal * (promo.value / 100.0);
          }
        } else if (promo.type === 'FLAT') {
          promoDiscount = parseFloat(promo.value);
        }
      } else {
        promo = null; // treat as invalid
      }
    }
  }

  // Loyalty application
  let loyaltyApplied = 0;
  if (applyLoyalty && customer) {
    const tierCaps = { BRONZE: 0.05, SILVER: 0.10, GOLD: 0.20 };
    const capPct = tierCaps[customer.tier] || 0.05;
    const maxAllowed = subtotal * capPct;
    loyaltyApplied = Math.min(customer.loyalty_points || 0, Math.floor(maxAllowed));
  }

  // Personalized offer via inventory (simple overstock rule)
  let personalizedOffer = null;
  for (let i of items) {
    const total = await getTotalStock(i.sku);
    if (total >= 100) {
      personalizedOffer = {
        message: 'Add Protein Bar for just ₹49 (clearance offer)',
        sku: 'PBAR50',
        offer_price: 49.0
      };
      break;
    }
  }

  // Final calculation
  const taxableAmount = Math.max(0, subtotal - promoDiscount - loyaltyApplied);
  const tax = Number((0.05 * taxableAmount).toFixed(2));
  const shipping = taxableAmount > 500 ? 0 : 50;
  const finalAmount = Number((taxableAmount + tax + shipping).toFixed(2));

  return {
    subtotal: Number(subtotal.toFixed(2)),
    promo_applied: promo ? promo.code : null,
    promo_discount: Number(promoDiscount.toFixed(2)),
    loyalty_applied: Number(loyaltyApplied.toFixed(2)),
    tax,
    shipping,
    final_amount: finalAmount,
    personalized_offer: personalizedOffer,
    customer: customer || null,
    items
  };
}

module.exports = { computePricing, getCustomer, getCart };
