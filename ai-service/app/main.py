from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.payloads import IncomeRequest, PriceRequest, RoiRequest
from app.services.model_service import load_models

app = FastAPI(title="CreatorBridge IQ AI Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "creatorbridge-ai"}


@app.post("/predict-price")
def predict_price(payload: PriceRequest) -> dict[str, float | str]:
    predicted_price = load_models()["price"].predict([
        payload.followers,
        payload.engagement_rate,
        payload.niche_score,
        payload.audience_quality,
        payload.platform_weight,
    ])
    return {"predicted_price": predicted_price, "model": "linear-regression"}


@app.post("/predict-roi")
def predict_roi(payload: RoiRequest) -> dict[str, float | str]:
    predicted_roi = load_models()["roi"].predict([
        payload.budget,
        payload.expected_reach,
        payload.engagement_rate,
        payload.conversion_rate,
        payload.avg_order_value,
    ])
    return {"predicted_roi": predicted_roi, "model": "linear-regression"}


@app.post("/predict-income")
def predict_income(payload: IncomeRequest) -> dict[str, float | str]:
    predicted_income = load_models()["income"].predict([
        payload.followers,
        payload.engagement_rate,
        payload.active_campaigns,
        payload.avg_campaign_rate,
    ])
    return {"predicted_income": predicted_income, "model": "linear-regression"}
