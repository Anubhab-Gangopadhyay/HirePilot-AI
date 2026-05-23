import "./globals.css";

export const metadata = {
  title: "HirePilot AI",
  description: "Autonomous Multi-Agent Job Application Copilot"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
