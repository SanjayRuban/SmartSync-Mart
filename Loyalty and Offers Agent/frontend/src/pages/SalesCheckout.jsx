import React, { useState } from "react";
import { API } from "../api";
import ResultBox from "../components/ResultBox";

export default function SalesCheckout(){
  const [customerId, setCustomerId] = useState(3);
  const [cartId, setCartId] = useState(3);
  const [promoCode, setPromoCode] = useState("FIT30");
  const [result, setResult] = useState(null);

  async function run() {
    setResult(null);
    try {
      const res = await API.post("/sales/checkout", { customerId: Number(customerId), cartId: Number(cartId), promoCode: promoCode || null });
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.message, details: err.response?.data || null });
    }
  }

  return (
    <div>
      <h2>Test 6 — Full Checkout (Sales Agent orchestration)</h2>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <label>CustomerId:</label>
        <input value={customerId} onChange={e => setCustomerId(e.target.value)} style={{ width: 70 }} />
        <label>CartId:</label>
        <input value={cartId} onChange={e => setCartId(e.target.value)} style={{ width: 70 }} />
        <label>PromoCode:</label>
        <input value={promoCode} onChange={e => setPromoCode(e.target.value)} />
        <button onClick={run}>Checkout</button>
      </div>

      {result && <ResultBox title="Sales Checkout Result">{JSON.stringify(result, null, 2)}</ResultBox>}
    </div>
  );
}
