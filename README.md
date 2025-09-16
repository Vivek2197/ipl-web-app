

# IPL Web App ⚡🏏  
A lightweight two‑service project: a Flask API for IPL stats and a Flask server‑rendered UI with secure forms, sessions, and a clean dashboard.[1][2][3]

## Features ✨  
- Teams list, head‑to‑head comparison, team record summaries, and player batting/bowling statistics available via simple API routes.[1]
- Server‑rendered dashboard that calls the API from the backend using Python requests for reliability and simplicity.[2]
- Session login with hashed passwords and CSRF‑protected POST forms for all dashboard actions.[4][5]

## Architecture 🧩  
- API service (port 5000): Flask app exposing /api/teams, /api/teamvteam, /api/team-record, /api/batting-record, /api/bowling-record.[1]
- UI service (port 7000): Flask app rendering Jinja templates and calling the API server‑side to populate pages.[2]
- Data: Match CSV for teams/head‑to‑head, plus helper logic for team and player aggregates.[1]

## Tech stack 🛠️  
- Python 3, Flask, Jinja templates, requests, and SQLite for user storage.[3]
- Security with Werkzeug password hashing and Flask‑WTF CSRF protection for all form submissions.[5][4]

## Project layout 📁  
- api/: app.py (routes), ipl.py (teams/H2H), jugaad.py (aggregations), ipl‑matches.csv (sample data).[1]
- web/: webapp.py (UI routes), templates/ (base and dashboard), static/ (styles/assets).[2]

## Quick start ▶️  
Clone, create a venv, install, and run both services.[3]
```bash
# from project root
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# terminal 1 – API (port 5000)
cd api
python app.py

# terminal 2 – UI (port 7000)
cd web
python webapp.py
```

Browse UI at http://127.0.0.1:7000 after confirming the API responds at http://127.0.0.1:5000/.[2][1]

## API endpoints 🔌  
- GET /api/teams → returns {"teams": [...]} used for dropdowns and lists.[1]
- GET /api/teamvteam?team1=...&team2=... → returns totals, wins by side, and draws/NR.[1]
- GET /api/team-record?team=... → returns overall and opponent‑wise aggregates.[1]
- GET /api/batting-record?batsman=... → batting “all” and “against” stats.[1]
- GET /api/bowling-record?bowler=... → bowling “all” and “against” stats.[1]

## UI routes 🧭  
- GET / → dashboard page populated with teams list from the API.[2]
- GET /teamvteam → demo route that renders a comparison result using query params.[2]

## Security 🔐  
- Passwords are stored as salted hashes via Werkzeug utilities; never plaintext.[4]
- CSRF tokens are required for every POST form in the UI, generated and validated by Flask‑WTF.[5]

## Dev tips 💡  
- Start the API first, then the UI; the UI depends on the API endpoints to render data.[2][1]
- If initial calls are slow, increase requests timeouts in the UI and consider caching heavy computations.[2]

## Troubleshooting 🧯  
- “CSRF token is missing” → ensure a hidden input named csrf_token is present in every POST form and a SECRET_KEY is configured.[5]
- “Read timed out” from the UI → verify API is running and reachable, and consider raising the read timeout during development.[2][1]

## Roadmap 🗺️  
- Add /api/players and UI datalists for name suggestions in Player Stats.[1]
- Add caching and warmup flows to reduce first‑hit latency on large data pulls.[1]

## License 📜  
This project is provided for educational purposes; adapt the license as needed for your repository.[3]

Acknowledgments 🙏  
Flask documentation and ecosystem tools made the setup straightforward and extensible.[6]

References  
- Flask docs overview and quickstart for app structure and running.[6][3]
- Flask‑WTF CSRF for form protection patterns.[5]
- Werkzeug utilities for password hashing guidance.[4]

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/89181332/a10d5c34-11ea-432d-9297-54fdb6e7154b/app.py)
[2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/89181332/14bb9d3c-2a88-4380-9a2f-9ecafee961b6/app.py)
[3](https://flask.palletsprojects.com/en/stable/quickstart/)
[4](https://werkzeug.palletsprojects.com/en/stable/utils/)
[5](https://flask-wtf.readthedocs.io/en/0.15.x/csrf.html)
[6](https://flask.palletsprojects.com)
[7](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/89181332/f5e2a0fb-9b70-49a8-8f32-3e6dd4b4a368/index.html)
