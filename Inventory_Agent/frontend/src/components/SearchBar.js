import React, { useState } from 'react';

export default function SearchBar({ products, onSearch, gpsEnabled }) {
  const [query, setQuery] = useState('');
  const suggestions = products ? products.filter(p => (p.name || '').toLowerCase().includes(query.toLowerCase()) || (p.sku || '').toLowerCase().includes(query.toLowerCase())).slice(0,6) : [];

  const handleSearchClick = () => {
    if (!gpsEnabled) {
      // allow manual lat,lng in the query like "SKU3002" or "13.08,80.27,SKU3002"
      const parts = query.split(',');
      if (parts.length >= 3) {
        // user input: lat,lng,sku
        const lat = parts[0].trim();
        const lng = parts[1].trim();
        const sku = parts.slice(2).join(',').trim();
        if (!sku) return alert('Enter SKU after lat,lng');
        // we'll pass the sku only — App handles location (manual entry can be implemented later)
        onSearch(sku);
        return;
      } else {
        return alert('GPS is required. Click "Allow GPS" first or enter manual lat,lng in format: lat,lng,SKU');
      }
    }
    onSearch(query.trim());
  };

  return (
    <div className="searchbar">
      <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search product name or paste SKU (e.g., SKU3002)" />
      <button onClick={handleSearchClick} className="btn primary">Check Inventory</button>
      {suggestions.length>0 && (
        <ul className="suggestions">
          {suggestions.map(s=>(
            <li key={s.sku} onClick={()=>{ setQuery(s.sku); }}>{s.name} — {s.sku}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
