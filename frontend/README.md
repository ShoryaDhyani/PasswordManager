# Password Manager Frontend

Minimal React + Vite frontend for Cognito Hosted UI authentication and vault CRUD.

## Environment

Create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Run

```bash
npm install
npm run dev
```

Default dev URL: `http://localhost:5173`

## Routes

- `/login`: public login screen, redirects to backend `/login`
- `/`: protected vault list
- `/entry/new`: protected create-entry screen
- `/entry/:service`: protected edit-entry screen

## API Usage

All API calls include `credentials: "include"` to send the backend session cookie.

