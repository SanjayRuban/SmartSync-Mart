// utils/scoring.js
function computeSuitability({stock, demand, distanceKm, weights}) {
  const { w_stock=2, w_demand=1, w_distance=0.5 } = weights || {};
  const runoutRisk = demand / (stock + 1);
  // score higher is better; penalize high demand, distance and runout risk
  const score = (stock * w_stock) - (demand * w_demand) - (distanceKm * w_distance) - (runoutRisk * 10);
  return { score, runoutRisk };
}

module.exports = { computeSuitability };
