import React from 'react';
import StoreCard from './StoreCard';

export default function ResultsList({ data, onReserve, onBuyOnline }) {
  if (!data) return null;
  const { product, recommended, alternatives, all, summary } = data;
  return (
    <div className="results">
      <div className="product">
        <h2>{product.name} <span className="sku">({product.sku})</span></h2>
        <p className="summary">{summary}</p>
      </div>

      {recommended && (
        <div className="recommended highlighted">
          <h3>Recommended Store</h3>
          <StoreCard store={recommended} onReserve={onReserve} onBuyOnline={onBuyOnline} isRecommended />
        </div>
      )}

      {alternatives && alternatives.length>0 && (
        <div className="alternatives">
          <h3>Alternative Stores</h3>
          <div className="grid">
            {alternatives.map(a => <StoreCard key={(a.code || '') + (a.store_id || '')} store={a} onReserve={onReserve} onBuyOnline={onBuyOnline} />)}
          </div>
        </div>
      )}

      {all && (
        <div className="all">
          <h3>All Stores (ranked)</h3>
          <div className="grid">
            {all.map(a => <StoreCard key={(a.code || '') + (a.store_id || '')} store={a} onReserve={onReserve} onBuyOnline={onBuyOnline} />)}
          </div>
        </div>
      )}
    </div>
  );
}
