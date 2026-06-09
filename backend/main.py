from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import db
from init_data import init_all
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title="口腔诊所管理系统", version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    from routers.patients import router as patients_router
    from routers.appointments import router as appointments_router
    from routers.charts import router as charts_router
    from routers.images import router as images_router
    from routers.billing import router as billing_router
    from routers.schedule import router as schedule_router
    from routers.recall import router as recall_router
    from routers.statistics import router as statistics_router
    
    app.include_router(patients_router)
    app.include_router(appointments_router)
    app.include_router(charts_router)
    app.include_router(images_router)
    app.include_router(billing_router)
    app.include_router(schedule_router)
    app.include_router(recall_router)
    app.include_router(statistics_router)
    
    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}
    
    return app

app = create_app()

@app.on_event("startup")
async def startup_event():
    init_all()
    logger.info("=" * 60)
    logger.info("口腔诊所管理系统启动")
    logger.info(f"服务端口: {settings.PORT}")
    logger.info("-" * 60)
    logger.info("已加载模块:")
    for module in db.module_names:
        count = db.get_module_count(module)
        logger.info(f"  - {module}: {count} 条数据")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
