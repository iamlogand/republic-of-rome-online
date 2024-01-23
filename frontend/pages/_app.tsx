import { AppProps } from "next/app"
import { useRef } from "react"
import Head from "next/head"
import localFont from "next/font/local"
import { Gentium_Plus, Open_Sans } from "next/font/google"

import TopBar from "@/components/TopBar"
import { RootProvider } from "@/contexts/RootContext"
import Footer from "@/components/Footer"
import PageWrapper from "@/components/PageWrapper"

import "../styles/space.css"
import "../styles/master.css"
import "../styles/dataGrid.css"
import ThemeWrapper from "@/components/ThemeWrapper"

const openSansFont = Open_Sans({
  subsets: ["latin"],
  variable: "--font-open-sans",
})

const trajanFont = localFont({
  src: "../fonts/TrajanProRegular.ttf",
  variable: "--font-trajan",
})

const gentiumFont = Gentium_Plus({
  weight: "400",
  subsets: ["greek"],
  variable: "--font-gentium",
})

// Highest level component in the app, except _document.tsx
function App({ Component, pageProps }: AppProps) {
  const nonModalContentRef = useRef<HTMLDivElement>(null)

  return (
    <RootProvider pageProps={pageProps}>
      <Head>
        <title>Republic of Rome Online</title>
      </Head>
      <style jsx global>
        {`
          html {
            --font-open-sans: ${openSansFont.style.fontFamily};
            --font-trajan: ${trajanFont.style.fontFamily};
            --font-gentium: ${gentiumFont.style.fontFamily};
          }
        `}
      </style>
      <PageWrapper reference={nonModalContentRef}>
        <TopBar {...pageProps} />
        <ThemeWrapper><Component {...pageProps} /></ThemeWrapper>
        <Footer />
      </PageWrapper>
    </RootProvider>
  )
}

export default App
