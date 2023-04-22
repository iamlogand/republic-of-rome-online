import { useAuthContext } from '@/contexts/AuthContext';
import Button from './Button';
import { useRouter } from 'next/router';

interface SignOutDialogProps {
  setDialog: Function
}

const SignOutDialog = (props: SignOutDialogProps) => {
  const { setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const router = useRouter();

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
    <div className='dialog-container'>
      <dialog open>
        <h2>Sign Out</h2>
        <div>
          <p>Are you sure you want to sign out?</p>
          <div className='row' style={{margin: "20px 0", justifyContent: "space-evenly"}}>
            <Button text="Cancel" onClick={handleCancel} />
            <Button text="Yes" onClick={handleSubmit} width={70} />
          </div>
        </div>
      </dialog>
    </div>
  )
}

export default SignOutDialog;
