from __future__ import annotations

from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from backend import mission_control_service as mc_service


router = APIRouter()


def require_local_dashboard_auth(request: Request) -> RedirectResponse | None:
    config = mc_service.get_local_auth_config()

    if not config.get("enabled"):
        return None

    cookie_name = config.get("cookie_name", "salus_access")
    cookie_token = request.cookies.get(cookie_name)
    header_token = request.headers.get("x-salus-token")

    if mc_service.verify_local_auth_token(cookie_token) or mc_service.verify_local_auth_token(header_token):
        return None

    return RedirectResponse("/mission-control/login", status_code=303)


@router.get("/api/mission-control/auth/status")
def api_local_auth_status():
    return mc_service.get_local_auth_state()


@router.get("/mission-control/login", response_class=HTMLResponse)
def local_auth_login_page():
    config = mc_service.get_local_auth_config()
    warning = ""

    if config.get("default_password_warning"):
        warning = """
        <div class="warning">
          Default password is active. Change SALUS_LOCAL_PASSWORD before exposing this outside localhost.
        </div>
        """

    return f"""
    <!doctype html>
    <html>
      <head>
        <title>Project Salus Access Gate</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #e5e7eb;
            margin: 0;
            padding: 40px;
          }}
          .card {{
            max-width: 460px;
            margin: 10vh auto;
            background: #111827;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 28px;
            box-shadow: 0 20px 60px rgba(0,0,0,.35);
          }}
          input, button {{
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            border-radius: 10px;
            border: 1px solid #475569;
            box-sizing: border-box;
          }}
          button {{
            background: #2563eb;
            color: white;
            font-weight: 700;
            cursor: pointer;
          }}
          .muted {{
            color: #94a3b8;
          }}
          .warning {{
            background: #451a03;
            border: 1px solid #f97316;
            padding: 12px;
            border-radius: 10px;
            margin: 14px 0;
            color: #fed7aa;
          }}
        </style>
      </head>
      <body>
        <section class="card">
          <h1>Project Salus</h1>
          <p class="muted">Local dashboard access gate 🔐</p>
          {warning}
          <form method="post" action="/mission-control/login">
            <input type="password" name="password" placeholder="Local password" autofocus>
            <button type="submit">Enter Mission Control</button>
          </form>
        </section>
      </body>
    </html>
    """


@router.post("/mission-control/login")
async def local_auth_login(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)
    password = form.get("password", [""])[0]

    if not mc_service.verify_local_auth_password(password):
        return HTMLResponse(
            """
            <html>
              <body style="font-family: Arial; padding: 40px;">
                <h1>Access denied</h1>
                <p>Invalid local password.</p>
                <p><a href="/mission-control/login">Try again</a></p>
              </body>
            </html>
            """,
            status_code=401,
        )

    response = RedirectResponse("/mission-control/v1", status_code=303)
    response.set_cookie(
        key=mc_service.get_local_auth_config().get("cookie_name", "salus_access"),
        value=mc_service.local_auth_cookie_value(),
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/mission-control/logout")
def local_auth_logout():
    response = RedirectResponse("/mission-control/login", status_code=303)
    response.delete_cookie(mc_service.get_local_auth_config().get("cookie_name", "salus_access"))
    return response
