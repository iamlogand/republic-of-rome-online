import { useEffect, useState } from 'react';
import { GetServerSidePropsContext } from 'next';
import Head from 'next/head';
import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';

import { useAuthContext } from '@/contexts/AuthContext';
import request from '@/functions/request';
import getInitialCookieData from '@/functions/cookies';
import PageError from '@/components/PageError';
import Breadcrumb from '@/components/Breadcrumb';
import KeyValueStack from '@/components/KeyValueStack';

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

  const fields = [
    { name: "Username", value: username },
    { name: "Email", value: email }
  ]

  return (
    <>
      <Head>
        <title>Account - Republic of Rome Online</title>
      </Head>
      <main aria-labelledby="page-title">
        <Breadcrumb />
        <h2>Your Account</h2>

        <Card variant="outlined">
          <KeyValueStack fields={fields} />
        </Card>
      </main>
    </>
  );
}

export default AccountPage;

export const getServerSideProps = async (context: GetServerSidePropsContext) => {
  const { clientAccessToken, clientRefreshToken, clientUsername } = getInitialCookieData(context);
  
  const response = await request('GET', `users/${clientUsername}/`, clientAccessToken, clientRefreshToken);
  const email = response?.data?.email ?? "";

  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUsername: clientUsername,
      initialEmail: email
    }
  };
};
