import React from "react";
import { Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import Home from "./pages/Home";
import InventoryTest from "./pages/InventoryTest";
import LoyaltyCompute from "./pages/LoyaltyCompute";
import LoyaltyApply from "./pages/LoyaltyApply";
import SalesCheckout from "./pages/SalesCheckout";

export default function App() {
  return (
    <div style={{ fontFamily: "Inter, Arial, sans-serif", padding: 20 }}>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/inventory" element={<InventoryTest />} />
        <Route path="/loyalty/compute" element={<LoyaltyCompute />} />
        <Route path="/loyalty/apply" element={<LoyaltyApply />} />
        <Route path="/sales/checkout" element={<SalesCheckout />} />
      </Routes>
    </div>
  );
}
