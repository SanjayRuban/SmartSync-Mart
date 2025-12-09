import React from "react";

export default function Modal({ show, title, children, onClose }) {
  if (!show) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <h2>{title}</h2>
        <div className="modal-content">{children}</div>

        <button className="btn close-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
}
