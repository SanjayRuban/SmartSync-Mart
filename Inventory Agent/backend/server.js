// server.js
require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const inventoryRoutes = require('./routes/inventory');

const app = express();
app.use(cors());
app.use(bodyParser.json());

app.use('/api', inventoryRoutes);

// basic health
app.get('/', (req, res) => res.json({ status: 'Inventory Agent API', env: process.env.NODE_ENV || 'dev' }));

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Inventory backend listening on port ${PORT}`);
});
