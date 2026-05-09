# Password Manager API

A FastAPI backend password manager that uses AWS Cognito for authentication, encrypts vault data with AES-256-GCM (via KMS data keys), and stores per-user vaults in S3.

## Features
- Cognito Hosted UI login with server-side sessions
- CORS support for local frontend origins with credentialed cookies
- KMS + AES-256-GCM envelope encryption for vault payloads
- S3-backed vault storage (one vault per user)
- Simple REST API for managing entries

## Requirements
- Python 3.9 or higher
- AWS resources: Cognito User Pool + App Client, domain, S3 bucket, KMS key
- IAM role for the server with permissions for KMS and S3

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Create a `.env` file in the project root:
```bash
SESSION_SECRET=change-me
SESSION_HTTPS_ONLY=false
SESSION_MAX_AGE_SECONDS=3600
SESSION_SAMESITE=lax
SESSION_COOKIE_NAME=pm_session
FRONTEND_ORIGINS=http://localhost:5173

AWS_REGION=ap-south-1
S3_BUCKET=your-bucket
KMS_KEY_ARN=arn:aws:kms:ap-south-1:123456789012:key/your-key-id

VAULT_PREFIX=vaults

COGNITO_USER_POOL_ID=ap-south-1_XXXXXXX
COGNITO_CLIENT_ID=your-client-id
COGNITO_CLIENT_SECRET=your-client-secret
COGNITO_DOMAIN=your-domain.auth.ap-south-1.amazoncognito.com
COGNITO_REDIRECT_URI=http://localhost:8000/authorize
COGNITO_REGION=ap-south-1
COGNITO_SCOPES=openid email profile
```

Cognito app client configuration for local development:
- Callback URL: `http://localhost:8000/authorize`
- Sign-out URL: `http://localhost:5173/login`

## Run
```bash
uvicorn auth:app --reload
```

## Usage

1. Start the frontend dev server on `http://localhost:5173`.
2. Open `http://localhost:5173/login` and click sign in.
3. Cognito redirects to backend `/authorize`, which sets the session cookie and returns to the frontend app.
4. Use the API endpoints below after login:

- `GET /api/me`
- `GET /api/vault`
- `GET /api/vault/{service}`
- `PUT /api/vault/{service}`
- `DELETE /api/vault/{service}`

Example payload for `PUT /api/vault/{service}`:
```json
{
  "username": "alice@example.com",
  "password": "S3cr3t!",
  "notes": "optional"
}
```

## Notes
- Set `SESSION_HTTPS_ONLY=false` for local HTTP development. Use HTTPS in production.
- `FRONTEND_ORIGINS` accepts a comma-separated list and the first origin is used for post-login (`/`) and post-logout (`/login`) redirects.
- Keep hostnames consistent across local URLs (`localhost` everywhere or `127.0.0.1` everywhere). Mixing them can break OAuth state cookies.
- Set `COGNITO_DOMAIN` as host only (no `https://` prefix), e.g. `my-app.auth.ap-south-1.amazoncognito.com`.
- S3 objects contain encrypted vault payloads, not plaintext secrets.

