import { useEffect, useState } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import request from '@/functions/request';
import Button from '@/components/Button';
import { GetServerSidePropsContext } from 'next';
import getInitialCookieData from '@/functions/cookies';
import Head from 'next/head';
import PageError from '@/components/PageError';
import Breadcrumb from '@/components/Breadcrumb';

interface GamePageProps {
  initialEmail: string;
}

/**
 * The component for the account page
 */
const AccountPage = (props : GamePageProps) => {
  const { accessToken, refreshToken, username, setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const [email, setEmail] = useState<string>(props.initialEmail);

  useEffect(() => {
    // Get the current user's email
    const fetchData = async () => {
      if (username) {
        const response = await request('GET', `users/${username}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
        if (response?.status == 200) {
          setEmail(response.data.email);
        }
      }
    }
    fetchData();
  }, [accessToken, refreshToken, username, setAccessToken, setRefreshToken, setUsername]);

  // Render page error if user is not signed in
  if (username == '') {
    return <PageError statusCode={401} />;
  }

  return (
    <>
      <Head>
        <title>Account - Republic of Rome Online</title>
      </Head>
      <main aria-labelledby="page-title">
        <Breadcrumb />
        <h2 id="page-title">Your Account</h2>

        <section aria-labelledby="account-details">
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
    </>
  );
}

export default AccountPage;

export const getServerSideProps = async (context: GetServerSidePropsContext) => {
  const { ssrAccessToken, ssrRefreshToken, ssrUsername } = getInitialCookieData(context);
  
  const response = await request('GET', `users/${ssrUsername}/`, ssrAccessToken, ssrRefreshToken);
  const ssrStatus = response.status ?? null;
  const email = response?.data?.email ?? "";

  return {
    props: {
      ssrEnabled: true,
      ssrAccessToken: ssrAccessToken,
      ssrRefreshToken: ssrRefreshToken,
      ssrUsername: ssrUsername,
      ssrStatus: ssrStatus,
      initialEmail: email
    }
  };
};
