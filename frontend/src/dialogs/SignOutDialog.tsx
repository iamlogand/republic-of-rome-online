import { useAuth } from "../AuthContext";

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
    props.setDialog('')
  }

  const handleCancel = () => {
    props.setDialog('')
  }

  return (
    <div className='dialog-container'>
      <dialog open>
        <h2>Sign Out</h2>
        <div>
          <p>Are you sure you want to sign out?</p>
          <div className='row' style={{margin: "20px 0", justifyContent: "space-evenly"}}>
            <button onClick={handleCancel} className="button" style={{width: "90px"}}>Cancel</button>
            <button onClick={handleSubmit} className="button" style={{width: "70px"}}>Yes</button>
          </div>
        </div>
      </dialog>
    </div>
  )
}

export default SignOutDialog;
