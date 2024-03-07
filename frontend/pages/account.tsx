import { GetServerSidePropsContext } from "next"
import Head from "next/head"
import Card from "@mui/material/Card"

import { useCookieContext } from "@/contexts/CookieContext"
import getInitialCookieData from "@/functions/cookies"
import PageError from "@/components/PageError"
import Breadcrumb from "@/components/Breadcrumb"
import KeyValueList from "@/components/KeyValueList"
import Box from "@mui/material/Box"

/**
 * The component for the account page
 */
const AccountPage = () => {
  const { user } = useCookieContext()

  // Render page error if user is not signed in
  if (user === null) {
    return <PageError statusCode={401} />
  }

  const pairs = [
    { key: "Username", value: user.username },
    { key: "Email", value: user.email },
  ]

  return (
    <>
      <Head>
        <title>Account | Republic of Rome Online</title>
      </Head>
      <main aria-labelledby="page-title" className="standard-page px-8 mb-8">
        <Breadcrumb />
        <h2 className="font-semibold text-2xl tracking-tight mb-4">
          Your Account
        </h2>
        <div className="p-2 pb-4 bg-white dark:bg-neutral-700 rounded">
          <KeyValueList pairs={pairs} />
        </div>
      </main>
    </>
  )
}

export default AccountPage

export const getServerSideProps = async (
  context: GetServerSidePropsContext
) => {
  const { clientAccessToken, clientRefreshToken, clientUser } =
    getInitialCookieData(context)

  return {
    props: {
      ssrEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
    },
  }
}
