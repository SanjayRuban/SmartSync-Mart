import axios from 'axios';
const API = axios.create({ baseURL: '/api' });

export async function getProducts() {
  const r = await API.get('/products');
  return r.data.products;
}

export async function getInventoryBySku(sku, lat, lng, preferred_store, weights) {
  const params = {};
  if (lat) params.lat = lat;
  if (lng) params.lng = lng;
  if (preferred_store) params.preferred_store = preferred_store;
  if (weights) {
    params.w_stock = weights.w_stock;
    params.w_demand = weights.w_demand;
    params.w_distance = weights.w_distance;
  }
  const r = await API.get(`/sku/${encodeURIComponent(sku)}`, { params });
  return r.data;
}

export async function makeReservation(payload) {
  const r = await API.post('/reserve', payload);
  return r.data;
}

export async function buyOnline(payload) {
  const r = await API.post('/buy', payload);
  return r.data;
}

export async function getStores() {
  const r = await API.get('/stores');
  return r.data.stores;
}
