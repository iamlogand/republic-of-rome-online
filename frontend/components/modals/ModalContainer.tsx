import SignInModal from '@/components/modals/SignInModal';
import SignOutModal from '@/components/modals/SignOutModal';
import { useModalContext } from '@/contexts/ModalContext';
import styles from "./ModalContainer.module.css"
import { useEffect, useRef, useState } from 'react';

function ModalContainer() {
  const { modal, setModal } = useModalContext();
  const [showBackdrop, setShowBackdrop] = useState(false);
  const [fadeOut, setFadeOut] = useState(false);
  const timeoutId = useRef<NodeJS.Timeout | undefined>();
  
  useEffect(() => {
    if (modal === '' && timeoutId.current == null) {
      setFadeOut(true);
      timeoutId.current = setTimeout(() => {
        setFadeOut(false);
        setShowBackdrop(false);
      }, 200);
    } else if (modal !== '') {
      if (timeoutId.current) {
        clearTimeout(timeoutId.current);
        timeoutId.current = undefined;
      }
      setFadeOut(false);
      setShowBackdrop(true);
    }
  }, [modal]);

  const renderModal = () => {
    switch (modal) {
      case "sign-in":
        return <SignInModal setModal={setModal} />
      case "sign-in-required":
        return <SignInModal setModal={setModal} sessionExpired={true} />
      case "sign-out":
        return <SignOutModal setModal={setModal} />
    }
  }
  
  return (
    <>
      {showBackdrop && <div className={`${styles.modalBackdrop} ${fadeOut ? styles.fadeOut : ''}`}></div>}
      {renderModal()}
    </>
  );
}

export default ModalContainer;
