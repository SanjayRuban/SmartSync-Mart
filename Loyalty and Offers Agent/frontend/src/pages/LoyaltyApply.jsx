import React, { useState } from "react";
import { API } from "../api";
import ResultBox from "../components/ResultBox";

export default function LoyaltyApply(){
  const [customerId, setCustomerId] = useState(2);
  const [loyaltyUsed, setLoyaltyUsed] = useState(50);
  const [orderAmount, setOrderAmount] = useState(2750);
  const [result, setResult] = useState(null);

  async function run() {
    setResult(null);
    try {
      const res = await API.post("/loyalty/apply", {
        customerId: Number(customerId),
        loyalty_used: Number(loyaltyUsed),
        order_amount: Number(orderAmount)
      });
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.message, details: err.response?.data || null });
    }
  }

  return (
    <div>
      <h2>Test 5 — Loyalty Apply (post-checkout)</h2>
      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 10 }}>
        <label>CustomerId:</label>
        <input value={customerId} onChange={e=>setCustomerId(e.target.value)} style={{ width: 70 }} />
        <label>loyalty_used:</label>
        <input value={loyaltyUsed} onChange={e=>setLoyaltyUsed(e.target.value)} style={{ width: 90 }} />
        <label>order_amount:</label>
        <input value={orderAmount} onChange={e=>setOrderAmount(e.target.value)} style={{ width: 90 }} />
        <button onClick={run}>Apply</button>
      </div>

      {result && <ResultBox title="Apply Result">{JSON.stringify(result, null, 2)}</ResultBox>}
    </div>
  );
}
