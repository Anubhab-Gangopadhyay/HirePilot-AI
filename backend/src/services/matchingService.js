import { prisma } from "../config/prisma.js";

const normalise = (value, max = 10) => Math.max(0, Math.min(max, value));

export const matchCreatorsForCampaign = async (campaignId) => {
  const campaign = await prisma.campaign.findUnique({ where: { id: campaignId } });
  const creators = await prisma.user.findMany({
    where: { role: "CREATOR" },
    include: { creatorProfile: true, trustMetrics: true }
  });

  return creators
    .filter((creator) => creator.creatorProfile)
    .map((creator) => {
      const profile = creator.creatorProfile;
      const nicheMatch = profile.niche.toLowerCase() === campaign.niche.toLowerCase() ? 10 : 5.5;
      const engagement = normalise(profile.engagementRate / 2);
      const locationMatch = campaign.targetCity && creator.city?.toLowerCase() === campaign.targetCity.toLowerCase() ? 10 : 6;
      const score = nicheMatch * 0.4 + engagement * 0.3 + locationMatch * 0.3;
      return {
        creatorId: creator.id,
        name: creator.name,
        niche: profile.niche,
        platform: profile.platform,
        engagementRate: profile.engagementRate,
        followers: profile.followers,
        trustScore: creator.trustMetrics?.trustScore ?? 0,
        score: Number(score.toFixed(2))
      };
    })
    .sort((a, b) => b.score - a.score);
};
