import type { Metadata } from "next";
import localFont from "next/font/local";

import { APP_METADATA } from "@sentinel/config";

import { ThemeProvider } from "@/lib/providers/theme-provider";
import { QueryProvider } from "@/lib/providers/query-provider";
import { OrgProvider } from "@/lib/providers/org-provider";

import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
});

const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
});

export const metadata: Metadata = {
  title: {
    default: APP_METADATA.name,
    template: `%s | ${APP_METADATA.name}`,
  },
  description: APP_METADATA.description,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <QueryProvider>
          <ThemeProvider>
            <OrgProvider>{children}</OrgProvider>
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
