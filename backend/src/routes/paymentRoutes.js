import { Router } from "express";
import { authenticate, requireRole } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import { createEscrowOrder, releaseEscrow } from "../services/paymentService.js";

const router = Router();

router.post("/escrow", authenticate, requireRole("BRAND"), asyncHandler(async (req, res) => {
  const result = await createEscrowOrder({ ...req.body, brandId: req.user.id });
  res.status(201).json(result);
}));

router.post("/:paymentId/release", authenticate, requireRole("BRAND"), asyncHandler(async (req, res) => {
  const payment = await releaseEscrow(req.params.paymentId, req.body.razorpayPaymentId);
  res.json(payment);
}));

export default router;
