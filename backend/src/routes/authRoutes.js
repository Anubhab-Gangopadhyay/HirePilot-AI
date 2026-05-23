import bcrypt from "bcryptjs";
import { Router } from "express";
import { prisma } from "../config/prisma.js";
import { authenticate } from "../middleware/authMiddleware.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import { signToken } from "../utils/jwt.js";
import { validate, z } from "../middleware/validate.js";
import { ApiError } from "../utils/apiError.js";

const router = Router();

const registerSchema = z.object({
  body: z.object({
    name: z.string().min(2),
    email: z.string().email(),
    password: z.string().min(6),
    role: z.enum(["CREATOR", "BRAND"]),
    city: z.string().optional(),
    niche: z.string().optional(),
    platform: z.enum(["INSTAGRAM", "YOUTUBE"]).optional(),
    audienceLocation: z.string().optional(),
    companyName: z.string().optional(),
    companyInfo: z.string().optional(),
    industry: z.string().optional(),
    budget: z.number().optional()
  })
});

router.post("/register", validate(registerSchema), asyncHandler(async (req, res) => {
  const payload = req.validated.body;
  const existing = await prisma.user.findUnique({ where: { email: payload.email } });
  if (existing) {
    throw new ApiError(409, "Email already registered");
  }

  const passwordHash = await bcrypt.hash(payload.password, 10);
  const user = await prisma.user.create({
    data: {
      name: payload.name,
      email: payload.email,
      passwordHash,
      role: payload.role,
      city: payload.city,
      creatorProfile: payload.role === "CREATOR" ? {
        create: {
          niche: payload.niche ?? "Lifestyle",
          platform: payload.platform ?? "INSTAGRAM",
          audienceLocation: payload.audienceLocation ?? payload.city ?? "India"
        }
      } : undefined,
      brandProfile: payload.role === "BRAND" ? {
        create: {
          companyName: payload.companyName ?? `${payload.name} Brands`,
          companyInfo: payload.companyInfo ?? "High-growth brand partner",
          industry: payload.industry ?? "Lifestyle",
          budget: payload.budget ?? 0
        }
      } : undefined,
      trustMetrics: {
        create: {}
      }
    },
    include: { creatorProfile: true, brandProfile: true, trustMetrics: true }
  });

  const token = signToken(user);
  res.status(201).json({ token, user });
}));

router.post("/login", asyncHandler(async (req, res) => {
  const { email, password } = req.body;
  const user = await prisma.user.findUnique({
    where: { email },
    include: { creatorProfile: true, brandProfile: true, trustMetrics: true, socialAccounts: true }
  });
  if (!user) {
    throw new ApiError(401, "Invalid credentials");
  }

  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    throw new ApiError(401, "Invalid credentials");
  }

  const token = signToken(user);
  res.json({ token, user });
}));

router.get("/me", authenticate, asyncHandler(async (req, res) => {
  res.json({ user: req.user });
}));

export default router;
