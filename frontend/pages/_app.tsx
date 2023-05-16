import { AppProps } from 'next/app';
import { useRef } from 'react';
import Head from 'next/head';
import '@fontsource/roboto';
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
import "../styles/form.css";
import "../styles/layout.css";
import "../styles/heading.css";
import "../styles/dataGrid.css";

// Highest level component in the app, except _document.tsx
function App({ Component, pageProps }: AppProps) {
  const nonModalContentRef = useRef<HTMLDivElement>(null);

  return (
    <RootProvider pageProps={pageProps}>
      <Head>
        <title>Republic of Rome Online</title>
      </Head>
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
