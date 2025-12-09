import React, { useState, useEffect } from 'react';
import { getProducts, getInventoryBySku, makeReservation, buyOnline, getStores } from './api';
import SearchBar from './components/SearchBar';
import ResultsList from './components/ResultsList';
import Modal from './components/Modal';

export default function App() {

  const [products, setProducts] = useState([]);
  const [stores, setStores] = useState([]);
  const [selectedSku, setSelectedSku] = useState('');

  const [location, setLocation] = useState({ lat: null, lng: null });
  const [gpsRequired, setGpsRequired] = useState(true);
  const [showGpsPrompt, setShowGpsPrompt] = useState(true);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Modal states
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState(""); 
  const [modalStore, setModalStore] = useState(null);

  const [formName, setFormName] = useState("");
  const [formContact, setFormContact] = useState("");
  const [formAddress, setFormAddress] = useState("");

  const [successMessage, setSuccessMessage] = useState("");


  // ---------------------------------------------------------
  // Load initial products & stores
  // ---------------------------------------------------------
  useEffect(() => {
    getProducts().then(setProducts);
    getStores().then(setStores);
  }, []);


  // ---------------------------------------------------------
  // AUTO close popup when coords are received
  // ---------------------------------------------------------
  useEffect(() => {
    if (location.lat && location.lng) {
      setGpsRequired(false);
      setShowGpsPrompt(false);
    }
  }, [location]);


  // ---------------------------------------------------------
  // IMPROVED GPS FUNCTION WITH RETRY + WATCHPOSITION
  // ---------------------------------------------------------
  const handleAllowLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation not supported in this browser.");
      return;
    }

    let gotLocation = false;

    // Primary attempt (fast network-based)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        gotLocation = true;
        setLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude
        });
        setGpsRequired(false);
        setShowGpsPrompt(false);
      },
      (err) => {
        console.warn("getCurrentPosition failed:", err);

        // Retry using watchPosition (more reliable)
        const watchId = navigator.geolocation.watchPosition(
          (pos) => {
            if (!gotLocation) {
              gotLocation = true;
              setLocation({
                lat: pos.coords.latitude,
                lng: pos.coords.longitude
              });
              setGpsRequired(false);
              setShowGpsPrompt(false);
              navigator.geolocation.clearWatch(watchId);
            }
          },
          (err2) => {
            console.error("watchPosition also failed:", err2);
            alert("Unable to get GPS. Try moving near a window or enabling Location Services.");
            navigator.geolocation.clearWatch(watchId);
          },
          { enableHighAccuracy: false, timeout: 20000, maximumAge: 0 }
        );
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  };


  // ---------------------------------------------------------
  // SEARCH handler
  // ---------------------------------------------------------
  const onSearch = async (skuInput) => {
    if (gpsRequired) return alert("Please allow GPS first.");
    if (!skuInput) return alert("Enter SKU");

    setSelectedSku(skuInput);
    setLoading(true);

    try {
      const res = await getInventoryBySku(skuInput, location.lat, location.lng);
      setResult(res);
    } catch (err) {
      alert("Error: " + (err?.response?.data?.error || err.message));
    }

    setLoading(false);
  };


  // ---------------------------------------------------------
  // RESERVE modal handler
  // ---------------------------------------------------------
  const openReserveModal = (storeId) => {
    setModalType("reserve");
    setModalStore(storeId);
    setFormName("");
    setFormContact("");
    setModalVisible(true);
  };


  // ---------------------------------------------------------
  // BUY modal handler
  // ---------------------------------------------------------
  const openBuyModal = () => {
    setModalType("buy");
    setFormName("");
    setFormContact("");
    setFormAddress("");
    setModalVisible(true);
  };


  // ---------------------------------------------------------
  // SUBMIT FORMS
  // ---------------------------------------------------------
  const submitForm = async () => {
    if (!formName) return alert("Enter your name");

    try {
      if (modalType === "reserve") {
        const r = await makeReservation({
          sku: selectedSku,
          store_id: modalStore,
          user_name: formName,
          user_contact: formContact
        });
        setSuccessMessage(`Reserved successfully! Reservation ID: ${r.reservation_id}`);
      }

      if (modalType === "buy") {
        if (!formAddress) return alert("Enter address");
        const r = await buyOnline({
          sku: selectedSku,
          user_name: formName,
          user_contact: formContact,
          address: formAddress
        });
        setSuccessMessage(`Order placed! Order ID: ${r.purchase_id}`);
      }

      const refreshed = await getInventoryBySku(selectedSku, location.lat, location.lng);
      setResult(refreshed);

      setModalVisible(false);

    } catch (err) {
      alert("Operation failed: " + (err?.response?.data?.error || err.message));
    }
  };


  return (
    <div className="app">

      {/* HEADER */}
      <header className="header">
        <div>
          <h1 className="title">Retail Inventory Agent</h1>
          <p className="subtitle">Real GPS-based store finder</p>
        </div>

        <button className="btn gps-btn" onClick={handleAllowLocation}>
          Allow GPS
        </button>
      </header>


      <SearchBar
        products={products}
        onSearch={onSearch}
        gpsEnabled={!gpsRequired}
      />

      {loading && <div className="loading">Checking inventory…</div>}

      {successMessage && (
        <div className="success-box">{successMessage}</div>
      )}

      {result &&
        <ResultsList
          data={result}
          onReserve={openReserveModal}
          onBuyOnline={openBuyModal}
        />
      }


      {/* MODAL */}
      <Modal
        show={modalVisible}
        title={modalType === "reserve" ? "Reserve Item" : "Buy Online"}
        onClose={() => setModalVisible(false)}
      >
        <div className="form-control">
          <label>Name</label>
          <input value={formName} onChange={e => setFormName(e.target.value)} />
        </div>

        <div className="form-control">
          <label>Contact (optional)</label>
          <input value={formContact} onChange={e => setFormContact(e.target.value)} />
        </div>

        {modalType === "buy" && (
          <div className="form-control">
            <label>Shipping Address</label>
            <textarea value={formAddress} onChange={e => setFormAddress(e.target.value)} />
          </div>
        )}

        <button className="btn primary" onClick={submitForm}>
          Confirm
        </button>
      </Modal>


      {/* GPS POPUP */}
      {showGpsPrompt && gpsRequired && (
        <div className="gps-popup">
          <div className="gps-card">
            <h2>Location Required</h2>
            <p>Allow GPS to get nearest store suggestions.</p>

            <button className="btn primary" onClick={handleAllowLocation}>
              Allow GPS
            </button>

            <button
              className="btn"
              onClick={() => {
                setShowGpsPrompt(false);
                setGpsRequired(false);
              }}
            >
              Enter Manually
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
