# AI Smart Home (Capstone Project)

An intelligent, AI-powered smart home automation system designed for Windows during development and later deployment to a Raspberry Pi backend.

This project features a clean, layered FastAPI backend connected to a modern, premium React frontend dashboard.

---

## Project Overview

AI-SmartHome is a capstone project building a clean, layered architecture backend in FastAPI, using SQLAlchemy 2.x and SQLite, designed to support local in-memory state caching for low-latency smart-home device control while maintaining persistent storage.

Its accompanying React frontend dashboard utilizes glassmorphism, responsive CSS grid layouts, and custom dark-theme tailormade colors to deliver a visually stunning, presentation-ready smart home IoT control center.

---

## Unified Architecture & State Flow

The application implements a clean **Unified Layered Architecture**:

```
 [ React Frontend ]
         │ (Fetch API)
         ▼
    [ API Route ] (FastAPI endpoint handles HTTP and CORS)
         │
         ▼
[Pydantic Schema] (Input/Output data validation)
         │
         ▼
  [Device Manager] (Orchestrates in-memory state cache & hardware abstraction)
    ┌────┴──────────────────────────┐
    ▼                               ▼
[In-Memory Cache]         [Hardware Abstraction]
                            ├── Windows: DeviceSimulator (Simulated registers)
                            └── Raspberry Pi: GPIO Service (Physical relays)
         │
         ▼
    [Repository] (SQLAlchemy CRUD operations)
         │
         ▼
   [SQLAlchemy]
         │
         ▼
    [Database] (SQLite persistence)
```

1. **React Frontend**: Functional components using hooks. Communicates with FastAPI via Fetch API and handles loading, error recovery, and theme variables.
2. **API Router**: Exposes endpoints and handles HTTP-related requests, status codes, CORS validation, and input validation.
3. **Pydantic Schemas**: Validates data schemas for request input and response output serialization (Pydantic v2).
4. **Services (Device Manager)**: Houses domain business logic. Manages an in-memory cache of device states to guarantee low-latency reads. Coordinates state changes with both the hardware abstraction layer and the persistence layer.
5. **Hardware Abstraction Layer (HAL)**: Emulates hardware during development via `DeviceSimulator`. When deployed on the Raspberry Pi, calls physical `GPIO` interfaces.
6. **Repositories**: Encapsulates all query/insert code using SQLAlchemy 2.x standard operators, decoupling the database engine from services.
7. **SQLite Database**: Serves as the persistence store.

---

## Project Structure

```
AI-SmartHome/
├── backend/                  # FastAPI Backend Layer
│   ├── .env
│   ├── .gitignore
│   ├── requirements.txt
│   ├── smarthome.db (Local development database)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py (App entrypoint & CORS config)
│   │   ├── api/routes/devices.py (Device routers)
│   │   ├── database/ (SQLite base, connections & seeding)
│   │   ├── models/ (SQLAlchemy models)
│   │   ├── repositories/ (Database query execution)
│   │   └── services/device/ (DeviceManager, Simulator, and GPIO abstraction)
│   └── tests/ (Integration test suites)
├── frontend/                 # React Frontend Layer
│   ├── .env.development      # Configures backend API endpoints
│   ├── index.html            # Main HTML wrapper
│   ├── package.json          # Node scripts and dependencies
│   ├── vite.config.js        # Vite compiler rules
│   └── src/
│       ├── main.jsx          # Bootstrap startup
│       ├── App.jsx           # Main controller layout
│       ├── index.css         # Professional dark UI styling
│       ├── components/       # Reusable React components (Header, Sidebar, etc.)
│       ├── services/api.js   # Encapsulated backend fetch operations
│       └── utils/deviceUtils.js # Name formatting & icon mappings
├── docs/                     # Status and Handoff Documentation
│   ├── DEVELOPMENT_STATUS.md # Unified status report
│   └── FRONTEND_STATUS.md    # Dedicated frontend report
└── venv/                     # Python Virtual Environment
```

---

## Technologies Used

### Backend
- **Python**: 3.12.10
- **FastAPI**: 0.141.1
- **SQLAlchemy**: 2.0.51
- **Pydantic**: 2.13.4
- **SQLite**: Python built-in driver
- **Uvicorn**: 0.52.0
- **Pytest**: 9.1.1 (with `httpx` for requests)

### Frontend
- **React**: 19.2.8
- **React DOM**: 19.2.8
- **Vite**: 8.2.2
- **Lucide React**: 0.475.0 (for icons)
- **Vanilla CSS**: Custom styling with HSL tailored variables

---

## Development Environment Setup

Ensure you have Python 3.12.10 and Node.js v18+ installed on your system.

### 1. Python Backend Setup

Navigate to the project root (`AI-SmartHome/`):

**Activate Virtual Environment (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Install Backend Dependencies:**
```powershell
pip install -r backend/requirements.txt
```

**Seeding & SQLite Setup (Optional):**
The SQLite database (`backend/smarthome.db`) initializes and auto-seeds on server startup. To seed manually, run:
```powershell
cd backend
$env:PYTHONPATH="."
..\venv\Scripts\python -c "from app.database.init_db import init_db; init_db()"
```

### 2. React Frontend Setup

Open a new shell and navigate to the frontend directory:
```powershell
cd frontend
npm install
```

Configure the development environment backend API inside `frontend/.env.development` if needed:
```
VITE_API_URL=http://127.0.0.1:8000
```

---

## How to Run the Project

### Step 1: Start the FastAPI Backend
From the `backend/` directory, activate the virtual environment and launch uvicorn:
```powershell
cd backend
$env:PYTHONPATH="."
..\venv\Scripts\python -m uvicorn app.main:app --reload
```
The backend API Swagger documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Step 2: Start the React Frontend
From the `frontend/` directory, start the Vite development server:
```powershell
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser to view the IoT Smart Home dashboard.

---

## Testing Verification

### 1. Run Python Backend Integration Tests
From the `backend/` directory:
```powershell
cd backend
$env:PYTHONPATH="."
..\venv\Scripts\pytest tests/
```

### 2. Verify Frontend Production Compilation
Ensure the React assets bundle correctly with no compiler errors:
```powershell
cd frontend
npm run build
```

---

## Implemented API Endpoints

- **GET** `/` -> Health check message.
- **GET** `/devices/` -> Fetch all smart devices list.
- **POST** `/devices/{device}/on` -> Toggle a device ON (maps to `ON`, `UNLOCKED`, or `OPEN`).
- **POST** `/devices/{device}/off` -> Toggle a device OFF (maps to `OFF`, `LOCKED`, or `CLOSED`).

---

## Implemented Device Controls
The database seeds 7 active devices, which are dynamically synced on the React dashboard:
1. **Bedroom Light** (Category: Light, Room: Bedroom, Status: ON/OFF)
2. **Living Room Light** (Category: Light, Room: Living Room, Status: ON/OFF)
3. **Kitchen Light** (Category: Light, Room: Kitchen, Status: ON/OFF)
4. **Fan** (Category: Fan, Room: Living Room, Status: ON/OFF)
5. **AC** (Category: AC, Room: Bedroom, Status: ON/OFF)
6. **Door** (Category: Security, Room: Entrance, Status: LOCKED/UNLOCKED)
7. **Curtains** (Category: Comfort, Room: Living Room, Status: CLOSED/OPEN)
