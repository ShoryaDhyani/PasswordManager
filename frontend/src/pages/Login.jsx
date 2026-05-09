import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getMe, loginUrl } from "../api";

function Login() {
  const [checkingSession, setCheckingSession] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;

    getMe()
      .then(() => {
        if (active) {
          navigate("/", { replace: true });
        }
      })
      .catch(() => {
        if (active) {
          setCheckingSession(false);
        }
      });

    return () => {
      active = false;
    };
  }, [navigate]);

  const handleLogin = () => {
    window.location.href = loginUrl();
  };

  return (
    <div className="page center">
      <div className="card login-card">
        <p className="eyebrow">Password Manager</p>
        <h1>Access your secure vault</h1>
        <p className="muted">
          Sign in to view and manage your encrypted passwords.
        </p>
        <button className="button primary" type="button" onClick={handleLogin}>
          Sign in with Cognito
        </button>
        {checkingSession && <p className="footer-note">Checking session...</p>}
      </div>
    </div>
  );
}

export default Login;
