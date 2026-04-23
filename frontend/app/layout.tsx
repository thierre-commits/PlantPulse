import type { Metadata } from "next";

import "./globals.css";


export const metadata: Metadata = {
  title: "PlantPulse Dashboard",
  description: "Visualizacao de sinais e analises do PlantPulse.",
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
