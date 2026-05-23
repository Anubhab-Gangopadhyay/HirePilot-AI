import dotenv from "dotenv";

dotenv.config();

const required = ["DATABASE_URL", "JWT_SECRET"];
for (const key of required) {
  if (!process.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}

export const env = {
  nodeEnv: process.env.NODE_ENV ?? "development",
  port: Number(process.env.PORT ?? 4000),
  databaseUrl: process.env.DATABASE_URL,
  jwtSecret: process.env.JWT_SECRET,
  frontendUrl: process.env.FRONTEND_URL ?? "http://localhost:3000",
  backendUrl: process.env.BACKEND_URL ?? "http://localhost:4000",
  aiServiceUrl: process.env.AI_SERVICE_URL ?? "http://localhost:8000",
  instagramClientId: process.env.INSTAGRAM_CLIENT_ID,
  instagramClientSecret: process.env.INSTAGRAM_CLIENT_SECRET,
  instagramRedirectUri: process.env.INSTAGRAM_REDIRECT_URI,
  googleClientId: process.env.GOOGLE_CLIENT_ID,
  googleClientSecret: process.env.GOOGLE_CLIENT_SECRET,
  googleRedirectUri: process.env.GOOGLE_REDIRECT_URI,
  youtubeApiKey: process.env.YOUTUBE_API_KEY,
  razorpayKeyId: process.env.RAZORPAY_KEY_ID,
  razorpayKeySecret: process.env.RAZORPAY_KEY_SECRET
};
