import axios from "axios";
import Razorpay from "razorpay";
import { env } from "../config/env.js";
import { prisma } from "../config/prisma.js";
import { ApiError } from "../utils/apiError.js";

const razorpay = env.razorpayKeyId && env.razorpayKeySecret
  ? new Razorpay({ key_id: env.razorpayKeyId, key_secret: env.razorpayKeySecret })
  : null;

export const createEscrowOrder = async ({ campaignId, brandId, creatorId, amount }) => {
  const payment = await prisma.payment.create({
    data: {
      campaignId,
      brandId,
      creatorId,
      amount,
      status: "PENDING"
    }
  });

  if (!razorpay) {
    return { payment, order: null, mode: "manual-test" };
  }

  const order = await razorpay.orders.create({
    amount: Math.round(amount * 100),
    currency: "INR",
    receipt: payment.id,
    payment_capture: true
  });

  await prisma.payment.update({
    where: { id: payment.id },
    data: { razorpayOrderId: order.id, status: "ESCROW_HELD" }
  });

  return { payment, order, mode: "razorpay" };
};

export const releaseEscrow = async (paymentId, razorpayPaymentId) => {
  const payment = await prisma.payment.findUnique({ where: { id: paymentId } });
  if (!payment) {
    throw new ApiError(404, "Payment not found");
  }

  return prisma.payment.update({
    where: { id: paymentId },
    data: {
      razorpayPaymentId: razorpayPaymentId ?? payment.razorpayPaymentId,
      status: "RELEASED"
    }
  });
};

export const predictRoi = async (payload) => {
  const { data } = await axios.post(`${env.aiServiceUrl}/predict-roi`, payload, { timeout: 4000 });
  return data;
};

export const predictIncome = async (payload) => {
  const { data } = await axios.post(`${env.aiServiceUrl}/predict-income`, payload, { timeout: 4000 });
  return data;
};
