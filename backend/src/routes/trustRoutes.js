import { Router } from "express";
import { authenticate } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import { prisma } from "../config/prisma.js";
import { updateTrustScore } from "../services/trustService.js";

const router = Router();

router.post("/", authenticate, asyncHandler(async (req, res) => {
  const rating = await prisma.rating.create({ data: req.body });
  await updateTrustScore(req.body.rateeId);
  res.status(201).json(rating);
}));

export default router;
