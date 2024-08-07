import { useState } from "react"
import { useRouter } from "next/router"
import { GetServerSidePropsContext } from "next"
import Head from "next/head"
import TextField from "@mui/material/TextField"
import Button from "@mui/material/Button"

import { useCookieContext } from "@/contexts/CookieContext"
import request from "@/functions/request"
import getInitialCookieData from "@/functions/cookies"
import PageError from "@/components/PageError"
import Breadcrumb from "@/components/Breadcrumb"
import Stack from "@mui/material/Stack"
import { capitalize } from "@mui/material/utils"

const NewGamePage = () => {
  const router = useRouter()
  const {
    accessToken,
    refreshToken,
    user,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useCookieContext()
  const [name, setName] = useState<string>("")
  const [nameFeedback, setNameFeedback] = useState<string>("")
  const [description, setDescription] = useState<string>("")
  const [descriptionFeedback, setDescriptionFeedback] = useState<string>("")

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setName(event.target.value)
  }

  const handleDescriptionChange = (
    event: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    setDescription(event.target.value)
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const gameData = {
      name: name,
      description: description,
    }

    const response = await request(
      "POST",
      "games/",
      accessToken,
      refreshToken,
      setAccessToken,
      setRefreshToken,
      setUser,
      gameData
    )
    if (response) {
      if (response.status === 201) {
        await router.push("/games/" + response.data.id)
      } else {
        if (response.data) {
          if (
            response.data.name &&
            Array.isArray(response.data.name) &&
            response.data.name.length > 0
          ) {
            setNameFeedback(response.data.name[0])
          } else {
            setNameFeedback("")
          }
          if (
            response.data.description &&
            Array.isArray(response.data.description) &&
            response.data.description.length > 0
          ) {
            setDescriptionFeedback(response.data.description[0])
          } else {
            setDescriptionFeedback("")
          }
        }
      }
    }
  }

  // Redirect to sign in if user is not signed in
  if (user === null) {
    router.push(`/sign-in?redirect=${router.asPath}`)
    return <PageError />
  }

  return (
    <>
      <Head>
        <title>Create Game | Republic of Rome Online</title>
      </Head>
      <main aria-label="Home Page" className="standard-page px-8 pb-8">
        <Breadcrumb />

        <h2 className="font-semibold text-xl tracking-tight mb-4">
          Create Game
        </h2>
        <section>
          <form onSubmit={handleSubmit}>
            <Stack alignItems={"start"} spacing={2}>
              <TextField
                required
                id="name"
                label="Name"
                error={nameFeedback != ""}
                onChange={handleNameChange}
                helperText={capitalize(nameFeedback)}
                style={{ width: "300px" }}
              />

              <TextField
                multiline
                id="description"
                label="Description"
                error={descriptionFeedback != ""}
                onChange={handleDescriptionChange}
                rows={3}
                style={{ width: "100%" }}
                helperText={capitalize(descriptionFeedback)}
              />

              <Button variant="contained" type="submit">
                Create
              </Button>
            </Stack>
          </form>
        </section>
      </main>
    </>
  )
}

export default NewGamePage

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
