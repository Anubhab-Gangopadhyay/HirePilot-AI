import { prisma } from "../config/prisma.js";

const ranked = (items, getScore) => items
  .map((item) => ({ ...item, score: Number(getScore(item).toFixed(2)) }))
  .sort((a, b) => b.score - a.score)
  .map((item, index) => ({ ...item, rank: index + 1 }));

export const buildLeaderboards = async () => {
  const creators = await prisma.user.findMany({
    where: { role: "CREATOR" },
    include: { creatorProfile: true, analyticsRecords: { orderBy: { capturedAt: "desc" }, take: 2 } }
  });
  const brands = await prisma.user.findMany({
    where: { role: "BRAND" },
    include: { brandProfile: true, paymentsAsBrand: true }
  });

  const nicheEngagement = ranked(
    creators.filter((creator) => creator.creatorProfile),
    (creator) => creator.creatorProfile.engagementRate * 0.4 + creator.creatorProfile.completionRate * 0.3 + creator.creatorProfile.audienceQuality * 0.3
  ).map((entry) => ({
    id: entry.id,
    name: entry.name,
    niche: entry.creatorProfile.niche,
    platform: entry.creatorProfile.platform,
    score: entry.score,
    rank: entry.rank
  }));

  const risingCreators = ranked(
    creators.filter((creator) => creator.analyticsRecords.length >= 1 && creator.creatorProfile),
    (creator) => {
      const latest = creator.analyticsRecords[0];
      return latest.growth * 0.6 + creator.creatorProfile.engagementRate * 0.4;
    }
  ).map((entry) => ({
    id: entry.id,
    name: entry.name,
    score: entry.score,
    growth: entry.analyticsRecords[0]?.growth ?? 0,
    rank: entry.rank
  }));

  const roiBased = ranked(
    creators.filter((creator) => creator.creatorProfile),
    (creator) => creator.creatorProfile.engagementRate * 0.5 + creator.creatorProfile.avgViews / 1000 * 0.5
  ).map((entry) => ({
    id: entry.id,
    name: entry.name,
    score: entry.score,
    avgViews: entry.creatorProfile.avgViews,
    rank: entry.rank
  }));

  const brandLeaderboard = ranked(
    brands.filter((brand) => brand.brandProfile),
    (brand) => {
      const payoutTotal = brand.paymentsAsBrand.reduce((sum, payment) => sum + payment.amount, 0);
      return payoutTotal / 1000 * 0.6 + brand.brandProfile.rating * 4;
    }
  ).map((entry) => ({
    id: entry.id,
    name: entry.brandProfile.companyName,
    score: entry.score,
    payouts: entry.paymentsAsBrand.reduce((sum, payment) => sum + payment.amount, 0),
    rank: entry.rank
  }));

  return { nicheEngagement, risingCreators, roiBased, brandLeaderboard };
};
