import { Router } from "express";
import { prisma } from "../config/prisma.js";
import { authenticate, requireRole } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import { ApiError } from "../utils/apiError.js";
import { matchCreatorsForCampaign } from "../services/matchingService.js";

const router = Router();

router.post("/", authenticate, requireRole("BRAND"), asyncHandler(async (req, res) => {
  const campaign = await prisma.campaign.create({
    data: {
      ...req.body,
      brandId: req.user.id
    }
  });
  res.status(201).json(campaign);
}));

router.get("/", authenticate, asyncHandler(async (req, res) => {
  const campaigns = await prisma.campaign.findMany({
    include: { brand: { include: { brandProfile: true } }, applications: true },
    orderBy: { createdAt: "desc" }
  });
  res.json({ campaigns });
}));

async function applyToCampaign(req, res) {
  const campaignId = req.params.campaignId ?? req.body.campaignId;
  const campaign = await prisma.campaign.findUnique({ where: { id: campaignId } });
  if (!campaign) {
    throw new ApiError(404, "Campaign not found");
  }

  const application = await prisma.application.create({
    data: {
      campaignId: campaign.id,
      creatorId: req.user.id,
      message: req.body.message,
      proposedRate: req.body.proposedRate
    }
  });
  res.status(201).json(application);
}

router.post("/apply", authenticate, requireRole("CREATOR"), asyncHandler(applyToCampaign));
router.post("/:campaignId/apply", authenticate, requireRole("CREATOR"), asyncHandler(applyToCampaign));
router.get("/match-creators/:campaignId", authenticate, requireRole("BRAND"), asyncHandler(async (req, res) => {
  const matches = await matchCreatorsForCampaign(req.params.campaignId);
  res.json({ matches });
}));
router.get("/:campaignId/match-creators", authenticate, requireRole("BRAND"), asyncHandler(async (req, res) => {
  const matches = await matchCreatorsForCampaign(req.params.campaignId);
  res.json({ matches });
}));

export default router;
