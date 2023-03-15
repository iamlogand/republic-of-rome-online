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
      <input className="button" type="submit" id="auth-submit" value="Yes" />
    </form>
  )
}

export default SignOutForm;
