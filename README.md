# Password Manager

Full-stack password manager with:
- FastAPI backend (`backend/`) for authentication and vault APIs
- React + Vite frontend (`frontend/`) for login and vault management

## Repository Structure

```text
.
|-- backend/
|-- frontend/
`-- README.md
```

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env` and configure required values (AWS, Cognito, session settings). Use [`backend/README.md`](backend/README.md) for the full environment variable list.

Run the API:

```bash
uvicorn main:app --reload
```

Default backend URL: `http://localhost:8000`

### 2. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

Run the frontend:

```bash
npm run dev
```

Default frontend URL: `http://localhost:5173`

## More Details

- Backend setup and API details: [`backend/README.md`](backend/README.md)
- Frontend routes and usage: [`frontend/README.md`](frontend/README.md)
