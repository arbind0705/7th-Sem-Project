# AI-Powered Recruitment and Interview Platform

An AI-assisted recruitment platform built with React, TypeScript, Vite, FastAPI, and PostgreSQL. The application supports recruiter job management, candidate applications, resume analysis, structured AI interviews, and interview reports.

This README explains how to open the project in Visual Studio Code, run it locally on Windows, configure the AI services, and troubleshoot common errors.

## 1. Project Overview

The application has two main parts:

- **Frontend:** React, TypeScript, Vite, and React Router.
- **Backend:** Python, FastAPI, SQLAlchemy, and PostgreSQL.

The backend also contains services for resume parsing, candidate-job matching, question selection, AI-based answer evaluation, interview scoring, audio analysis, and video observations.

### Main features

- Recruiter and candidate authentication.
- Job creation and job listings.
- Candidate registration and resume uploads.
- Resume extraction from PDF and DOCX files.
- Candidate skill extraction and job-match scoring.
- Structured interview rounds covering technical, project, behavioral, problem-solving, and HR questions.
- Adaptive interview difficulty and limited follow-up questions.
- Text-based interview answers.
- Audio transcription and acoustic feature analysis.
- Supplementary video observations, including face presence and approximate head direction.
- Interview reports and final candidate scores.

Some features depend on the configured AI provider, database, and external services.

## 2. Project Structure

The core structure is:

```text
7th-sem-project/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── candidates.py
│   │   │   ├── jobs.py
│   │   │   ├── interviews.py
│   │   │   └── deps.py
│   │   └── services/
│   │       ├── auth_service.py
│   │       ├── llm_service.py
│   │       ├── interview_service.py
│   │       ├── question_bank.py
│   │       ├── resume_parser.py
│   │       ├── matching.py
│   │       ├── scoring.py
│   │       ├── whisper_service.py
│   │       ├── audio_features.py
│   │       ├── video_features.py
│   │       ├── av_utils.py
│   │       └── filler_analysis.py
│   │
│   ├── data/
│   │   └── question_bank/
│   ├── experiments/
│   ├── alembic/
│   ├── .venv/
│   ├── .env
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   ├── package-lock.json
│   ├── index.html
│   └── vite.config.ts
│
└── README.md
```

This is a guide to the main files based on the project files reviewed; some filenames or subdirectories may differ in the current working copy.

## 3. Requirements

Install the following software before starting the project:

- Visual Studio Code.
- Python compatible with the backend dependencies.
- Node.js and npm.
- PostgreSQL, either through the configured database service or a local installation.
- Git, if version control is required.
- Ollama, if you want to run the language model locally.

The frontend uses Vite 8. Its documented minimum Node.js versions are 20.19+ or 22.12+. See the [official Vite guide](https://vite.dev/guide/).

## 4. Open the Project in VS Code

Open Visual Studio Code.

Select **File → Open Folder** and choose the main project directory:

```text
C:\sem 7\7th-sem-project-local-llm\7th-sem-project
```

Open the integrated terminal using:

**Terminal → New Terminal**

The main folder contains both the frontend and backend, but they use different commands and run in separate terminals.

## 5. Start the Backend

### Step 1: Open the backend folder

In the first VS Code terminal, run:

```powershell
cd "C:\sem 7\7th-sem-project-local-llm\7th-sem-project\backend"
```

### Step 2: Activate the virtual environment

If the virtual environment already exists, activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

The prompt should show `(venv)` or `(.venv)` when the environment is active.

If it does not exist, create it first:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, the following command changes the execution policy only for the current terminal process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then retry the activation command.

### Step 3: Install Python dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4: Configure environment variables

The backend uses a `.env` configuration file. Keep it in the backend directory if that matches the application's configuration.

Example configuration:

```dotenv
DATABASE_URL=your_postgresql_connection_string
JWT_SECRET=replace_with_a_long_random_secret

LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

ANTHROPIC_API_KEY=
GROQ_API_KEY=
```

Use actual credentials in your private local configuration. Never commit real passwords, API keys, or JWT secrets to Git.

The database connection above is a placeholder. The project previously used a Neon PostgreSQL connection, which means the backend can run locally while the database remains hosted remotely.

Make sure the backend actually loads `.env`. If it reports that a variable is missing even though it is present in that file, check how environment variables are loaded in the application.

### Step 5: Apply database migrations

The project includes Alembic configuration. If the migrations and database settings are configured, run:

```powershell
python -m alembic upgrade head
```

This applies the available database migrations. If it fails, check the database URL, database connectivity, and migration configuration before proceeding.

### Step 6: Start FastAPI

Run this command from inside the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

This is the backend startup command.

Do not run `npm run dev` from the backend directory. npm is used for the frontend, whereas Uvicorn runs the Python API.

### Step 7: Check the API

Open these addresses in your browser:

- API documentation: http://127.0.0.1:8000/docs
- Alternative documentation: http://127.0.0.1:8000/redoc

Keep the backend terminal open while using the application.

## 6. Start the Frontend

Open a second VS Code terminal. Leave the backend running.

Navigate to the frontend directory:

```powershell
cd "C:\sem 7\7th-sem-project-local-llm\7th-sem-project\frontend"
```

Install the JavaScript dependencies:

```powershell
npm ci
```

Start the development server:

```powershell
npm run dev
```

Vite will display a local URL, usually:

http://localhost:5173

Open that address in your browser.

The frontend and backend are separate processes. Both must remain running for the complete application to work.

## 7. Run AI Features Locally with Ollama

The language-model service supports either Anthropic or a local Ollama model.

### Step 1: Install Ollama

Install Ollama for Windows from:

https://ollama.com/download

Ollama provides a local API, normally at `http://localhost:11434`.

### Step 2: Download a model

Open a separate terminal and run:

```powershell
ollama pull llama3.1:8b
```

Check the installed models:

```powershell
ollama list
```

Model downloads require an internet connection. Once the model is downloaded, local inference can work without sending prompts to a cloud language-model API.

### Step 3: Configure the backend

Set these values in the backend's `.env` file:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

Restart FastAPI after changing the environment configuration.

With this setting, resume-profile extraction, interview-answer evaluation, and interview-report generation can use the local Ollama model, provided Ollama and the selected model are available.

If inference is too slow or memory usage is too high, try a smaller compatible model.

## 8. External API Requirements

Not every feature is fully local in the current implementation.

| Feature | Current implementation |
|---|---|
| Authentication | Local application code, database, and JWT |
| Job management | Local application code and database |
| PDF/DOCX resume text extraction | Local Python libraries |
| Skill matching | Local keyword-overlap calculation |
| Interview question selection | Local JSON question bank |
| Resume profile extraction | Anthropic by default; Ollama supported |
| Answer evaluation | Anthropic by default; Ollama supported |
| Report generation | Anthropic by default; Ollama supported |
| Audio transcription | Currently uses the Groq Whisper API |
| Audio measurements | Local audio-processing libraries |
| Video observations | Local MediaPipe model after it is available |

### Audio transcription

The current `whisper_service.py` sends recordings to Groq. Audio interviews therefore require a valid `GROQ_API_KEY` unless the transcription implementation is changed to use a local speech-recognition model.

Setting `LLM_PROVIDER=ollama` does not, by itself, make audio transcription local.

### Video observations

The video-analysis service downloads a MediaPipe model file on first use if the file is missing. An internet connection is needed for that initial download. After the model is available, the feature processes video locally.

### Database

Using a Neon connection requires internet access. For a fully offline setup, configure a local database and ensure the application and migrations support that database configuration.

## 9. Frontend Pages and Backend API Routes

### Frontend routes

The React application defines these main pages:

| Route | Purpose |
|---|---|
| `/login` | Recruiter login |
| `/apply/login` | Candidate login |
| `/` | Recruiter job listing |
| `/jobs/:jobId` | Job details |
| `/apply` | Candidate portal |
| `/candidates/:candidateId/interview` | Candidate interview |
| `/interviews/:interviewId/report` | Interview report |

Protected routes restrict recruiter and candidate pages according to their roles.

### Backend API routes

The following routes are defined in the reviewed API files:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Register a user |
| POST | `/api/auth/login` | Authenticate a user |
| GET | `/api/auth/me` | Retrieve the authenticated user |
| POST | `/api/jobs` | Create a job |
| GET | `/api/jobs` | List jobs |
| GET | `/api/jobs/{job_id}` | Retrieve a job |
| GET | `/api/jobs/{job_id}/candidates` | List candidates for a job |
| POST | `/api/candidates/resumes/upload` | Upload a resume for a job |
| POST | `/api/candidates/apply` | Submit a candidate application |
| GET | `/api/candidates/me` | List the candidate's applications |
| POST | `/api/interviews/start` | Start an interview |
| POST | `/api/interviews/{interview_id}/respond` | Submit a text answer |
| POST | `/api/interviews/{interview_id}/respond/audio` | Submit an audio recording |
| GET | `/api/interviews/{interview_id}/report` | Retrieve a completed interview report |

Some routes require authentication and a specific user role. See `/docs` for the available schemas, parameters, and request formats.

## 10. Useful Development Commands

### Backend

Run these from `backend/` with the virtual environment active:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
python -m alembic upgrade head
```

### Frontend

Run these from `frontend/`:

```powershell
npm ci
npm run dev
npm run build
npm run lint
```

`npm run build` checks TypeScript project builds and creates the production frontend bundle. `npm run lint` runs Oxlint.

## 11. Troubleshooting

### Error: npm cannot find `backend/package.json`

You are running an npm command in the Python backend directory.

Use:

```powershell
python -m uvicorn app.main:app --reload
```

### Error: No module named `uvicorn`

Activate the virtual environment and install the backend requirements:

```powershell
python -m pip install -r requirements.txt
```

### Error: Could not import `app.main`

Verify that `backend/app/main.py` exists and that the terminal is currently inside `backend/`.

Use:

```powershell
python -m uvicorn app.main:app --reload
```

### Error: `JWT_SECRET` is not set

Check the backend environment configuration. Authentication token creation requires a JWT secret.

### Error: `ANTHROPIC_API_KEY is not set`

The AI service may still be using its default Anthropic provider. Set `LLM_PROVIDER=ollama` if using a configured local Ollama model, then restart the backend.

### Error: `GROQ_API_KEY is not set`

The current audio-transcription service requires this key. Configure it securely or replace the service with local transcription.

### Error: Ollama connection refused

Confirm that Ollama is installed and running, and that the selected model exists:

```powershell
ollama list
```

### Error: Database connection failed

Verify `DATABASE_URL`, internet access if using Neon, database availability, and migration status.

### Frontend loads but API calls fail

Check that FastAPI is running, that the frontend is targeting the correct API URL, and that CORS and authentication settings permit the request.

## 12. Security and Data Handling

- Never commit `.env` files containing real credentials.
- Rotate any database password or JWT secret exposed in screenshots, logs, or repositories.
- Keep `.env`, `.venv/`, `node_modules/`, and generated files out of Git.
- Use a strong, randomly generated JWT secret.
- Do not test using real candidate documents until access controls and data-handling practices have been reviewed.
- Remember that using a local language model does not automatically make the database or audio-transcription pipeline local.

## 13. Recommended Daily Workflow

1. Open the root project folder in VS Code.
2. Activate the Python virtual environment in the backend terminal.
3. Start FastAPI with `python -m uvicorn app.main:app --reload`.
4. Open a second terminal and run `npm run dev` from `frontend/`.
5. Open the frontend URL in the browser.
6. Use `/docs` to inspect or test API endpoints.
7. Check the backend terminal when an action fails.
8. Stop the running processes with `Ctrl+C` when finished.

## 14. Project Status and Next Steps

The backend has been started successfully using Uvicorn, and the React frontend has a Vite development command.

Before treating the whole project as production-ready, verify database migrations, environment-variable loading, frontend-to-backend connectivity, error handling, authentication, and the configuration of all AI services.

For fully local operation, switch language-model evaluation to Ollama, replace Groq transcription with local speech recognition, and configure a local database if offline access is required.

---

**Development note:** Keep this README updated when API routes, configuration variables, dependencies, or model providers change.
