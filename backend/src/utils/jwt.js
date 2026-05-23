import jwt from "jsonwebtoken";
import { env } from "../config/env.js";

export const signToken = (user) => jwt.sign({ sub: user.id, role: user.role }, env.jwtSecret, { expiresIn: "7d" });
export const verifyToken = (token) => jwt.verify(token, env.jwtSecret);
