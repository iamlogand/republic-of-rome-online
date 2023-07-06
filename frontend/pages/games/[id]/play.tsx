import Head from 'next/head';
import { GetServerSidePropsContext } from 'next';
import getInitialCookieData from '@/functions/cookies';

const EditGamePage = () => {

  return (
    <>
      <Head>
        <title>Playing Game - Republic of Rome Online</title>
      </Head>
      <main>
        <h2 id="page-title">Playing Game</h2>
        <section>
          This is the game page. More stuff will go here.
        </section>
      </main>
    </>
  )
}

export default EditGamePage;

export async function getServerSideProps(context: GetServerSidePropsContext) {

  const { clientAccessToken, clientRefreshToken, clientUsername, clientTimezone } = getInitialCookieData(context);

  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUsername: clientUsername,
      clientTimezone: clientTimezone
    }
  };
}
