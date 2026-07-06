from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["command-home"])


@router.get("/command-home", response_class=HTMLResponse)
def command_home() -> str:
    modules = [
        {
            "title": "Mission Control",
            "url": "/mission-control/ui",
            "description": "Primary operating dashboard: missions, SITREPs, AARs, status actions, commander briefs.",
            "status": "Operational",
        },
        {
            "title": "Daily Driver",
            "url": "/command/daily-driver",
            "description": "Daily workflow control surface for execution, review, and daily operating rhythm.",
            "status": "Operational",
        },
        {
            "title": "Dashboard Index",
            "url": "/command/dashboard-index",
            "description": "Index of command dashboards and local MVP navigation.",
            "status": "Operational",
        },
        {
            "title": "Kernel",
            "url": "/command/kernel",
            "description": "Core Salus kernel status, subsystem registry, planning, execution gate, and learning capture.",
            "status": "Operational",
        },
        {
            "title": "Memory",
            "url": "/command/memory",
            "description": "Memory engine interface for persistent knowledge and recall.",
            "status": "Operational",
        },
        {
            "title": "Judgment Engine",
            "url": "/command/judgment",
            "description": "Decision quality, scoring, and judgment support.",
            "status": "Operational",
        },
        {
            "title": "Teaching Engine",
            "url": "/command/teaching-engine",
            "description": "Learning support, lessons, quizzes, and skill development.",
            "status": "Operational",
        },
        {
            "title": "Records",
            "url": "/command/records",
            "description": "Record management, archival, deletion controls, and project records.",
            "status": "Operational",
        },
        {
            "title": "API Docs",
            "url": "/docs",
            "description": "FastAPI route inventory and manual endpoint testing.",
            "status": "Developer",
        },
        {
            "title": "System Readiness",
            "url": "/api/kernel/health",
            "description": "Machine-readable kernel health endpoint.",
            "status": "API",
        },
    ]

    cards = ""
    for module in modules:
        cards += f"""
        <a class="card" href="{module["url"]}">
          <div class="status">{module["status"]}</div>
          <h2>{module["title"]}</h2>
          <p>{module["description"]}</p>
          <span>{module["url"]}</span>
        </a>
        """

    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Project Salus Command Home</title>
      <style>
        body {{
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          background: #080c11;
          color: #e8edf2;
        }}
        header {{
          padding: 34px;
          background: linear-gradient(135deg, #111821, #182536);
          border-bottom: 1px solid #263241;
        }}
        h1 {{
          margin: 0;
          font-size: 34px;
        }}
        .sub {{
          color: #9fb0c0;
          max-width: 900px;
          line-height: 1.5;
        }}
        main {{
          padding: 24px;
        }}
        .grid {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 16px;
        }}
        .card {{
          display: block;
          text-decoration: none;
          color: #e8edf2;
          background: #141c26;
          border: 1px solid #263241;
          border-radius: 14px;
          padding: 18px;
          min-height: 170px;
          box-shadow: 0 8px 24px rgba(0,0,0,.25);
        }}
        .card:hover {{
          border-color: #5b7ca3;
          background: #172231;
        }}
        .card h2 {{
          margin: 8px 0 10px;
          font-size: 21px;
        }}
        .card p {{
          color: #b8c7d6;
          line-height: 1.45;
        }}
        .card span {{
          color: #8ab4ff;
          font-size: 13px;
        }}
        .status {{
          display: inline-block;
          color: #cfe3ff;
          border: 1px solid #334960;
          border-radius: 999px;
          padding: 4px 9px;
          font-size: 12px;
          background: #0d141d;
        }}
        .bar {{
          margin-bottom: 20px;
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
        }}
        .button {{
          text-decoration: none;
          color: #e8edf2;
          border: 1px solid #334960;
          border-radius: 10px;
          padding: 10px 14px;
          background: #121a24;
        }}
      </style>
    </head>
    <body>
      <header>
        <h1>Project Salus Command Home</h1>
        <p class="sub">
          Central local launch point for Mission Control, daily execution, judgment, memory, teaching, records, kernel health, and developer tools.
        </p>
      </header>
      <main>
        <div class="bar">
          <a class="button" href="/mission-control/ui">Open Mission Control</a>
          <a class="button" href="/docs">Open API Docs</a>
          <a class="button" href="/api/kernel/health">Kernel Health</a>
        </div>
        <section class="grid">
          {cards}
        </section>
      </main>
    </body>
    </html>
    """
