import { Router } from "express";
import { authenticate } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import { calculatePrice } from "../services/pricingService.js";
import { predictIncome, predictRoi } from "../services/paymentService.js";

const router = Router();

router.post("/calculate-price", authenticate, asyncHandler(async (req, res) => {
  const result = await calculatePrice(req.body);
  res.json(result);
}));

router.post("/predict-roi", authenticate, asyncHandler(async (req, res) => {
  const result = await predictRoi(req.body);
  res.json(result);
}));

router.post("/predict-income", authenticate, asyncHandler(async (req, res) => {
  const result = await predictIncome(req.body);
  res.json(result);
}));

export default router;
