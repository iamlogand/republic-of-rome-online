import { useEffect, useState } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import request from '@/functions/request';
import Button from '@/components/Button';
import { GetServerSidePropsContext } from 'next';
import getInitialCookieData from '@/functions/cookies';
import Head from 'next/head';
import { useModalContext } from '@/contexts/ModalContext';

/**
 * The component for the account page
 */
const AccountPage = ({initialEmail} : {initialEmail: string}) => {
  const { accessToken, refreshToken, username, setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const [email, setEmail] = useState<string>(initialEmail);
  const { modal, setModal } = useModalContext();

  useEffect(() => {
    if (username == '') {
      setModal("sign-in-required");
    }
  }, [username, modal])

  useEffect(() => {
    // Get the current user's email
    const fetchData = async () => {
      const response = await request('GET', `users/${username}/`, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
      if (response) {
        setEmail(response.data.email);
      }
    }
    fetchData();
  }, [accessToken, refreshToken, username, setAccessToken, setRefreshToken, setUsername]);

  return (
    <>
      <Head>
        <title>Account - Republic of Rome Online</title>
      </Head>
      <main id="standard_page" aria-labelledby="page-title">
        <section className='row'>
          <Button href="..">◀&nbsp; Back</Button>
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
    </>
  );
}

export default AccountPage;

export const getServerSideProps = async (context: GetServerSidePropsContext) => {
  const { accessToken, refreshToken, username } = getInitialCookieData(context);
  
  const response = await request('GET', `users/${username}/`, accessToken, refreshToken);
  const email = response?.data?.email ?? "";

  return {
    props: {
      ssrAccessToken: accessToken,
      ssrRefreshToken: refreshToken,
      ssrUsername: username,
      initialEmail: email
    }
  };
};
