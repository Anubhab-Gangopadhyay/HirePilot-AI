import { prisma } from "../config/prisma.js";

export const buildDashboardAnalytics = async (userId) => {
  const records = await prisma.analyticsData.findMany({
    where: { userId },
    orderBy: { capturedAt: "asc" },
    take: 14
  });

  const latest = records.at(-1);
  return {
    latest,
    growthSeries: records.map((record) => ({
      date: record.capturedAt,
      followers: record.followers,
      avgViews: record.avgViews
    })),
    engagementSeries: records.map((record) => ({
      date: record.capturedAt,
      engagementRate: record.engagementRate,
      avgLikes: record.avgLikes,
      avgComments: record.avgComments
    })),
    topPosts: latest?.topPosts ?? []
  };
};
