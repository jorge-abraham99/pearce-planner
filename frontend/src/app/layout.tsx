import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pearce Delivery Date Planner",
  description: "Demo planner for estimating baler delivery dates from order book and labour capacity.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
