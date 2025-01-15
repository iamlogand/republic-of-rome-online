import type { Metadata } from "next"

import "./globals.css"
import { AppProvider } from "@/contexts/AppContext"
import AppWrapper from "@/components/AppWrapper"

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
        <body>
          <AppWrapper>{children}</AppWrapper>
        </body>
      </html>
    </AppProvider>
  )
}
