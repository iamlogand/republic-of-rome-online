import { AppProps } from 'next/app';
import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';

import TopBar from "@/components/TopBar";
import { RootProvider } from '@/contexts/RootContext';
import BottomBar from '@/components/BottomBar';
import ModalContainer from '@/components/modals/ModalContainer';
import PageWrapper from '@/components/PageWrapper';

import "../styles/color.css";
import "../styles/space.css";
import "../styles/master.css";
import "../styles/form.css";
import "../styles/table.css";
import "../styles/layout.css";
import "../styles/link.css";
import "../styles/heading.css";

// Highest level component in the app, except _document.tsx
function App({ Component, pageProps }: AppProps) {
  const nonModalContentRef = useRef<HTMLDivElement>(null);
  const [pageStatus, setPageStatus] = useState<number | null>(null);

  useEffect(() => {
    setPageStatus(pageProps.ssrStatus);
  }, [pageProps, pageProps.ssrStatus])

  return (
    <RootProvider pageProps={pageProps}>
      <Head>
        <title>Republic of Rome Online</title>
      </Head>
      <PageWrapper ref={nonModalContentRef} pageStatus={pageStatus} setPageStatus={setPageStatus}>
        <TopBar {...pageProps} />
        <Component {...pageProps} pageStatus={pageStatus} />
        <BottomBar />
      </PageWrapper>
      <ModalContainer nonModalContentRef={nonModalContentRef} />
    </RootProvider>
  );
}

export default App;
