import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { deleteEntry, getEntry, putEntry } from "../api";

function Entry() {
  const { service } = useParams();
  const isNew = !service || service === "new";
  const [serviceName, setServiceName] = useState(isNew ? "" : service || "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;

    if (isNew || !service) {
      return undefined;
    }

    getEntry(service)
      .then((response) => {
        if (!active) {
          return;
        }
        const entry = response.entry || {};
        setUsername(entry.username || "");
        setPassword(entry.password || "");
        setNotes(entry.notes || "");
      })
      .catch((err) => {
        if (!active) {
          return;
        }
        if (err.status === 401) {
          navigate("/login", { replace: true });
          return;
        }
        setError(err.message || "Unable to load entry");
      });

    return () => {
      active = false;
    };
  }, [isNew, navigate, service]);

  const handleSave = async (event) => {
    event.preventDefault();
    setError("");

    if (!serviceName.trim()) {
      setError("Service name is required.");
      return;
    }

    try {
      setStatus("saving");
      await putEntry(serviceName.trim(), {
        username,
        password,
        notes,
      });
      setStatus("saved");
      navigate("/login");
    } catch (err) {
      if (err.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      setError(err.message || "Unable to save entry");
      setStatus("idle");
    }
  };

  const handleDelete = async () => {
    if (isNew) {
      navigate("/login");
      return;
    }

    try {
      setStatus("deleting");
      await deleteEntry(service);
      navigate("/login");
    } catch (err) {
      if (err.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      setError(err.message || "Unable to delete entry");
      setStatus("idle");
    }
  };

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">Entry</p>
          <h1>Password Manager</h1>
        </div>
        <button
          className="button ghost"
          type="button"
          onClick={() => navigate("/login")}
        >
          Back to Login
        </button>
      </header>

      <form className="card form" onSubmit={handleSave}>
        <label>
          Service name
          <input
            type="text"
            value={serviceName}
            onChange={(event) => setServiceName(event.target.value)}
            placeholder="e.g. GitHub"
            disabled={!isNew}
            required
          />
        </label>

        <label>
          Username
          <input
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="user@example.com"
          />
        </label>

        <label>
          Password
          <input
            type="text"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="••••••••"
          />
        </label>

        <label>
          Notes
          <textarea
            rows={4}
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            placeholder="Optional notes"
          />
        </label>

        {error && <p className="error">{error}</p>}

        <div className="form-actions">
          <button
            className="button primary"
            type="submit"
            disabled={status === "saving"}
          >
            {status === "saving" ? "Saving..." : "Save"}
          </button>
          <button
            className="button danger"
            type="button"
            onClick={handleDelete}
            disabled={status === "deleting"}
          >
            {status === "deleting"
              ? "Deleting..."
              : isNew
                ? "Cancel"
                : "Delete"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default Entry;
