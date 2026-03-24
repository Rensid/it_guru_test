from typing import Callable
import traceback

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("app.middleware")
logging.basicConfig(level=logging.INFO)


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response

        except HTTPException:
            raise

        except NoResultFound as e:
            detail = f"{str(e)} not found"
            logger.info(f"Not found: {detail}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"Unhandled exception:\n{tb}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"},
            )
