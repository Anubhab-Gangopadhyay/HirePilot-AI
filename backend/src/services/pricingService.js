import axios from "axios";
import { env } from "../config/env.js";

const nicheWeights = {
  fashion: 9,
  beauty: 8.5,
  tech: 8,
  gaming: 8.2,
  finance: 8.8,
  travel: 7.9,
  food: 7.6,
  fitness: 8.1,
  lifestyle: 7.4,
  education: 7.8
};

const platformWeights = {
  INSTAGRAM: 8.4,
  YOUTUBE: 9.1
};

const locationQuality = {
  india: 7.6,
  usa: 9,
  uk: 8.8,
  uae: 8.2,
  canada: 8.5,
  singapore: 8.7
};

const normalizeFollowers = (followers) => Math.min(10, Math.log10(Math.max(1, followers)) * 1.8);
const clamp = (value, min = 0, max = 10) => Math.max(min, Math.min(max, value));

export const calculatePrice = async (input) => {
  const engagement = clamp(input.engagementRate / 2);
  const followers = normalizeFollowers(input.followers);
  const nicheScore = nicheWeights[input.niche.toLowerCase()] ?? 7;
  const audienceQuality = locationQuality[input.audienceLocation.toLowerCase()] ?? 7;
  const platformWeight = platformWeights[input.platform.toUpperCase()] ?? 7.5;

  const priceScore =
    engagement * 0.25 +
    followers * 0.2 +
    nicheScore * 0.2 +
    audienceQuality * 0.15 +
    platformWeight * 0.2;

  const baseRate = input.followers * 0.06 + input.engagementRate * 900 + priceScore * 1200;
  const range = {
    min: Number((baseRate * 0.85).toFixed(2)),
    max: Number((baseRate * 1.15).toFixed(2))
  };

  let aiPrediction = null;
  try {
    const { data } = await axios.post(`${env.aiServiceUrl}/predict-price`, {
      followers: input.followers,
      engagement_rate: input.engagementRate,
      niche_score: nicheScore,
      audience_quality: audienceQuality,
      platform_weight: platformWeight
    }, { timeout: 4000 });
    aiPrediction = data;
  } catch {
    aiPrediction = null;
  }

  const recommended = aiPrediction?.predicted_price ?? Number(((range.min + range.max) / 2).toFixed(2));
  const marketPosition = recommended < range.min ? "underpriced" : recommended > range.max ? "overpriced" : "fairly priced";

  return {
    priceScore: Number(priceScore.toFixed(2)),
    priceRange: range,
    recommendedPrice: Number(recommended.toFixed(2)),
    confidenceScore: Number((Math.min(0.96, 0.58 + priceScore / 20)).toFixed(2)),
    insights: {
      marketPosition,
      negotiationSuggestion:
        marketPosition === "underpriced"
          ? "Your profile has room for an assertive increase. Lead with audience quality and engagement proof."
          : marketPosition === "overpriced"
            ? "Bundle deliverables or add performance clauses to support this ask."
            : "Use recent analytics and campaign outcomes to keep negotiations anchored near the midpoint.",
      aiSignal: aiPrediction?.model ?? "formula"
    }
  };
};
