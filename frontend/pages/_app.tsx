import { AppProps } from 'next/app';
import Head from 'next/head';
import TopBar from "@/components/TopBar";
import { RootProvider } from '@/contexts/RootContext';
import BottomBar from '@/components/BottomBar';

import "../styles/color.css";
import "../styles/space.css";
import "../styles/master.css";
import "../styles/form.css";
import "../styles/modal.css";
import "../styles/table.css";
import "../styles/layout.css";
import "../styles/link.css";
import "../styles/heading.css";
import ModalContainer from '@/components/modals/ModalContainer';

function App({ Component, pageProps }: AppProps) {
  return (
    <RootProvider pageProps={pageProps}>
      <Head>
        <title>Republic of Rome Online</title>
      </Head>
      <TopBar/>
      <Component {...pageProps} />
      <BottomBar />
      <ModalContainer />
    </RootProvider>
  );
}

export default App;
