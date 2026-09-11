import { expect, test } from "@playwright/test"

import { Player, loginAsBrowserUser } from "./helpers/auth"
import { deleteGame, setupGame } from "./helpers/game"

const TIMEOUT = 15000

test.describe("unaligned senators", () => {
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

  test("shows an empty unaligned senators section", async ({
    page,
    playwright,
  }) => {
    // Arrange
    ;({ gameId, players } = await setupGame(playwright.request, "mortality"))
    await loginAsBrowserUser(
      playwright.request,
      page.context(),
      players[0].username,
    )

    // Act
    await page.goto(`/games/${gameId}`)

    // Assert
    await expect(
      page.getByRole("heading", { name: "Unaligned senators" }),
    ).toBeVisible({ timeout: TIMEOUT })

    await expect(
      page.getByText("There are no unaligned senators right now"),
    ).toBeVisible()
  })
})
