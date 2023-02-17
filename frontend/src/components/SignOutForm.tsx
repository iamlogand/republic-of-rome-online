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
      <div>Are you sure you want to sign out?</div>
      <input className="auth_submit auth_submit_ready" type="submit" value="Yes" />
    </form>
  )
}

export default SignOutForm;
