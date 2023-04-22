import SignInDialog from '@/components/SignInDialog';
import SignOutDialog from '@/components/SignOutDialog';
import { useDialogContext } from '@/contexts/DialogContext';
import styles from "./DialogContainer.module.css"
import { useEffect, useRef, useState } from 'react';

function DialogContainer() {
  const { dialog, setDialog } = useDialogContext();
  const [showBackdrop, setShowBackdrop] = useState(false);
  const [fadeOut, setFadeOut] = useState(false);

  const timeoutId = useRef<NodeJS.Timeout | undefined>();
  
  useEffect(() => {
    if (dialog === '' && timeoutId.current == null) {
      setFadeOut(true);
      timeoutId.current = setTimeout(() => {
        setFadeOut(false);
        setShowBackdrop(false);
      }, 200);
    } else if (dialog !== '') {
      if (timeoutId.current) {
        clearTimeout(timeoutId.current);
        timeoutId.current = undefined;
      }
      setFadeOut(false);
      setShowBackdrop(true);
    }
  }, [dialog]);

  const renderDialog = () => {
    switch (dialog) {
      case "sign-in":
        return <SignInDialog setDialog={setDialog} />
      case "sign-in-required":
        return <SignInDialog setDialog={setDialog} sessionExpired={true} />
      case "sign-out":
        return <SignOutDialog setDialog={setDialog} />
    }
  }
  
  return (
    <>
      {showBackdrop && <div className={`${styles.dialogBackdrop} ${fadeOut ? styles.fadeOut : ''}`}></div>}
      {renderDialog()}
    </>
  );
}

export default DialogContainer;
