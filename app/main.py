from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
import json
from datetime import datetime

from app.models import User, Booking, UsageLog
from app.data import db, BRAND_LOGO_URL

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- HELPER FUNCTIONS ---
def get_current_user(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return db.get_user(user_id)

def flash(request: Request, message: str, category: str = "info"):
    # Simple flash implementation using cookies or list injection (Mock implementation)
    pass 

# --- MIDDLEWARE / CONTEXT PROCESSOR ---
@app.middleware("http")
async def add_context(request: Request, call_next):
    response = await call_next(request)
    return response

def common_context(request: Request):
    user = get_current_user(request)
    return {
        "request": request,
        "current_user": user,
        "home_config": db.home_config,
        "brand_logo": BRAND_LOGO_URL,
        "visit_count": db.home_config.visitorCount
    }

# --- ROUTES ---

@app.get("/")
async def home(request: Request):
    ctx = common_context(request)
    db.home_config.visitorCount += 1
    featured = [e for e in db.equipment if e.id in db.home_config.featuredEquipmentIds]
    ctx.update({"featured_equipment": featured, "labs": db.labs})
    return templates.TemplateResponse("index.html", ctx)

@app.get("/login")
async def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/")
    return templates.TemplateResponse("login.html", common_context(request))

@app.post("/api/login")
async def login_api(response: Response, user_id: str = Form(...), password: str = Form(...)):
    user = db.get_user(user_id)
    if user and user.password == password and not user.isLocked:
        content = {"success": True, "redirect": "/"}
        resp = JSONResponse(content=content)
        resp.set_cookie(key="user_id", value=user.id)
        return resp
    return JSONResponse(content={"success": False, "message": "Sai thông tin đăng nhập"}, status_code=401)

@app.get("/logout")
async def logout():
    resp = RedirectResponse("/login")
    resp.delete_cookie("user_id")
    return resp

@app.get("/equipment")
async def equipment_list(request: Request, search: str = "", status: str = "ALL"):
    ctx = common_context(request)
    items = db.equipment
    if search:
        s = search.lower()
        items = [e for e in items if s in e.name.lower() or s in e.code.lower()]
    if status != "ALL":
        items = [e for e in items if e.status == status]
    
    ctx.update({"equipment": items, "search": search, "status_filter": status})
    return templates.TemplateResponse("equipment_list.html", ctx)

@app.get("/equipment/{id}")
async def equipment_detail(request: Request, id: str):
    ctx = common_context(request)
    item = db.get_equipment(id)
    if not item:
        return RedirectResponse("/equipment")
    
    # Related data
    item_logs = [l for l in db.logs if l.equipmentId == id]
    manager = db.get_user(item.managerId)
    
    ctx.update({"item": item, "manager": manager, "logs": item_logs})
    return templates.TemplateResponse("equipment_detail.html", ctx)

@app.get("/bookings")
async def bookings_page(request: Request):
    ctx = common_context(request)
    user = ctx['current_user']
    if not user:
        return RedirectResponse("/login")
    
    user_bookings = db.bookings if user.role in ['ADMIN', 'STAFF'] else [b for b in db.bookings if b.userId == user.id]
    # Sort by recent
    user_bookings.sort(key=lambda x: x.startTime, reverse=True)
    
    # Resolve equipment names for display
    enhanced_bookings = []
    for b in user_bookings:
        eq = db.get_equipment(b.equipmentId)
        enhanced_bookings.append({**b.dict(), "equipmentName": eq.name if eq else "Unknown", "equipmentCode": eq.code if eq else ""})

    ctx.update({"bookings": enhanced_bookings})
    return templates.TemplateResponse("bookings.html", ctx)

@app.post("/api/bookings/create")
async def create_booking(request: Request):
    data = await request.json()
    # Validate overlap here (omitted for brevity)
    new_booking = Booking(**data)
    db.bookings.append(new_booking)
    return {"success": True}

@app.get("/scan")
async def qr_scan_page(request: Request):
    return templates.TemplateResponse("qr_scanner.html", common_context(request))

@app.get("/admin")
async def admin_panel(request: Request):
    ctx = common_context(request)
    if not ctx['current_user'] or ctx['current_user'].role != 'ADMIN':
        return RedirectResponse("/")
    ctx.update({"users": db.users, "all_equipment": db.equipment})
    return templates.TemplateResponse("admin.html", ctx)
