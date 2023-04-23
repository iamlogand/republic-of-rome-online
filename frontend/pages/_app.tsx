import { AppProps } from 'next/app';
import Head from 'next/head';
import TopBar from "@/components/TopBar";
import { RootProvider } from '@/contexts/RootContext';
import BottomBar from '@/components/BottomBar';
import ModalContainer from '@/components/modals/ModalContainer';
import { useEffect, useRef, useState } from 'react';

import "../styles/color.css";
import "../styles/space.css";
import "../styles/master.css";
import "../styles/form.css";
import "../styles/table.css";
import "../styles/layout.css";
import "../styles/link.css";
import "../styles/heading.css";

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
      <div ref={nonModalContentRef} className='non-modal-content'>
        <TopBar {...pageProps} pageStatus={pageStatus} setPageStatus={setPageStatus} />
        <Component {...pageProps} pageStatus={pageStatus} />
        <BottomBar />
      </div>
      <ModalContainer nonModalContentRef={nonModalContentRef} />
    </RootProvider>
  );
}

export default App;
