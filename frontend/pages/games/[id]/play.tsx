import { GetServerSidePropsContext } from 'next'
import getInitialCookieData from '@/functions/cookies'
import request from '@/functions/request'
import { GameProvider } from '@/contexts/GameContext'
import GamePage, { GamePageProps } from '@/components/GamePage'

// Wrapper for the GamePage component with GameProvider
const GamePageWrapper = (props: GamePageProps) => {
  return <GameProvider><GamePage {...props} /></GameProvider>
}

export default GamePageWrapper

// The game and latest step is retrieved by the frontend server
export async function getServerSideProps(context: GetServerSidePropsContext) {

  // Get client cookie data from the page request
  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context)

  // Get game Id from the URL
  const gameId = context.params?.id

  // Asynchronously retrieve the game and latest step
  const requests = [
    request('GET', `games/${gameId}/`, clientAccessToken, clientRefreshToken),
    request('GET', `steps/?game=${gameId}&ordering=-index&limit=1`, clientAccessToken, clientRefreshToken)
  ]
  const [gameResponse, stepsResponse] = await Promise.all(requests)

  // Track whether there has been an authentication failure due to bad credentials
  let authFailure = false

  // Ensure that the responses are OK before getting data
  let gameJSON = null
  let stepsJSON = null
  if (gameResponse.status === 200 && stepsResponse.status === 200) {
    gameJSON = gameResponse.data
    stepsJSON = stepsResponse.data
  } else if (gameResponse.status === 401 || stepsResponse.status === 401) {
    authFailure = true
  }

  return {
    props: {
      ssrEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
      clientTimezone: clientTimezone,
      gameId: gameId,
      authFailure: authFailure,
      initialGame: gameJSON,
      initialLatestSteps: stepsJSON
    }
  };
}
