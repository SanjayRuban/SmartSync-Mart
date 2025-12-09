import React, { useState } from "react";
import { API } from "../api";
import ResultBox from "../components/ResultBox";

export default function LoyaltyCompute(){
  const [customerId, setCustomerId] = useState(1);
  const [cartId, setCartId] = useState(1);
  const [promoCode, setPromoCode] = useState("FIT30");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    setResult(null);
    try {
      const res = await API.post("/loyalty/compute", { customerId: Number(customerId), cartId: Number(cartId), promoCode: promoCode || null });
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.message, details: err.response?.data || null });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Test 2/3/4 — Loyalty Compute (Bronze / Silver / Gold)</h2>
      <p>Enter customerId and cartId for the tier you want to test (1 Bronze, 2 Silver, 3 Gold).</p>

      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <label>CustomerId:</label>
        <input value={customerId} onChange={e => setCustomerId(e.target.value)} style={{ width: 70 }} />
        <label>CartId:</label>
        <input value={cartId} onChange={e => setCartId(e.target.value)} style={{ width: 70 }} />
        <label>PromoCode:</label>
        <input value={promoCode} onChange={e => setPromoCode(e.target.value)} />
        <button onClick={run} disabled={loading}>Compute</button>
      </div>

      {result && <ResultBox title="Compute Result">{JSON.stringify(result, null, 2)}</ResultBox>}
    </div>
  );
}
