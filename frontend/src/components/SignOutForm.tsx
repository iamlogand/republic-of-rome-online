import { Link } from "react-router-dom";

interface SignOutFormProps {
  setAuthData: Function
}

/**
 * The component for the sign out form
 */
const SignOutForm = (props: SignOutFormProps) => {

  const handleSubmit = (event: any) => {
    event.preventDefault();  // Prevent default form submission behavior

    // Clear auth data
    props.setAuthData({
      accessToken: '',
      refreshToken: '',
      username: ''
    });
  }

  return (
    <form onSubmit={handleSubmit} className="auth_form">
      <p>Are you sure you want to sign out?</p>
      <div className='row' style={{margin: 0, justifyContent: "space-evenly"}}>
          <Link to=".." className="button" style={{width: "90px"}}>Cancel</Link>
          <input type="submit" value="Yes" className="button" style={{width: "70px"}} />
        </div>
    </form>
  )
}

export default SignOutForm;
