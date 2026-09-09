from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth,me,qr,applications,messages,notifications,profile,sport,cms,push,admin,dev,system,directory,trainer,admin_manage,admin_console,cms_blocks

app=FastAPI(title="Federation Boxing API",version="2.1.0",docs_url="/docs",openapi_url="/openapi.json")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for router in [auth.router,me.router,qr.router,applications.router,messages.router,notifications.router,profile.router,sport.router,cms.router,cms_blocks.router,push.router,admin.router,directory.router,trainer.router,admin_manage.router,admin_console.router,dev.router,system.router]: app.include_router(router)
