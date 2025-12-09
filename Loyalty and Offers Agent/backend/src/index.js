// src/index.js
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const inventoryRoutes = require('./routes/inventory');
const loyaltyRoutes = require('./routes/loyalty');
const salesRoutes = require('./routes/sales');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// route mounts
app.use('/inventory', inventoryRoutes);
app.use('/loyalty', loyaltyRoutes);
app.use('/sales', salesRoutes);

// health check
app.get('/', (req, res) => res.send('Retail Agent Backend is up'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
