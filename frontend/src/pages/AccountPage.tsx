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
    <main id="standard_page" aria-labelledby="page-title">
      <section className='row'>
        <Link to=".." className="button" style={{width: "90px"}}>◀&nbsp; Back</Link>
        <h2 id="page-title">Your Account</h2>
      </section>

      <section aria-labelledby="account-details">
        <h3 id="account-details">Account Details</h3>
        <p>Your account details:</p>
        <div className='table-container' style={{maxWidth: "500px"}}>
          <table>
            <tr>
              <th scope="row">Username</th>
              <td>{props.username}</td>
            </tr>
            <tr>
              <th scope="row">Email</th>
              <td>{email}</td>
            </tr>
          </table>
        </div>
      </section>
    </main>
  );
}

export default AccountPage;
