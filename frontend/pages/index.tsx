import { useState } from "react"
import { GetServerSidePropsContext } from "next"
import Link from "next/link"
import { TextField, Button, Snackbar, Alert } from "@mui/material"
import { capitalize } from "lodash"
import SendIcon from "@mui/icons-material/Send"

import { requestWithoutAuthentication } from "@/functions/request"
import { useAuthContext } from "@/contexts/AuthContext"
import getInitialCookieData from "@/functions/cookies"
import ExternalLink from "@/components/ExternalLink"

/**
 * The component for the home page
 */
const HomePage = () => {
  const [email, setEmail] = useState("")
  const [emailFeedback, setEmailFeedback] = useState("")
  const [open, setOpen] = useState(false)
  const { user } = useAuthContext()

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

  return (
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
          className="font-semibold text-4xl tracking-tighter text-center text-tyrian-500"
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
            <div className="sm:h-[56px] flex-1 bg-stone-50">
              <TextField
                error={emailFeedback != ""}
                id="email"
                label="Your email"
                onChange={handleEmailChange}
                helperText={capitalize(emailFeedback)}
                value={email}
                variant="outlined"
                fullWidth
                className="shadow-inner"
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

      <div className="grid grid-rows-2 lg:grid-cols-2 lg:grid-rows-1 gap-8">
        <section
          aria-labelledby="notice"
          className="flex flex-col gap-6 p-6 bg-white shadow border-0 border-t-4 border-solid border-tyrian-300 rounded-md"
        >
          <h2 id="notice" className="font-semibold text-xl tracking-tight">
            The Project
          </h2>
          <p className="leading-relaxed">
            We&apos;re developing a fan-made online adaptation of the classic
            strategy board game{" "}
            <ExternalLink href="https://boardgamegeek.com/boardgame/1513/republic-rome">
              The Republic of Rome
            </ExternalLink>
            , which will be hosted here.
          </p>
          <p className="leading-relaxed">
            User registration is currently closed as we work to create a worthy
            adaptation of the original game. Stay tuned for updates and the
            opening of user registration.
          </p>

          <p className="leading-relaxed">
            This project is open source. You can find the code on{" "}
            <ExternalLink href="https://github.com/iamlogand/republic-of-rome-online">
              GitHub
            </ExternalLink>
            .
          </p>
        </section>
        <section
          aria-labelledby="wiki"
          className="flex flex-col gap-6 p-6 bg-white shadow border-0 border-t-4 border-solid border-tyrian-300 rounded-md"
        >
          <h2 id="wiki" className="font-semibold text-xl tracking-tight">
            Wiki
          </h2>
          <p className="leading-relaxed">
            Republic of Rome has a complex set of rules codified in a large and
            intimidating instruction manual. Learning and checking the rules can
            be a time consuming and often challenging experience. A potential
            solution to this problem is the{" "}
            <ExternalLink href="https://wiki.roronline.com/index.php">
              Republic of Rome Wiki
            </ExternalLink>
            .
          </p>
          <p className="leading-relaxed">
            The vision for the wiki is to create a resource that can be used as
            a player aid by <i>Republic of Rome Online</i> and the{" "}
            <i>Republic of Rome</i> board game players alike.
          </p>
        </section>
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
