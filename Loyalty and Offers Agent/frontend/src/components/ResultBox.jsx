import React from "react";

export default function ResultBox({ title, children }) {
  return (
    <div style={{
      background: "#fff", borderRadius: 8, padding: 16, boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
      marginTop: 12
    }}>
      {title && <h3 style={{ marginTop: 0 }}>{title}</h3>}
      <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{children}</pre>
    </div>
  );
}
