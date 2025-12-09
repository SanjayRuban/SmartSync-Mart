import React from "react";
import { Link } from "react-router-dom";

export default function NavBar() {
  const itemStyle = { marginRight: 12, textDecoration: "none", color: "#0b5fff" };
  return (
    <nav style={{ marginBottom: 18 }}>
      <Link to="/" style={itemStyle}><b>Home</b></Link>
      <Link to="/inventory" style={itemStyle}>Inventory / Overstock</Link>
      <Link to="/loyalty/compute" style={itemStyle}>Loyalty Compute</Link>
      <Link to="/loyalty/apply" style={itemStyle}>Loyalty Apply</Link>
      <Link to="/sales/checkout" style={itemStyle}>Full Checkout</Link>
    </nav>
  );
}
