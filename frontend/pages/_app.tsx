import { useState } from 'react';
import { AppProps } from 'next/app';
import Head from 'next/head';
import TopBar from "@/components/TopBar";
import DialogBackdrop from '@/components/DialogBackdrop';
import SignInDialog from '@/components/SignInDialog';
import SignOutDialog from '@/components/SignOutDialog';
import ContextProvider from '@/contexts/ContextProvider';

import "../styles/color.css";
import "../styles/space.css";
import "../styles/master.css";
import "../styles/form.css";
import "../styles/dialog.css";
import "../styles/table.css";
import "../styles/layout.css";
import "../styles/link.css";
import "../styles/heading.css";
import BottomBar from '@/components/BottomBar';

function App({ Component, pageProps }: AppProps) {
  const [dialog, setDialog] = useState<string>('');

  const renderDialog = () => {
    switch (dialog) {
      case "sign-in":
        return <SignInDialog setDialog={setDialog} />
      case "sign-out":
        return <SignOutDialog setDialog={setDialog} />
    }
  }
  
  return (
    <ContextProvider pageProps={pageProps}>
      <Head>
        <title>Republic of Rome Online</title>
      </Head>
      <TopBar setDialog={setDialog} />
      <Component {...pageProps} />
      <BottomBar />
      {dialog !== "" && <DialogBackdrop setDialog={setDialog} />}
      {renderDialog()}
    </ContextProvider>
  );
}

export default App;
