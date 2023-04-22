import { useAuthContext } from '@/contexts/AuthContext';
import Button from './Button';
import { useRouter } from 'next/router';
import { LegacyRef, useRef } from 'react';
import useFocusTrap from '@/hooks/useFocusTrap';

interface SignOutDialogProps {
  setDialog: Function
}

const SignOutDialog = (props: SignOutDialogProps) => {
  const { setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const router = useRouter();
  const modalRef: LegacyRef<HTMLDivElement> | undefined = useRef(null);
  const initialFocusRef: LegacyRef<HTMLDivElement> | undefined = useRef(null);

  useFocusTrap(modalRef, initialFocusRef);

  const handleSubmit = async () => {
    // Must navigate to home before doing anything else
    await router.push('/');

    // Clear auth data
    setAccessToken('');
    setRefreshToken('');
    setUsername('');
    props.setDialog('');
  }

  const handleCancel = () => {
    props.setDialog('');
  }

  return (
    <div ref={modalRef} className='dialog-container'>
      <dialog open>
        <h2>Sign Out</h2>
        <div>
          <p>Are you sure you want to sign out?</p>
          <div className='row' style={{margin: "20px 0", justifyContent: "space-evenly"}}>
            <Button text="Cancel" onClick={handleCancel} />
            <Button text="Yes" onClick={handleSubmit} width={70} ref={initialFocusRef} />
          </div>
        </div>
      </dialog>
    </div>
  )
}

export default SignOutDialog;
