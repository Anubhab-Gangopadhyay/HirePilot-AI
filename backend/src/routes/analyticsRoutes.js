import { Router } from "express";
import { authenticate, requireRole } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import { buildDashboardAnalytics } from "../services/analyticsService.js";
import { refreshSocialAnalytics } from "../services/socialService.js";

const router = Router();

router.get("/dashboard", authenticate, asyncHandler(async (req, res) => {
  const dashboard = await buildDashboardAnalytics(req.user.id);
  res.json(dashboard);
}));

router.post("/refresh", authenticate, requireRole("CREATOR"), asyncHandler(async (req, res) => {
  const records = await refreshSocialAnalytics(req.user.id);
  res.json({ records });
}));

export default router;
