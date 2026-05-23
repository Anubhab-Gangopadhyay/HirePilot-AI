import { Router } from "express";
import { authenticate } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import { buildLeaderboards } from "../services/leaderboardService.js";

const router = Router();

router.get("/", authenticate, asyncHandler(async (req, res) => {
  const data = await buildLeaderboards();
  res.json(data);
}));

export default router;
