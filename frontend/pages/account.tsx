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
import KeyValueList from '@/components/KeyValueList';
import Box from '@mui/material/Box';

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

  const pairs = [
    { key: "Username", value: username },
    { key: "Email", value: email }
  ]

  return (
    <>
      <Head>
        <title>Account | Republic of Rome Online</title>
      </Head>
      <main aria-labelledby="page-title">
        <Breadcrumb />
        <h2>Your Account</h2>

        <Card>
          <Box margin={1}>
            <KeyValueList pairs={pairs} />
          </Box>
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
