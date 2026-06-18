from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.exports.bookings import router as bookings_router
from app.api.routes.exports.customers import router as customers_router
from app.api.routes.exports.payments import router as payments_router
from app.api.routes.exports.custody import router as custody_router
from app.api.routes.exports.schedules import router as schedules_router
from app.api.routes.exports.tickets import router as tickets_router
from app.api.routes.exports.reports import router as reports_router

router = APIRouter(prefix='/exports', tags=['exports'])

router.include_router(customers_router)
router.include_router(bookings_router)
router.include_router(payments_router)
router.include_router(custody_router)
router.include_router(schedules_router)
router.include_router(tickets_router)
router.include_router(reports_router)
