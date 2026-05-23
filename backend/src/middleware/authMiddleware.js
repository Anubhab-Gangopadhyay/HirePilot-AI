import { prisma } from "../config/prisma.js";
import { ApiError } from "../utils/apiError.js";
import { verifyToken } from "../utils/jwt.js";

export const authenticate = async (req, res, next) => {
  try {
    const header = req.headers.authorization;
    if (!header?.startsWith("Bearer ")) {
      return next(new ApiError(401, "Authentication required"));
    }

    const token = header.slice(7);
    const payload = verifyToken(token);
    const user = await prisma.user.findUnique({
      where: { id: payload.sub },
      include: {
        creatorProfile: true,
        brandProfile: true,
        trustMetrics: true,
        socialAccounts: true
      }
    });

    if (!user) {
      return next(new ApiError(401, "Invalid session"));
    }

    req.user = user;
    next();
  } catch (error) {
    next(new ApiError(401, "Invalid or expired token"));
  }
};

export const requireRole = (...roles) => (req, res, next) => {
  if (!req.user || !roles.includes(req.user.role)) {
    return next(new ApiError(403, "You do not have access to this resource"));
  }
  next();
};
