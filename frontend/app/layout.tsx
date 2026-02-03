import type { Metadata } from "next"
import "./globals.css"

import AppWrapper from "@/components/AppWrapper"
import { AppProvider } from "@/contexts/AppContext"

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
      <html lang="en">
        <body className="w-full font-sans">
          <link rel="preconnect" href="https://fonts.googleapis.com" />
          <link
            rel="preconnect"
            href="https://fonts.gstatic.com"
            crossOrigin="anonymous"
          />
          <link
            href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300..800&family=Roboto:wght@500&display=swap"
            rel="stylesheet"
          />
          <AppWrapper>{children}</AppWrapper>
        </body>
      </html>
    </AppProvider>
  )
}
