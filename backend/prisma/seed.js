import bcrypt from "bcryptjs";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  await prisma.rating.deleteMany();
  await prisma.payment.deleteMany();
  await prisma.application.deleteMany();
  await prisma.campaign.deleteMany();
  await prisma.analyticsData.deleteMany();
  await prisma.socialAccount.deleteMany();
  await prisma.trustMetric.deleteMany();
  await prisma.creatorProfile.deleteMany();
  await prisma.brandProfile.deleteMany();
  await prisma.user.deleteMany();

  const passwordHash = await bcrypt.hash("Password123!", 10);

  const creatorOne = await prisma.user.create({
    data: {
      name: "Aarav Mehta",
      email: "aarav@creatorbridgeiq.com",
      passwordHash,
      role: "CREATOR",
      city: "Mumbai",
      creatorProfile: {
        create: {
          niche: "Tech",
          platform: "YOUTUBE",
          followers: 125000,
          engagementRate: 6.4,
          audienceLocation: "India",
          avgLikes: 7100,
          avgComments: 320,
          avgViews: 54000,
          audienceQuality: 8.3,
          completionRate: 9.2,
          latitude: 19.076,
          longitude: 72.8777
        }
      },
      trustMetrics: { create: { trustScore: 8.8, ratingAvg: 4.7, completionAvg: 9.2, responseAvg: 8.4 } }
    }
  });

  const creatorTwo = await prisma.user.create({
    data: {
      name: "Naina Kapoor",
      email: "naina@creatorbridgeiq.com",
      passwordHash,
      role: "CREATOR",
      city: "Delhi",
      creatorProfile: {
        create: {
          niche: "Fashion",
          platform: "INSTAGRAM",
          followers: 98000,
          engagementRate: 7.8,
          audienceLocation: "India",
          avgLikes: 8200,
          avgComments: 440,
          avgViews: 61000,
          audienceQuality: 8.6,
          completionRate: 9.5,
          latitude: 28.6139,
          longitude: 77.209
        }
      },
      trustMetrics: { create: { trustScore: 9.1, ratingAvg: 4.8, completionAvg: 9.5, responseAvg: 8.7 } }
    }
  });

  const brand = await prisma.user.create({
    data: {
      name: "Orbit Labs",
      email: "orbit@creatorbridgeiq.com",
      passwordHash,
      role: "BRAND",
      city: "Bengaluru",
      brandProfile: {
        create: {
          companyName: "Orbit Labs",
          companyInfo: "Consumer tech brand focused on creator-first product launches.",
          industry: "Tech",
          budget: 600000,
          rating: 4.6
        }
      },
      trustMetrics: { create: { trustScore: 8.9, ratingAvg: 4.6, completionAvg: 9.1, responseAvg: 8.1 } }
    }
  });

  const campaign = await prisma.campaign.create({
    data: {
      brandId: brand.id,
      title: "Creator-led smartphone launch",
      budget: 180000,
      niche: "Tech",
      requirements: "2 reels, 1 long-form review, product demo and CTA.",
      targetCity: "Mumbai",
      status: "OPEN"
    }
  });

  await prisma.application.createMany({
    data: [
      { campaignId: campaign.id, creatorId: creatorOne.id, message: "Strong fit for long-form review content.", proposedRate: 145000, status: "SHORTLISTED" },
      { campaignId: campaign.id, creatorId: creatorTwo.id, message: "Can add premium Instagram launch coverage.", proposedRate: 98000, status: "APPLIED" }
    ]
  });

  const analyticsSeed = [
    [creatorOne.id, "YOUTUBE", 118000, 5.9, 6500, 280, 50000, 4.2],
    [creatorOne.id, "YOUTUBE", 121000, 6.1, 6800, 300, 52000, 4.9],
    [creatorOne.id, "YOUTUBE", 125000, 6.4, 7100, 320, 54000, 5.4],
    [creatorTwo.id, "INSTAGRAM", 91000, 7.2, 7600, 380, 56000, 5.1],
    [creatorTwo.id, "INSTAGRAM", 95000, 7.5, 7900, 410, 59000, 5.8],
    [creatorTwo.id, "INSTAGRAM", 98000, 7.8, 8200, 440, 61000, 6.2]
  ];

  for (const [userId, platform, followers, engagementRate, avgLikes, avgComments, avgViews, growth] of analyticsSeed) {
    await prisma.analyticsData.create({
      data: {
        userId,
        platform,
        followers,
        engagementRate,
        avgLikes,
        avgComments,
        avgViews,
        growth,
        topPosts: [
          { title: "Launch week feature", views: avgViews + 4000, likes: avgLikes + 500 },
          { title: "Audience Q&A", views: avgViews - 2000, likes: avgLikes - 250 }
        ]
      }
    });
  }

  await prisma.payment.create({
    data: {
      campaignId: campaign.id,
      brandId: brand.id,
      creatorId: creatorOne.id,
      amount: 145000,
      status: "ESCROW_HELD",
      razorpayOrderId: "order_seed_001"
    }
  });
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (error) => {
    console.error(error);
    await prisma.$disconnect();
    process.exit(1);
  });
