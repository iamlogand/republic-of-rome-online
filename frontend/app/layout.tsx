import type { Metadata } from "next"
import { Open_Sans } from 'next/font/google'

import "./globals.css"
import { AppProvider } from "@/contexts/AppContext"
import AppWrapper from "@/components/AppWrapper"

const openSans = Open_Sans({
  subsets: ['latin'],
  display: 'swap',
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
        <body>
          <AppWrapper>{children}</AppWrapper>
        </body>
      </html>
    </AppProvider>
  )
}
