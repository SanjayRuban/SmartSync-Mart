import React from 'react';

export default function StoreCard({ store, onReserve, onBuyOnline, isRecommended }) {
  const handleReserve = () => {
    if (!onReserve) return;
    onReserve(store.store_id);
  };

  const handleBuy = () => {
    if (!onBuyOnline) return;
    // if store is online, it's same; otherwise we keep buy route to online warehouse
    onBuyOnline(store);
  };

  return (
    <div className={`store-card ${isRecommended ? 'recommended-card' : ''}`}>
      <div className="left">
        <h4>{store.name} {store.store_id === null ? '(Online Warehouse)' : ''}</h4>
        <p className="meta">Qty: <strong>{store.qty}</strong> • Dist: <strong>{store.distanceKm === 99999 ? 'N/A' : store.distanceKm + ' km'}</strong> • Demand: <strong>{store.demand}</strong></p>
        <p>Runout risk: <strong>{store.runoutRisk}</strong> • Score: <strong>{store.score}</strong></p>
        <p className="options">Options: {store.fulfillment_options && store.fulfillment_options.join(', ')}</p>
      </div>

      <div className="right">
        {store.store_id !== null ? (
          <>
            <button className="btn" onClick={handleReserve} disabled={store.qty<=0}>Reserve</button>
            <button className="btn primary" onClick={handleBuy}>Buy Online</button>
          </>
        ) : (
          <button className="btn primary" onClick={handleBuy} disabled={store.qty<=0}>Buy Online</button>
        )}
      </div>
    </div>
  );
}
