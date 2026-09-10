import { expect, test } from "@playwright/test"

import { Player, loginAsBrowserUser } from "./helpers/auth"
import { deleteGame, setupGame } from "./helpers/game"

const TIMEOUT = 15000

test.describe("concession capitalization", () => {
  let gameId: number
  let players: Player[]

  test.afterEach(async () => {
    if (!gameId) return

    try {
      await deleteGame(players[0].api, gameId)
    } catch (e) {
      console.warn("Game cleanup threw an error:", e)
    }

    await Promise.all(players.map((p) => p.api.dispose()))
  })

  test("capitalizes only the first letter of concession names", async ({
    page,
    playwright,
  }) => {
    // Arrange
    ;({ gameId, players } = await setupGame(
      playwright.request,
      "revenue__concession_capitalization",
    ))
    await loginAsBrowserUser(
      playwright.request,
      page.context(),
      players[0].username,
    )

    // Act
    await page.goto(`/games/${gameId}`)

    // Assert
    await expect(
      page.getByText("Ship building", { exact: true }),
    ).toBeVisible({ timeout: TIMEOUT })
    await expect(
      page.getByText("Aegyptian grain", { exact: true }),
    ).toBeVisible()
    const armaments = page.getByText("Armaments", { exact: true })
    await expect(armaments).toBeVisible()
    await armaments.hover()
    await expect(
      page.getByText("2T per new legion raised", { exact: true }),
    ).toBeVisible()
    await expect(page.getByText("Mining", { exact: true })).toBeVisible()
    await expect(
      page.getByText("Harbor fees", { exact: true }),
    ).toBeVisible()
    await expect(
      page.getByText("Ship Building", { exact: true }),
    ).not.toBeVisible()
    await expect(
      page.getByText("Harbor Fees", { exact: true }),
    ).not.toBeVisible()
  })
})
