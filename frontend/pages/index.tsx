import { useState } from "react"
import { GetServerSidePropsContext } from "next"
import Link from "next/link"
import { TextField, Button, Snackbar, Alert } from "@mui/material"
import { capitalize } from "@mui/material/utils"
import Head from "next/head"
import Image, { StaticImageData } from "next/image"

import { requestWithoutAuthentication } from "@/functions/request"
import { useCookieContext } from "@/contexts/CookieContext"
import getInitialCookieData from "@/functions/cookies"
import ExternalLink from "@/components/ExternalLink"

import Screenshot1 from "@/images/screenshots/screenshot1.png"
import Screenshot2 from "@/images/screenshots/screenshot2.png"
import Screenshot3 from "@/images/screenshots/screenshot3.png"
import Screenshot4 from "@/images/screenshots/screenshot4.png"
import Screenshot5 from "@/images/screenshots/screenshot5.png"
import Screenshot6 from "@/images/screenshots/screenshot6.png"

/**
 * The component for the home page
 */
const HomePage = () => {
  const [email, setEmail] = useState("")
  const [emailFeedback, setEmailFeedback] = useState("")
  const [open, setOpen] = useState(false)
  const { user } = useCookieContext()

  const getFixedSizeImage = (imageSource: StaticImageData) => (
    <div className="overflow-auto">
      <div className="w-full min-w-[576px] flex justify-center">
        <a
          target="_blank"
          href={imageSource.src}
          rel="noopener noreferrer"
          className="flex"
        >
          <Image
            alt="Screenshot"
            src={imageSource}
            width={576}
            height={284}
          ></Image>
        </a>
      </div>
    </div>
  )

  const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(event.target.value)
  }

  const handleSnackbarWaitlistClose = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    setOpen(false)
  }

  const handleSubmit = async (event: React.ChangeEvent<HTMLFormElement>) => {
    event.preventDefault()

    const response = await requestWithoutAuthentication(
      "POST",
      "waitlist-entries/",
      { email }
    )

    if (response) {
      if (response.status === 201) {
        setEmail("")
        setEmailFeedback("")
        setOpen(true)
      } else if (response.status === 429) {
        setEmailFeedback("Too many requests.")
      } else {
        if (response.data) {
          if (
            response.data.email &&
            Array.isArray(response.data.email) &&
            response.data.email.length > 0
          ) {
            setEmailFeedback(response.data.email[0])
          } else {
            setEmailFeedback("")
          }
        }
      }
    }
  }

  const sectionClassNames =
    "flex flex-col gap-6 p-6 bg-white dark:bg-neutral-700 shadow border-0 border-t-4 border-solid border-tyrian-300 dark:border-tyrian-500 rounded-md leading-relaxed"

  return (
    <>
      <Head>
        <meta
          name="description"
          content="A fan-made online adaption of a board game called The Republic of Rome. This open source project is currently in early development."
        />
      </Head>
      <main
        aria-label="Home Page"
        className="standard-page flex flex-col my-8 gap-8 px-2"
      >
        <div className="grid grid-cols-1 xl:grid-cols-1 gap-8">
          <div className="flex flex-col gap-6">
            <section className={sectionClassNames}>
              <h2 className="font-semibold text-xl tracking-tight">Notice</h2>
              <p>
                I was developing an online adaptation of the classic strategy
                board game{" "}
                <ExternalLink href="https://boardgamegeek.com/boardgame/1513/republic-rome">
                  The Republic of Rome
                </ExternalLink>
                . While I believe the project had great potential, after two
                years of work, I&apos;ve decided to stop development. The scope of
                the project proved to be more ambitious than I could manage with
                the time available.
              </p>
              <p>
                This project is open source, and the code is still available on{" "}
                <span className="whitespace-nowrap">
                  <ExternalLink href="https://github.com/iamlogand/republic-of-rome-online">
                    GitHub
                  </ExternalLink>
                  .
                </span>{" "}
                It is licensed under the MIT license, so anyone is free to use,
                modify, or build upon it for any purpose.
              </p>
              <p>
                Thank you to everyone who showed interest and supported the
                project.
              </p>
            </section>
          </div>
        </div>

        {user?.username && (
          <section
            aria-labelledby="features"
            className="flex flex-col gap-4 mx-6"
          >
            <h2 id="features" className="font-semibold text-xl tracking-tight">
              Exclusive Features
            </h2>
            <p>
              As a logged-in user, you can now discover and explore existing
              features and demos.
            </p>
            <div>
              <Button variant="contained" LinkComponent={Link} href="/games">
                Browse Games
              </Button>
            </div>
          </section>
        )}

        <Snackbar
          open={open}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          onClose={handleSnackbarWaitlistClose}
          className="mb-8"
        >
          <Alert
            onClose={handleSnackbarWaitlistClose}
            className="text-green-700 border border-solid border-green-700"
          >
            You joined our waitlist successfully. Thank you for your interest!
          </Alert>
        </Snackbar>
      </main>
    </>
  )
}

export default HomePage

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
