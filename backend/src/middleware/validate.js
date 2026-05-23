import { z } from "zod";
import { ApiError } from "../utils/apiError.js";

export const validate = (schema) => (req, res, next) => {
  const result = schema.safeParse({ body: req.body, query: req.query, params: req.params });
  if (!result.success) {
    return next(new ApiError(400, "Validation failed", result.error.flatten()));
  }
  req.validated = result.data;
  next();
};

export { z };
