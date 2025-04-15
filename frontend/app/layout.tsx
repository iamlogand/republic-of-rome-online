import type { Metadata } from "next"
import "./globals.css"

import { Open_Sans } from "next/font/google"

import AppWrapper from "@/components/AppWrapper"
import { AppProvider } from "@/contexts/AppContext"

const openSans = Open_Sans({
  subsets: ["latin"],
  display: "swap",
})

export const metadata: Metadata = {
  title: "Republic of Rome Online",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <AppProvider>
      <html lang="en" className={openSans.className}>
        <body className="w-full">
          <AppWrapper>{children}</AppWrapper>
        </body>
      </html>
    </AppProvider>
  )
}
