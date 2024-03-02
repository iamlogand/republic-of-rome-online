import { useState } from "react"
import { GetServerSidePropsContext } from "next"
import Link from "next/link"
import { TextField, Button, Snackbar, Alert } from "@mui/material"
import { capitalize } from "@mui/material/utils"
import Head from "next/head"
import Image, { StaticImageData } from "next/image"

import { requestWithoutAuthentication } from "@/functions/request"
import { useAuthContext } from "@/contexts/AuthContext"
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
  const { user } = useAuthContext()

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
        <section
          aria-labelledby="waitlist"
          className="flex flex-col items-center gap-5 mx-6 mb-2"
        >
          <h2
            id="waitlist"
            className="font-semibold text-4xl tracking-tighter text-center text-tyrian-500 dark:text-tyrian-300"
          >
            Join the Waitlist
          </h2>
          <div className="flex flex-col gap-6 items-stretch">
            <p className="text-center">
              Sign up to receive an email when user registration opens
            </p>
            <form
              onSubmit={handleSubmit}
              className="flex flex-col sm:flex-row gap-3"
            >
              <div className="sm:h-[56px] flex-1">
                <TextField
                  error={emailFeedback != ""}
                  id="email"
                  label="Your email"
                  onChange={handleEmailChange}
                  helperText={capitalize(emailFeedback)}
                  value={email}
                  variant="outlined"
                  fullWidth
                />
              </div>
              <div className="sm:h-[56px] self-center sm:self-start">
                <Button
                  variant="outlined"
                  type="submit"
                  size="large"
                  className="h-full"
                  color="primary"
                >
                  Join
                </Button>
              </div>
            </form>
          </div>
        </section>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          <div className="flex flex-col gap-6">
            <section className={sectionClassNames}>
              <h2 className="font-semibold text-xl tracking-tight">
                About the Game
              </h2>
              <p>
                I&apos;m developing an online adaptation of the classic strategy
                board game{" "}
                <ExternalLink href="https://boardgamegeek.com/boardgame/1513/republic-rome">
                  The Republic of Rome
                </ExternalLink>
                , which will be hosted here.
              </p>
              <p>
                This project is open source, and you can find the code{" "}
                <span className="whitespace-nowrap">
                  <ExternalLink href="https://github.com/iamlogand/republic-of-rome-online">
                    here on GitHub
                  </ExternalLink>
                  .
                </span>{" "}
                This project is not for-profit and never will be—it&apos;s my
                hobby.
              </p>
            </section>
            <section className={sectionClassNames}>
              <h2 className="font-semibold text-xl tracking-tight">
                User Registration
              </h2>
              <p>
                User registration is currently closed and the game is still a
                long way from being playable. However, you can sign up for the
                waitlist to receive an email when registration opens.
              </p>
            </section>
            <section className={sectionClassNames}>
              <h2 className="font-semibold text-xl tracking-tight">
                Purpose of the Game
              </h2>
              <p>
                As demonstrated by the Republic of Rome Table Top Simulator mod
                (which can be found{" "}
                <ExternalLink href="https://steamcommunity.com/sharedfiles/filedetails/?id=2754926674&searchtext=republic+of+rome">
                  here on Steam
                </ExternalLink>
                ), this is a game that lends itself well to online play. That
                mod also demonstrates that scripting features can be used to
                improve the experience by automating some of the bookkeeping
                tasks in the game.
              </p>
              <p>
                This project takes the concept of automation further by guiding
                player actions and taking care of everything that is not a
                player decision.
              </p>
              <p>
                Additionally, the project departs from the traditional
                presentation of the game. There are no cards, and there is no
                board. The UI design is inspired by strategy video games that
                I&apos;ve played, such as{" "}
                <span className="whitespace-nowrap">
                  <ExternalLink href="https://store.steampowered.com/app/1158310/Crusader_Kings_III/">
                    Crusader Kings III
                  </ExternalLink>
                  .
                </span>{" "}
                However, I&apos;m not a professional designer or artist, so
                expect things to be far more basic than your typical high budget
                video game!
              </p>
            </section>
          </div>
          <div className="h-full hidden xl:flex flex-col">
            <h2 className="font-semibold text-xl tracking-tight flex justify-center mb-3">
              Screenshots
            </h2>
            <div className="grow flex flex-col justify-between gap-6">
              {getFixedSizeImage(Screenshot1)}
              {getFixedSizeImage(Screenshot2)}
              {getFixedSizeImage(Screenshot3)}
            </div>
          </div>
        </div>

        <div className="w-full hidden xl:grid grid-cols-2 gap-8">
          {getFixedSizeImage(Screenshot4)}
          {getFixedSizeImage(Screenshot5)}
          {getFixedSizeImage(Screenshot6)}
        </div>

        <div className="flex xl:hidden flex-col gap-8">
          <h2 className="font-semibold text-xl tracking-tight flex justify-center">
            Screenshots
          </h2>
          {getFixedSizeImage(Screenshot1)}
          {getFixedSizeImage(Screenshot2)}
          {getFixedSizeImage(Screenshot3)}
          {getFixedSizeImage(Screenshot4)}
          {getFixedSizeImage(Screenshot5)}
          {getFixedSizeImage(Screenshot6)}
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
