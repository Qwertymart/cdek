import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Image from "next/image"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CDEK | Dahboard",
  description: "Dahboard for HR",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable}`}
      >
        <header  className="pt-4 pl-4">
            <Image width={148} height={22} src="https://www.cdek.ru/storage/source/logo/1/VYeDb0rvMBWDEtWovyfeTphLgDCV-gdF.svg" alt="CDEK" />
        </header>
        {children}
      </body>
    </html>
  );
}
