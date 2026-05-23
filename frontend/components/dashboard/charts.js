"use client";

import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend);

export function GrowthChart({ items }) {
  const data = {
    labels: items.map((item) => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: "Followers",
        data: items.map((item) => item.followers),
        borderColor: "#0f766e",
        backgroundColor: "rgba(15,118,110,0.2)",
        tension: 0.3
      },
      {
        label: "Avg views",
        data: items.map((item) => item.avgViews),
        borderColor: "#f97316",
        backgroundColor: "rgba(249,115,22,0.15)",
        tension: 0.3
      }
    ]
  };
  return <Line data={data} options={{ responsive: true, plugins: { legend: { position: "bottom" } } }} />;
}

export function EngagementChart({ items }) {
  const data = {
    labels: items.map((item) => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: "Engagement rate",
        data: items.map((item) => item.engagementRate),
        backgroundColor: "rgba(15,118,110,0.72)"
      },
      {
        label: "Avg likes",
        data: items.map((item) => item.avgLikes),
        backgroundColor: "rgba(249,115,22,0.72)"
      }
    ]
  };
  return <Bar data={data} options={{ responsive: true, plugins: { legend: { position: "bottom" } } }} />;
}
