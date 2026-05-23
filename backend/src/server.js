import cron from "node-cron";
import { createApp } from "./app.js";
import { env } from "./config/env.js";
import { prisma } from "./config/prisma.js";
import { refreshSocialAnalytics } from "./services/socialService.js";

const app = createApp();

cron.schedule("0 0 * * *", async () => {
  const creators = await prisma.user.findMany({ where: { role: "CREATOR" }, include: { socialAccounts: true } });
  for (const creator of creators) {
    if (!creator.socialAccounts.length) continue;
    try {
      await refreshSocialAnalytics(creator.id);
    } catch (error) {
      console.error(`Scheduled sync failed for ${creator.id}:`, error.message);
    }
  }
});

app.listen(env.port, () => {
  console.log(`CreatorBridge IQ backend listening on port ${env.port}`);
});
