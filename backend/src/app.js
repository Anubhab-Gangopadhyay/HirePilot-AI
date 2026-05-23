import cors from "cors";
import express from "express";
import helmet from "helmet";
import { env } from "./config/env.js";
import authRoutes from "./routes/authRoutes.js";
import userRoutes from "./routes/userRoutes.js";
import campaignRoutes from "./routes/campaignRoutes.js";
import analyticsRoutes from "./routes/analyticsRoutes.js";
import socialRoutes from "./routes/socialRoutes.js";
import aiRoutes from "./routes/aiRoutes.js";
import paymentRoutes from "./routes/paymentRoutes.js";
import leaderboardRoutes from "./routes/leaderboardRoutes.js";
import trustRoutes from "./routes/trustRoutes.js";
import { errorMiddleware, notFoundMiddleware } from "./middleware/errorMiddleware.js";

export const createApp = () => {
  const app = express();
  app.use(helmet());
  app.use(cors({ origin: env.frontendUrl, credentials: true }));
  app.use(express.json());

  app.get("/health", (req, res) => {
    res.json({ status: "ok", service: "creatorbridge-backend" });
  });

  app.use("/api/auth", authRoutes);
  app.use("/api/users", userRoutes);
  app.use("/api/campaign", campaignRoutes);
  app.use("/api/campaigns", campaignRoutes);
  app.use("/api/analytics", analyticsRoutes);
  app.use("/api/social", socialRoutes);
  app.use("/api/ai", aiRoutes);
  app.use("/api/payments", paymentRoutes);
  app.use("/api/leaderboard", leaderboardRoutes);
  app.use("/api/trust", trustRoutes);

  app.use(notFoundMiddleware);
  app.use(errorMiddleware);

  return app;
};
