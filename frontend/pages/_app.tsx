import { AppProps } from 'next/app';
import { useRef } from 'react';
import Head from 'next/head';
import localFont from 'next/font/local';
import { Gentium_Plus, Open_Sans } from 'next/font/google';

import { ThemeProvider } from '@mui/material/styles';

import TopBar from "@/components/TopBar";
import { RootProvider } from '@/contexts/RootContext';
import Footer from '@/components/Footer';
import ModalContainer from '@/components/modals/ModalContainer';
import PageWrapper from '@/components/PageWrapper';
import mainTheme from "@/themes/mainTheme";

import "../styles/color.css";
import "../styles/space.css";
import "../styles/master.css";
import "../styles/heading.css";
import "../styles/dataGrid.css";

const openSansFont = Open_Sans({
  subsets: ['latin'],
  variable: '--font-open-sans'
});

const trajanFont = localFont({
  src: '../fonts/TrajanProRegular.ttf',
  variable: '--font-trajan'
});

const gentiumFont = Gentium_Plus({
  weight: "400", subsets: ['greek'],
  variable: '--font-gentium'
});

// Highest level component in the app, except _document.tsx
function App({ Component, pageProps }: AppProps) {
  const nonModalContentRef = useRef<HTMLDivElement>(null);

  return (
    <RootProvider pageProps={pageProps}>
      <Head>
        <title>Republic of Rome Online</title>
      </Head>
      <style jsx global>
        {`html {
          --font-open-sans: ${openSansFont.style.fontFamily};
          --font-trajan: ${trajanFont.style.fontFamily};
          --font-gentium: ${gentiumFont.style.fontFamily};
        }`}
      </style>
      <PageWrapper reference={nonModalContentRef}>
        <TopBar {...pageProps} />
        <ThemeProvider theme={mainTheme}>
          <Component {...pageProps} />
        </ThemeProvider>
        <Footer />
      </PageWrapper>
      <ThemeProvider theme={mainTheme}>
        <ModalContainer nonModalContentRef={nonModalContentRef} />
      </ThemeProvider>
    </RootProvider>
  );
}

export default App;
