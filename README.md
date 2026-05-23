# CreatorBridge IQ

CreatorBridge IQ is a production-shaped MVP for the creator economy: creators connect Instagram and YouTube analytics, brands launch campaigns, AI prices creator work, campaign-fit matching ranks talent, discovery works on a map, escrow is handled through Razorpay, and trust plus leaderboard systems reflect performance over time.

## Stack

- Frontend: Next.js App Router, Tailwind CSS v4, Chart.js, Mapbox GL
- Backend: Node.js, Express, Prisma, PostgreSQL, JWT auth
- AI service: FastAPI, scikit-learn Linear Regression
- Integrations: Instagram Graph API, YouTube Data API v3, Razorpay test mode, Mapbox

## Project structure

- `frontend/` Next.js UI with dashboard, campaigns, calculator, leaderboard, and profile/discovery flows
- `backend/` Express APIs, Prisma schema, seeds, social integrations, pricing, matching, payments, and trust logic
- `ai-service/` FastAPI prediction service for pricing, ROI, and income

## Setup

1. Copy the environment templates:
   - root: `.env.example` -> `.env`
   - backend: `backend/.env.example` -> `backend/.env`
   - frontend: `frontend/.env.example` -> `frontend/.env.local`
2. Install Node dependencies from the repo root:
   - `npm install`
3. Install Python dependencies:
   - `pip install -r ai-service/requirements.txt`
4. Generate Prisma client and run migrations:
   - `npm run prisma:generate --workspace backend`
   - `npm run prisma:migrate --workspace backend`
5. Seed the database:
   - `npm run seed`

## Run locally

Open three terminals.

1. Backend API:
   - `npm run dev:backend`
2. Frontend:
   - `npm run dev:frontend`
3. AI service:
   - `npm run dev:ai`

## Seeded accounts

- Creator: `aarav@creatorbridgeiq.com` / `Password123!`
- Creator: `naina@creatorbridgeiq.com` / `Password123!`
- Brand: `orbit@creatorbridgeiq.com` / `Password123!`

## Core API surface

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/users/profile`
- `PUT /api/users/profile`
- `GET /api/users/discover`
- `POST /api/campaign`
- `GET /api/campaigns`
- `POST /api/campaign/apply`
- `GET /api/campaign/match-creators/:campaignId`
- `GET /api/analytics/dashboard`
- `POST /api/analytics/refresh`
- `GET /api/social/instagram/login`
- `GET /api/social/youtube/login`
- `POST /api/social/sync`
- `POST /api/ai/calculate-price`
- `POST /api/ai/predict-roi`
- `POST /api/ai/predict-income`
- `POST /api/payments/escrow`
- `POST /api/payments/:paymentId/release`
- `GET /api/leaderboard`
- `POST /api/trust`

## Social integration notes

Instagram and YouTube OAuth flows are implemented with real provider endpoints and require valid application credentials in the backend environment file. The scheduler refreshes connected creator analytics every 24 hours using `node-cron`.

## Pricing intelligence

The smart pay calculator combines the requested weighted pricing formula with an AI prediction request to the FastAPI service. If the AI service is unavailable, the backend gracefully falls back to the formula output.

## Payments and trust

Escrow creation uses Razorpay test mode when keys are present. Without keys, the API still records the payment intent in manual test mode so local workflow testing can continue. Trust score updates after ratings are submitted using:

`trust_score = (rating * 0.5) + (completion * 0.3) + (response_time * 0.2)`

## Known operational requirements

- PostgreSQL must be running before Prisma migrate/seed steps.
- Instagram Graph API requires a Facebook page linked to an Instagram business account.
- YouTube OAuth requires a Google Cloud OAuth client with the redirect URI configured.
- Mapbox requires `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN` for the live map renderer.
- Razorpay requires test keys to create real orders.
