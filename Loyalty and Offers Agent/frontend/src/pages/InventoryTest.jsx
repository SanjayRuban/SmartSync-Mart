import React, { useState } from "react";
import { API } from "../api";
import ResultBox from "../components/ResultBox";

export default function InventoryTest() {
  const [sku, setSku] = useState("PBAR50");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await API.get(`/inventory/sku/${encodeURIComponent(sku)}/total`);
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.message, details: err.response?.data || null });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Test 1 — Inventory / Overstock</h2>
      <p>Check total stock for SKU and verify overstock triggers personalized offers.</p>

      <div style={{ display: "flex", gap: 8 }}>
        <input value={sku} onChange={e => setSku(e.target.value)} />
        <button onClick={run} disabled={loading}>Get Total</button>
      </div>

      {result && <ResultBox title="Result">{JSON.stringify(result, null, 2)}</ResultBox>}
    </div>
  );
}
