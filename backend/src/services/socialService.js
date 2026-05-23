import axios from "axios";
import dayjs from "dayjs";
import { google } from "googleapis";
import pkg from "@prisma/client";
const { Platform } = pkg;
import { prisma } from "../config/prisma.js";
import { env } from "../config/env.js";
import { ApiError } from "../utils/apiError.js";

const instagramBase = "https://graph.facebook.com/v19.0";

const oauthClient = new google.auth.OAuth2(env.googleClientId, env.googleClientSecret, env.googleRedirectUri);

const average = (items, field) => {
  if (!items.length) return 0;
  return items.reduce((sum, item) => sum + Number(item[field] ?? 0), 0) / items.length;
};

const buildAnalyticsPayload = (platform, raw) => ({
  platform,
  followers: raw.followers,
  engagementRate: raw.engagementRate,
  avgLikes: raw.avgLikes,
  avgComments: raw.avgComments,
  avgViews: raw.avgViews,
  growth: raw.growth,
  topPosts: raw.topPosts
});

export const getInstagramAuthUrl = (userId) => {
  const params = new URLSearchParams({
    client_id: env.instagramClientId,
    redirect_uri: env.instagramRedirectUri,
    scope: "instagram_basic,instagram_manage_insights,pages_show_list,pages_read_engagement",
    response_type: "code",
    state: userId
  });
  return `https://www.facebook.com/v19.0/dialog/oauth?${params.toString()}`;
};

export const getYouTubeAuthUrl = (userId) => oauthClient.generateAuthUrl({
  access_type: "offline",
  prompt: "consent",
  scope: ["https://www.googleapis.com/auth/youtube.readonly"],
  state: userId
});

export const exchangeInstagramCode = async (code, userId) => {
  if (!env.instagramClientId || !env.instagramClientSecret) {
    throw new ApiError(400, "Instagram OAuth is not configured");
  }

  const tokenResponse = await axios.get(`${instagramBase}/oauth/access_token`, {
    params: {
      client_id: env.instagramClientId,
      client_secret: env.instagramClientSecret,
      grant_type: "authorization_code",
      redirect_uri: env.instagramRedirectUri,
      code
    }
  });

  const token = tokenResponse.data.access_token;
  const { data: me } = await axios.get(`${instagramBase}/me/accounts`, {
    params: {
      access_token: token
    }
  });

  const page = me.data?.[0];
  if (!page?.instagram_business_account?.id) {
    throw new ApiError(400, "No Instagram business account connected to the selected Facebook page");
  }

  await prisma.socialAccount.upsert({
    where: { userId_platform: { userId, platform: Platform.INSTAGRAM } },
    update: {
      username: page.name,
      accessToken: token,
      accountId: page.instagram_business_account.id,
      metadata: page,
      tokenExpiry: dayjs().add(55, "day").toDate()
    },
    create: {
      userId,
      platform: Platform.INSTAGRAM,
      username: page.name,
      accessToken: token,
      accountId: page.instagram_business_account.id,
      metadata: page,
      tokenExpiry: dayjs().add(55, "day").toDate()
    }
  });
};

export const exchangeYouTubeCode = async (code, userId) => {
  const { tokens } = await oauthClient.getToken(code);
  oauthClient.setCredentials(tokens);
  const youtube = google.youtube({ version: "v3", auth: oauthClient });
  const channelResponse = await youtube.channels.list({ part: ["snippet", "statistics"], mine: true });
  const channel = channelResponse.data.items?.[0];

  if (!channel) {
    throw new ApiError(400, "No YouTube channel available for this Google account");
  }

  await prisma.socialAccount.upsert({
    where: { userId_platform: { userId, platform: Platform.YOUTUBE } },
    update: {
      username: channel.snippet?.title ?? "YouTube Creator",
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      tokenExpiry: tokens.expiry_date ? new Date(tokens.expiry_date) : null,
      accountId: channel.id,
      metadata: channel
    },
    create: {
      userId,
      platform: Platform.YOUTUBE,
      username: channel.snippet?.title ?? "YouTube Creator",
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      tokenExpiry: tokens.expiry_date ? new Date(tokens.expiry_date) : null,
      accountId: channel.id,
      metadata: channel
    }
  });
};

export const fetchInstagramStats = async (userId) => {
  const account = await prisma.socialAccount.findUnique({ where: { userId_platform: { userId, platform: Platform.INSTAGRAM } } });
  if (!account) {
    throw new ApiError(404, "Instagram account not connected");
  }

  const { data: profile } = await axios.get(`${instagramBase}/${account.accountId}`, {
    params: {
      fields: "followers_count,media_count,username",
      access_token: account.accessToken
    }
  });

  const { data: mediaResponse } = await axios.get(`${instagramBase}/${account.accountId}/media`, {
    params: {
      fields: "id,caption,like_count,comments_count,media_type,permalink,timestamp",
      access_token: account.accessToken,
      limit: 10
    }
  });

  const posts = mediaResponse.data ?? [];
  const avgLikes = average(posts, "like_count");
  const avgComments = average(posts, "comments_count");
  const engagementRate = profile.followers_count ? ((avgLikes + avgComments) / profile.followers_count) * 100 : 0;

  return buildAnalyticsPayload(Platform.INSTAGRAM, {
    followers: profile.followers_count ?? 0,
    engagementRate,
    avgLikes,
    avgComments,
    avgViews: avgLikes * 2.4,
    growth: Number((engagementRate * 1.2).toFixed(2)),
    topPosts: posts.slice(0, 5)
  });
};

export const fetchYouTubeStats = async (userId) => {
  const account = await prisma.socialAccount.findUnique({ where: { userId_platform: { userId, platform: Platform.YOUTUBE } } });
  if (!account) {
    throw new ApiError(404, "YouTube account not connected");
  }

  oauthClient.setCredentials({
    access_token: account.accessToken,
    refresh_token: account.refreshToken,
    expiry_date: account.tokenExpiry?.getTime()
  });

  const youtube = google.youtube({ version: "v3", auth: oauthClient });
  const channelResponse = await youtube.channels.list({ part: ["statistics", "snippet"], mine: true });
  const channel = channelResponse.data.items?.[0];
  if (!channel) {
    throw new ApiError(404, "YouTube channel not found");
  }

  const videosResponse = await youtube.search.list({ part: ["snippet"], forMine: true, maxResults: 8, type: ["video"] });
  const videoIds = videosResponse.data.items?.map((item) => item.id?.videoId).filter(Boolean) ?? [];
  const statsResponse = videoIds.length
    ? await youtube.videos.list({ part: ["statistics", "snippet"], id: videoIds })
    : { data: { items: [] } };
  const videos = statsResponse.data.items ?? [];

  const avgViews = average(videos.map((video) => video.statistics ?? {}), "viewCount");
  const avgLikes = average(videos.map((video) => video.statistics ?? {}), "likeCount");
  const avgComments = average(videos.map((video) => video.statistics ?? {}), "commentCount");
  const subscribers = Number(channel.statistics?.subscriberCount ?? 0);
  const engagementRate = subscribers ? ((avgLikes + avgComments) / subscribers) * 100 : 0;

  return buildAnalyticsPayload(Platform.YOUTUBE, {
    followers: subscribers,
    engagementRate,
    avgLikes,
    avgComments,
    avgViews,
    growth: Number((engagementRate * 0.9).toFixed(2)),
    topPosts: videos.slice(0, 5).map((video) => ({
      id: video.id,
      title: video.snippet?.title,
      views: Number(video.statistics?.viewCount ?? 0),
      likes: Number(video.statistics?.likeCount ?? 0),
      comments: Number(video.statistics?.commentCount ?? 0)
    }))
  });
};

export const refreshSocialAnalytics = async (userId) => {
  const user = await prisma.user.findUnique({ where: { id: userId }, include: { socialAccounts: true, creatorProfile: true } });
  if (!user) {
    throw new ApiError(404, "User not found");
  }

  const analyticsRecords = [];
  for (const account of user.socialAccounts) {
    const data = account.platform === Platform.INSTAGRAM
      ? await fetchInstagramStats(userId)
      : await fetchYouTubeStats(userId);

    analyticsRecords.push(await prisma.analyticsData.create({ data: { userId, ...data } }));

    if (user.creatorProfile) {
      await prisma.creatorProfile.update({
        where: { userId },
        data: {
          platform: data.platform,
          followers: data.followers,
          engagementRate: data.engagementRate,
          avgLikes: data.avgLikes,
          avgComments: data.avgComments,
          avgViews: data.avgViews
        }
      });
    }

    await prisma.socialAccount.update({ where: { id: account.id }, data: { lastSyncedAt: new Date() } });
  }

  return analyticsRecords;
};
