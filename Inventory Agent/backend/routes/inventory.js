// backend/routes/inventory.js
const express = require('express');
const router = express.Router();
const ctrl = require('../controllers/inventoryController');

router.get('/sku/:sku', ctrl.inventoryLookup);
router.post('/reserve', ctrl.reserveItem);
router.post('/buy', ctrl.buyItem);        // NEW endpoint
router.get('/stores', ctrl.listStores);
router.get('/products', ctrl.listProducts);
router.post('/toggle_failure', ctrl.toggleFailure);

module.exports = router;
