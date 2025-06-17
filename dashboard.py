from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    matches = []
    if os.path.exists("matches.json"):
        with open("matches.json") as f:
            matches = json.load(f)
    return templates.TemplateResponse("dashboard.html", {"request": request, "matches": matches})
from fastapi.responses import RedirectResponse

@app.get("/tip")
async def redirect_to_paypal():
    print("💸 Tip link clicked!")
    return RedirectResponse(url="https://paypal.me/arbitip")
