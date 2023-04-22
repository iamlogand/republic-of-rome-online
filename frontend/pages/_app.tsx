import { AppProps } from 'next/app';
import Head from 'next/head';
import TopBar from "@/components/TopBar";
import { RootProvider } from '@/contexts/RootContext';
import BottomBar from '@/components/BottomBar';
import ModalContainer from '@/components/modals/ModalContainer';
import { useRef } from 'react';

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
  
  return (
    <RootProvider pageProps={pageProps}>
      <Head>
        <title>Republic of Rome Online</title>
      </Head>
      <div ref={nonModalContentRef} className='non-modal-content'>
        <TopBar />
        <Component {...pageProps} />
        <BottomBar />
      </div>
      <ModalContainer nonModalContentRef={nonModalContentRef} />
    </RootProvider>
  );
}

export default App;
