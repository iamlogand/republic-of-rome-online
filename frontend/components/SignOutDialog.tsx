import { useAuth } from '@/contexts/AuthContext';
import Button from './Button';
import router from 'next/router';

interface SignOutDialogProps {
  setDialog: Function
}

const SignOutDialog = (props: SignOutDialogProps) => {
  const { setAccessToken, setRefreshToken, setUsername } = useAuth();

  const handleSubmit = () => {
    // Clear auth data
    setAccessToken('');
    setRefreshToken('');
    setUsername('');
    props.setDialog('');
    router.push('/');
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
