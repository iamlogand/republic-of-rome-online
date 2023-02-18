import { useEffect, useState } from 'react';
import request from "../helpers/RequestHelper"
import "./AccountPage.css";
import TopBar from "../components/TopBar"

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
        <div id="page_content">
          <h1>Account Configuration</h1>
          <p>Manage your account settings here.</p>

          <div className="account-page_info">
            <div>Username</div>
            <div>{props.username}</div>
          </div>
          <div className="account-page_info">
            <div>Email</div>
            <div>{email}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AccountPage;
