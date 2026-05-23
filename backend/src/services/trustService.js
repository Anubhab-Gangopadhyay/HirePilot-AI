import { prisma } from "../config/prisma.js";

export const updateTrustScore = async (userId) => {
  const ratings = await prisma.rating.findMany({ where: { rateeId: userId } });
  if (!ratings.length) {
    return prisma.trustMetric.upsert({
      where: { userId },
      update: { trustScore: 0, ratingAvg: 0, completionAvg: 0, responseAvg: 0 },
      create: { userId, trustScore: 0, ratingAvg: 0, completionAvg: 0, responseAvg: 0 }
    });
  }

  const ratingAvg = ratings.reduce((sum, entry) => sum + entry.rating, 0) / ratings.length;
  const completionAvg = ratings.reduce((sum, entry) => sum + entry.completion, 0) / ratings.length;
  const responseAvg = ratings.reduce((sum, entry) => sum + entry.responseTime, 0) / ratings.length;
  const trustScore = ratingAvg * 0.5 + completionAvg * 0.3 + responseAvg * 0.2;

  return prisma.trustMetric.upsert({
    where: { userId },
    update: { trustScore, ratingAvg, completionAvg, responseAvg },
    create: { userId, trustScore, ratingAvg, completionAvg, responseAvg }
  });
};
