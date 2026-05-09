import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { getMe } from "../api";

function RequireAuth({ children }) {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    let active = true;

    getMe()
      .then(() => {
        if (active) {
          setStatus("ok");
        }
      })
      .catch((error) => {
        if (active) {
          if (error.status === 401) {
            setStatus("unauthenticated");
          } else {
            setStatus("error");
          }
        }
      });

    return () => {
      active = false;
    };
  }, []);

  if (status === "loading") {
    return (
      <div className="page">
        <div className="card">Checking session...</div>
      </div>
    );
  }

  if (status === "unauthenticated") {
    return <Navigate to="/login" replace />;
  }

  if (status === "error") {
    return (
      <div className="page">
        <div className="card">Unable to reach the API.</div>
      </div>
    );
  }

  return children;
}

export default RequireAuth;
