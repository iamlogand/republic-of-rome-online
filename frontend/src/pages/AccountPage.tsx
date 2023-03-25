import { useEffect, useState } from 'react';
import request from "../helpers/requestHelper"
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';

/**
 * The component for the account page
 */
const AccountPage = () => {
  const { accessToken, refreshToken, username, setAccessToken, setRefreshToken, setUsername } = useAuth();
  const [email, setEmail] = useState<string>();

  useEffect(() => {
    // Get the current user's email
    const fetchData = async () => {
      const response = await request('GET', 'user/detail/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
      if (response) {
        setEmail(response.data.email);
      }
    }
    fetchData();
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername]);

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
            <thead>
              <tr>
                <th scope="row">Username</th>
                <td>{username}</td>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Email</th>
                <td>{email}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

export default AccountPage;
