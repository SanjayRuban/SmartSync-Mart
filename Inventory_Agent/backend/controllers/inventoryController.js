// backend/controllers/inventoryController.js
const db = require('../db');
const { haversineDistance } = require('../utils/geo');
const { computeSuitability } = require('../utils/scoring');

let simulateFailure = false; // toggle via endpoint for demo

async function getAllStores() {
  const [rows] = await db.execute('SELECT * FROM stores');
  return rows;
}

async function getProduct(sku) {
  const [rows] = await db.execute('SELECT * FROM products WHERE sku = ?', [sku]);
  return rows[0];
}

async function getInventoryBySku(sku) {
  const [rows] = await db.execute(
    `SELECT inv.*, s.id as store_id, s.name, s.code, s.lat, s.lng, s.city 
     FROM inventory inv 
     LEFT JOIN stores s ON inv.store_id = s.id 
     WHERE inv.sku = ?`,
    [sku]
  );
  return rows;
}

async function getDemandForSku(sku) {
  const [rows] = await db.execute(
    `SELECT d.*, s.code, s.name, d.store_id 
     FROM demand d 
     LEFT JOIN stores s ON d.store_id = s.id 
     WHERE d.sku = ?`,
    [sku]
  );
  const map = {};
  rows.forEach(r => { map[r.store_id] = r.demand_score; });
  return map;
}

async function inventoryLookup(req, res) {
  try {
    if (simulateFailure) {
      return res.status(503).json({ error: 'Inventory service temporarily unavailable (simulated)' });
    }

    const sku = req.params.sku;
    const lat = req.query.lat ? parseFloat(req.query.lat) : null;
    const lng = req.query.lng ? parseFloat(req.query.lng) : null;
    const preferred_store_code = req.query.preferred_store || null;
    const weights = {
      w_stock: parseFloat(req.query.w_stock) || 2,
      w_demand: parseFloat(req.query.w_demand) || 1,
      w_distance: parseFloat(req.query.w_distance) || 0.5
    };

    const product = await getProduct(sku);
    if (!product) return res.status(404).json({ error: 'SKU not found' });

    const invRows = await getInventoryBySku(sku);
    const demandMap = await getDemandForSku(sku);
    const stores = await getAllStores();

    // Build store map (include online if present)
    const storeMap = {};
    invRows.forEach(r => {
      if (!r.store_id) {
        storeMap['ONLINE_WAREHOUSE'] = {
          store_id: null,
          code: 'ONLINE',
          name: 'Central Warehouse',
          lat: null,
          lng: null,
          city: 'Online',
          qty: r.qty
        };
      } else {
        storeMap[r.store_id] = {
          store_id: r.store_id,
          code: r.code,
          name: r.name,
          lat: r.lat,
          lng: r.lng,
          city: r.city,
          qty: r.qty
        };
      }
    });

    // Ensure all stores present
    stores.forEach(s => {
      if (!storeMap[s.id]) {
        storeMap[s.id] = {
          store_id: s.id,
          code: s.code,
          name: s.name,
          lat: s.lat,
          lng: s.lng,
          city: s.city,
          qty: 0
        };
      }
    });

    const entries = [];
    for (const key of Object.keys(storeMap)) {
      const st = storeMap[key];
      const demand = demandMap[st.store_id] || 1;
      const distanceKm = (st.lat != null && lat != null && lng != null)
        ? haversineDistance(lat, lng, st.lat, st.lng)
        : (st.store_id === null ? 50 : 99999);
      const { score, runoutRisk } = computeSuitability({ stock: st.qty, demand, distanceKm, weights });

      entries.push({
        store_id: st.store_id,
        code: st.code,
        name: st.name,
        city: st.city,
        qty: st.qty,
        demand,
        distanceKm: Number(distanceKm.toFixed(2)),
        score: Number(score.toFixed(3)),
        runoutRisk: Number(runoutRisk.toFixed(3)),
        fulfillment_options: (st.store_id === null) ? ['Ship to Home'] : ['Click & Collect', 'Reserve in Store', 'Ship to Home']
      });
    }

    entries.sort((a,b) => b.score - a.score);

    const best = entries[0] || null;
    const alternatives = entries.slice(1,4);
    const onlineEntry = entries.find(e => e.store_id === null);

    const summary = best
      ? (best.qty > 0
          ? `${best.name} recommended: ${best.qty} available, ${best.distanceKm} km away. Options: ${best.fulfillment_options.join(', ')}.`
          : `Recommended store (${best.name}) has no stock; online warehouse has ${onlineEntry ? onlineEntry.qty : 0} units.`)
      : 'No inventory entries found.';

    return res.json({
      sku,
      product,
      recommended: best,
      alternatives,
      all: entries,
      summary
    });

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error', details: err.message });
  }
}

async function reserveItem(req, res) {
  try {
    const { sku, store_id, user_name, user_contact } = req.body;
    if (!sku || (store_id === undefined) || !user_name) return res.status(400).json({ error: 'Missing fields' });

    // Check inventory row
    const [rows] = await db.execute('SELECT * FROM inventory WHERE sku = ? AND store_id = ?', [sku, store_id]);
    if (rows.length === 0) return res.status(404).json({ error: 'Inventory record not found for that store' });

    const inv = rows[0];
    if (inv.qty <= 0) return res.status(409).json({ error: 'Out of stock at selected store' });

    // Use transaction for safety
    const conn = await db.getConnection();
    try {
      await conn.beginTransaction();
      // re-check qty
      const [recheck] = await conn.query('SELECT qty FROM inventory WHERE id = ? FOR UPDATE', [inv.id]);
      const currentQty = recheck[0].qty;
      if (currentQty <= 0) {
        await conn.rollback();
        conn.release();
        return res.status(409).json({ error: 'Out of stock (race condition)' });
      }
      await conn.execute('UPDATE inventory SET qty = qty - 1 WHERE id = ?', [inv.id]);
      const [resIns] = await conn.execute('INSERT INTO reservations (sku, store_id, user_name, user_contact, status) VALUES (?, ?, ?, ?, ?)',
        [sku, store_id, user_name, user_contact || null, 'reserved']);
      await conn.commit();
      conn.release();
      return res.json({ success: true, reservation_id: resIns.insertId });
    } catch (txErr) {
      await conn.rollback();
      conn.release();
      console.error(txErr);
      return res.status(500).json({ error: 'Reservation failed', details: txErr.message });
    }
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error', details: err.message });
  }
}

// NEW: buyItem — purchases from online warehouse (store_id = NULL)
async function buyItem(req, res) {
  try {
    const { sku, user_name, user_contact, address } = req.body;
    if (!sku || !user_name || !address) return res.status(400).json({ error: 'Missing fields - sku/user_name/address required' });

    // Find central warehouse inventory row (store_id IS NULL)
    const [rows] = await db.execute('SELECT * FROM inventory WHERE sku = ? AND store_id IS NULL', [sku]);
    if (rows.length === 0) return res.status(404).json({ error: 'Online warehouse record not found for that SKU' });

    const inv = rows[0];
    if (inv.qty <= 0) return res.status(409).json({ error: 'Out of stock in online warehouse' });

    const conn = await db.getConnection();
    try {
      await conn.beginTransaction();
      // re-check qty with lock
      const [recheck] = await conn.query('SELECT qty FROM inventory WHERE id = ? FOR UPDATE', [inv.id]);
      const currentQty = recheck[0].qty;
      if (currentQty <= 0) {
        await conn.rollback();
        conn.release();
        return res.status(409).json({ error: 'Out of stock (race condition)' });
      }
      // decrement warehouse
      await conn.execute('UPDATE inventory SET qty = qty - 1 WHERE id = ?', [inv.id]);
      // insert a reservation/purchase record with store_id NULL and status 'purchased'
      const [ins] = await conn.execute(
        'INSERT INTO reservations (sku, store_id, user_name, user_contact, status) VALUES (?, ?, ?, ?, ?)',
        [sku, null, user_name, user_contact || null, 'purchased']
      );
      // optionally: you could also create an orders table; for demo, reservations works.
      await conn.commit();
      conn.release();
      return res.json({ success: true, purchase_id: ins.insertId });
    } catch (txErr) {
      await conn.rollback();
      conn.release();
      console.error(txErr);
      return res.status(500).json({ error: 'Purchase failed', details: txErr.message });
    }
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error', details: err.message });
  }
}

async function listStores(req, res) {
  try {
    const stores = await getAllStores();
    return res.json({ stores });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error', details: err.message });
  }
}

async function listProducts(req, res) {
  try {
    const [rows] = await db.execute('SELECT sku, name, category, price FROM products');
    return res.json({ products: rows });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error', details: err.message });
  }
}

function toggleFailure(req, res) {
  simulateFailure = !simulateFailure;
  return res.json({ simulateFailure });
}

module.exports = {
  inventoryLookup,
  reserveItem,
  buyItem,            // exported
  listStores,
  listProducts,
  toggleFailure
};
