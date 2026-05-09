import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getMe, getVault, logoutUrl } from "../api";

function Vault() {
  const [vault, setVault] = useState({});
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;

    Promise.all([getMe(), getVault()])
      .then(([me, vaultResponse]) => {
        if (!active) {
          return;
        }
        setEmail(me.email || "");
        setVault(vaultResponse.vault || {});
        setLoading(false);
      })
      .catch((err) => {
        if (!active) {
          return;
        }
        if (err.status === 401) {
          navigate("/login", { replace: true });
          return;
        }
        setError(err.message || "Unable to load vault");
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [navigate]);

  const handleLogout = () => {
    window.location.href = logoutUrl();
  };

  const services = Object.keys(vault).sort((a, b) => a.localeCompare(b));

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">Vault</p>
          <h1>Password Manager</h1>
        </div>
        <div className="topbar-actions">
          <span className="muted">{email || "Signed in"}</span>
          <button className="button ghost" type="button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <div className="card">
        <div className="card-header">
          <h2>Services</h2>
          <button
            className="button primary"
            type="button"
            onClick={() => navigate("/entry/new")}
          >
            New Entry
          </button>
        </div>

        {loading && <p className="muted">Loading vault...</p>}
        {error && <p className="error">{error}</p>}

        {!loading && !error && services.length === 0 && (
          <p className="muted">No entries yet. Create your first one.</p>
        )}

        {!loading && !error && services.length > 0 && (
          <ul className="service-list">
            {services.map((service) => (
              <li key={service}>
                <button
                  className="service-item"
                  type="button"
                  onClick={() =>
                    navigate(`/entry/${encodeURIComponent(service)}`)
                  }
                >
                  <span>{service}</span>
                  <span className="muted">View</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default Vault;
