import { APIRequest, APIRequestContext, expect } from "@playwright/test"

import { BACKEND, TEST_PASSWORD, ensureUser } from "./api"
import { Player } from "./auth"

const PLAYER_USERNAMES = ["test_host", "test_player2", "test_player3"]

export async function deleteGame(
  context: APIRequestContext,
  gameId: number,
): Promise<void> {
  const response = await context.delete(`${BACKEND}/api/games/${gameId}/`)
  expect(response.ok()).toBeTruthy()
}

export async function setupGame(
  request: APIRequest,
): Promise<{ gameId: number; players: Player[] }> {
  const utilCtx = await request.newContext()
  await Promise.all(PLAYER_USERNAMES.map((u) => ensureUser(utilCtx, u)))
  await utilCtx.dispose()

  const playerApis = await Promise.all(
    PLAYER_USERNAMES.map((username) =>
      request.newContext({
        httpCredentials: { username, password: TEST_PASSWORD, send: "always" },
      }),
    ),
  )
  const [hostApi, player2Api, player3Api] = playerApis

  const gameResponse = await hostApi.post(`${BACKEND}/api/games/`, {
    data: { name: `e2e-${crypto.randomUUID()}` },
  })
  expect(gameResponse.ok()).toBeTruthy()
  const gameId = (await gameResponse.json()).id

  await Promise.all([
    hostApi.post(`${BACKEND}/api/factions/`, {
      data: { game: gameId, position: 1 },
    }),
    player2Api.post(`${BACKEND}/api/factions/`, {
      data: { game: gameId, position: 2 },
    }),
    player3Api.post(`${BACKEND}/api/factions/`, {
      data: { game: gameId, position: 3 },
    }),
  ])

  expect(
    (await hostApi.post(`${BACKEND}/api/games/${gameId}/start-game/`)).ok(),
  ).toBeTruthy()

  return {
    gameId,
    players: PLAYER_USERNAMES.map((username, i) => ({
      username,
      api: playerApis[i],
    })),
  }
}

export async function skipToNextPhase(
  context: APIRequestContext,
  gameId: number,
): Promise<{ phase: string; subPhase: string }> {
  const response = await context.post(
    `${BACKEND}/api/test/skip-to-next-phase/${gameId}/`,
  )
  expect(response.ok()).toBeTruthy()
  const { phase, sub_phase: subPhase } = await response.json()
  return { phase, subPhase }
}
