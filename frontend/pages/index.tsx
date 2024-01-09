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

      <div className="flex flex-col lg:grid lg:grid-cols-2 lg:grid-rows-1 gap-8">
        <div className="flex flex-col gap-8">
          <section className="flex flex-col gap-6 p-6 bg-white shadow border-0 border-t-4 border-solid border-tyrian-300 rounded-md leading-relaxed">
            <h2 className="font-semibold text-xl tracking-tight">About</h2>
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
              By the way, this project is not for-profit and never will be—it's
              my hobby.
            </p>
          </section>
          <section className="flex flex-col gap-6 p-6 bg-white shadow border-0 border-t-4 border-solid border-tyrian-300 rounded-md leading-relaxed">
            <h2 className="font-semibold text-xl tracking-tight">Access</h2>
            <p>
              User registration is currently closed and the game is still a long
              way from being playable. However, you can sign up for the waitlist
              to receive an email when registration opens.
            </p>
          </section>
        </div>
        <section className="flex flex-col gap-6 p-6 bg-white shadow border-0 border-t-4 border-solid border-tyrian-300 rounded-md leading-relaxed">
          <h2 className="font-semibold text-xl tracking-tight">Purpose</h2>
          <p>
            As demonstrated by the Republic of Rome Table Top Simulator mod
            (which can be found{" "}
            <ExternalLink href="https://steamcommunity.com/sharedfiles/filedetails/?id=2754926674&searchtext=republic+of+rome">
              here on Steam
            </ExternalLink>
            ), this is a game that lends itself well to online play. That mod
            also demonstrates that scripting features can be used to improve the
            experience by automating some of the bookkeeping tasks in the game.
          </p>
          <p>
            This project takes the concept of automation further by guiding
            player actions and taking care of everything that is not a player
            decision.
          </p>
          <p>
            Additionally, the project departs from the traditional presentation
            of the game. There are no cards, and there is no board. The UI
            design is inspired by strategy video games that I've played, such as{" "}
            <span className="whitespace-nowrap">
              <ExternalLink href="https://store.steampowered.com/app/1158310/Crusader_Kings_III/">
                Crusader Kings III
              </ExternalLink>
              .
            </span>{" "}
            However, I'm not a professional designer or artist, so expect things
            to be far more basic than your typical high budget video game!
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
