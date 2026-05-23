import { Router } from "express";
import { prisma } from "../config/prisma.js";
import { authenticate } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";

const router = Router();

router.get("/profile", authenticate, asyncHandler(async (req, res) => {
  const user = await prisma.user.findUnique({
    where: { id: req.user.id },
    include: { creatorProfile: true, brandProfile: true, socialAccounts: true, trustMetrics: true }
  });
  res.json(user);
}));

router.put("/profile", authenticate, asyncHandler(async (req, res) => {
  const { name, city, creatorProfile, brandProfile } = req.body;
  await prisma.user.update({ where: { id: req.user.id }, data: { name, city } });

  if (req.user.role === "CREATOR" && creatorProfile) {
    await prisma.creatorProfile.update({ where: { userId: req.user.id }, data: creatorProfile });
  }

  if (req.user.role === "BRAND" && brandProfile) {
    await prisma.brandProfile.update({ where: { userId: req.user.id }, data: brandProfile });
  }

  const user = await prisma.user.findUnique({
    where: { id: req.user.id },
    include: { creatorProfile: true, brandProfile: true, socialAccounts: true, trustMetrics: true }
  });
  res.json(user);
}));

router.get("/discover", authenticate, asyncHandler(async (req, res) => {
  const { city, niche } = req.query;
  const creators = await prisma.user.findMany({
    where: {
      role: "CREATOR",
      city: city ? String(city) : undefined,
      creatorProfile: {
        is: {
          niche: niche ? String(niche) : undefined
        }
      }
    },
    include: { creatorProfile: true, trustMetrics: true }
  });
  res.json({ creators });
}));

export default router;
