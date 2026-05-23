import { ApiError } from "../utils/apiError.js";

export const errorMiddleware = (error, req, res, next) => {
  const statusCode = error.statusCode ?? 500;
  const payload = {
    message: error.message ?? "Internal server error"
  };

  if (error.details) {
    payload.details = error.details;
  }

  if (process.env.NODE_ENV !== "production" && error.stack) {
    payload.stack = error.stack;
  }

  res.status(statusCode).json(payload);
};

export const notFoundMiddleware = (req, res, next) => {
  next(new ApiError(404, `Route not found: ${req.method} ${req.originalUrl}`));
};
