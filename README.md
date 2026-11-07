# TKD Intelligence — Free Public Access Update

This update removes the paid-access plan entirely. The application is free to use:
- No signup or login
- No subscriptions, trial periods, or payment gateway
- Existing Rules, Training, Fitness, and Competition agents are preserved
- Existing Pinecone RAG integration is preserved
- Streamlit UI includes the About-page contact information and friendly frontend error messages
- FastAPI returns user-friendly error responses and logs technical details on the server

## Apply the update

1. Make a backup of your current project folder.
2. Extract this ZIP.
3. Copy `backend/main.py` into your existing project, replacing the old `backend/main.py`.
4. Copy `frontend/app.py` into your existing project, replacing the old `frontend/app.py`.
5. Keep your existing `.env`, `backend/agents/`, `backend/llm.py`, `data/`, and Pinecone configuration. Do not overwrite your secret `.env` file.

## Run locally (PowerShell)

Open PowerShell in the project folder:

```powershell
.env\Scripts\Activate.ps1
```

Start the API in one PowerShell window:

```powershell
python -m uvicorn backend.main:app --reload
```

Start Streamlit in a second PowerShell window:

```powershell
.env\Scripts\Activate.ps1
python -m streamlit run frontend/app.py
```

Open the Streamlit URL shown in the terminal (normally `http://localhost:8501`).

## Verify

- Open `http://127.0.0.1:8000/health` and confirm the API reports `access: free`.
- Test all four specialist agents.
- Test the About page and contact links.
- Stop the backend and send a chat message: the frontend should show a friendly connection message, not a Python traceback.
- Restart the backend and test again.

## Important

This is a local code update, not a public deployment. Public access still requires deploying the Streamlit frontend and FastAPI backend to hosting services and configuring environment variables securely. Keep `GROQ_API_KEY` and Pinecone credentials on the server; never commit `.env` to GitHub.

No Supabase or Razorpay setup is needed for this free version.
