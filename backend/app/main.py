from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
import traceback
import time

from .config import settings
from .logging_config import configure_logging, get_logger
from .api import analyze, kb_admin


configure_logging()
log = get_logger("main")

app = FastAPI(
    title="FairDeal DEBUG",
    version="1.0.0",
    default_response_class=ORJSONResponse,
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = traceback.format_exc()
    # Log to file to guarantee capture
    try:
        with open("backend_error.log", "w", encoding="utf-8") as f:
            f.write(f"Timestamp: {time.time()}\n")
            f.write(f"URL: {request.url}\n")
            f.write(error_msg)
    except Exception:
        pass # Fallback
    
    log.error(f"Global error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "details": [{"loc": [], "msg": error_msg, "type": "traceback"}]
            }
        },
    )

from fastapi.exceptions import RequestValidationError, ResponseValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = str(exc)
    log.error(f"VALIDATION ERROR: {error_msg}")
    
    details = []
    for err in exc.errors():
        details.append({
            "loc": [str(x) for x in err.get("loc", [])],
            "msg": err.get("msg", ""),
            "type": err.get("type", "")
        })
        
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": details
            }
        },
    )

@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    error_msg = str(exc)
    log.error(f"RESPONSE SCHEMA ERROR: {error_msg}")
    try:
        with open("validation_error.log", "w", encoding="utf-8") as f:
            f.write(f"Timestamp: {time.time()}\n")
            f.write(f"URL: {request.url}\n")
            f.write(f"Errors: {exc.errors()}\n")
            f.write(f"Body: {exc.body}\n")
    except Exception:
        pass
        
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "RESPONSE_SCHEMA_ERROR",
                "message": "Server response mismatch",
                "details": [{"loc": [], "msg": str(exc), "type": "schema_error"}]
            }
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    log.info("Starting FairDeal backend")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    log.info("Shutting down FairDeal backend")


app.include_router(analyze.router, prefix="/api")
app.include_router(kb_admin.router, prefix="/api/kb")

