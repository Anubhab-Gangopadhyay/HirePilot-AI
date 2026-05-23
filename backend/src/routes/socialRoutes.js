import { Router } from "express";
import { authenticate } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import {
  exchangeInstagramCode,
  exchangeYouTubeCode,
  getInstagramAuthUrl,
  getYouTubeAuthUrl,
  refreshSocialAnalytics
} from "../services/socialService.js";

const router = Router();

router.get("/instagram/login", authenticate, asyncHandler(async (req, res) => {
  res.json({ url: getInstagramAuthUrl(req.user.id) });
}));

router.get("/youtube/login", authenticate, asyncHandler(async (req, res) => {
  res.json({ url: getYouTubeAuthUrl(req.user.id) });
}));

router.get("/instagram/callback", asyncHandler(async (req, res) => {
  await exchangeInstagramCode(String(req.query.code), String(req.query.state));
  res.redirect(`${process.env.FRONTEND_URL ?? "http://localhost:3000"}/profile?connected=instagram`);
}));

router.get("/youtube/callback", asyncHandler(async (req, res) => {
  await exchangeYouTubeCode(String(req.query.code), String(req.query.state));
  res.redirect(`${process.env.FRONTEND_URL ?? "http://localhost:3000"}/profile?connected=youtube`);
}));

router.post("/sync", authenticate, asyncHandler(async (req, res) => {
  const records = await refreshSocialAnalytics(req.user.id);
  res.json({ records });
}));

export default router;
