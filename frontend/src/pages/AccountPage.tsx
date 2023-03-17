import { useEffect, useState } from 'react';
import request from "../helpers/requestHelper"
import TopBar from "../components/TopBar"
import { Link } from 'react-router-dom';

interface AccountPageProps {
  accessToken: string,
  refreshToken: string,
  username: string
  setAuthData: Function
}

/**
 * The component for the account page
 */
const AccountPage = (props: AccountPageProps) => {
  const [email, setEmail] = useState<string>();

  useEffect(() => {
    // Get the current user's email
    const fetchData = async () => {
      const response = await request('get', 'user/detail/', props.accessToken, props.refreshToken, props.setAuthData);
      if (response) {
        setEmail(response.data.email);
      }
    }
    fetchData();
  }, [props.accessToken, props.refreshToken, props.setAuthData]);

  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div id="standard_page">
        <header className='row'>
          <Link to=".." className="button" style={{width: "90px"}}>◀&nbsp; Back</Link>
          <h2 className='no-margin'>Your Account</h2>
        </header>

        <section>
          <p>Manage your account settings here.</p>
          <table style={{maxWidth: "500px"}}>
            <tr>
              <td>Username</td>
              <td>{props.username}</td>
            </tr>
            <tr>
              <td>Email</td>
              <td>{email}</td>
            </tr>
          </table>
        </section>
      </div>
    </div>
  );
}

export default AccountPage;
