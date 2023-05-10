import { useRouter } from 'next/router';
import { Ref, useCallback, useEffect, useRef } from 'react';
import Button from '@mui/material/Button';
import { useAuthContext } from '@/contexts/AuthContext';
import useFocusTrap from '@/hooks/useFocusTrap';
import ModalTitle from '@/components/modals/ModalTitle';
import styles from "./ModalContainer.module.css"

interface SignOutModalProps {
  setModal: Function
}

const SignOutModal = (props: SignOutModalProps) => {
  const { setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const router = useRouter();
  const modalRef: Ref<HTMLDialogElement> | undefined = useRef(null);

  useFocusTrap(modalRef);

  const handleSubmit = async () => {
    // Must navigate to home before doing anything else
    await router.push('/');
    // Clear auth data
    setAccessToken('');
    setRefreshToken('');
    setUsername('');
    props.setModal('');
  }

  const handleCancel = useCallback(async () => {
    props.setModal('');
  }, [props]);

  // Close modal using ESC key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleCancel();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleCancel]);

  return (
    <dialog open aria-modal="true" ref={modalRef}>
      <ModalTitle title="Sign out" closeAction={handleCancel} ariaLabel="Cancel" />

      <div className={styles.modalContent}>
        <p>Are you sure you want to sign out?</p>
        <div className='row' style={{margin: "20px 0", justifyContent: "space-evenly"}}>
          <Button variant="contained" onClick={handleCancel}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>Yes</Button>
        </div>
      </div>
    </dialog>
  )
}

export default SignOutModal;
