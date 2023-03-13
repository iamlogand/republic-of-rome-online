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
      <label htmlFor="auth-submit">Are you sure you want to sign out?</label>
      <input className="submit ready" type="submit" id="auth-submit" value="Yes" />
    </form>
  )
}

export default SignOutForm;
