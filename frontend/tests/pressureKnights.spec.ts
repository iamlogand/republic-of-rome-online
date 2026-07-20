import { expect, test } from "@playwright/test"

import { Player } from "./helpers/auth"
import { deleteGame, setupGame } from "./helpers/game"
import { loginAsBrowserUser } from "./helpers/auth"

const TIMEOUT = 15000

test.describe("pressure knights (forum phase)", () => {
  let gameId: number
  let players: Player[]

  test.beforeEach(async ({ playwright }) => {
    const result = await setupGame(playwright.request, "forum__attract_knight")
    gameId = result.gameId
    players = result.players
  })

  test.afterEach(async () => {
    if (!gameId) return

    try {
      await deleteGame(players[0].api, gameId)
    } catch (e) {
      console.warn("Game cleanup threw an error:", e)
    }

    await Promise.all(players.map((p) => p.api.dispose()))
  })

  test("can open Pressure knight dialog and interact with per-senator controls", async ({
    page,
    playwright,
  }) => {
    await loginAsBrowserUser(playwright.request, page.context(), players[0].username)
    await page.goto(`/games/${gameId}`)

    const pressureButton = page
      .getByRole("button", { name: "Pressure knight..." })
      .first()

    await expect(pressureButton).toBeVisible({ timeout: TIMEOUT })

    await pressureButton.click()

    const dialog = page.locator("dialog[open]")
    await expect(dialog).toBeVisible({ timeout: TIMEOUT })

    // Basic verification of the custom form UI
    await expect(dialog.getByText(/Pressure Knight/i)).toBeVisible()
    await expect(dialog.getByText(/Total knights to pressure:/)).toBeVisible()

    const numberInputs = dialog.locator('input[type="number"]')
    await expect(numberInputs.first()).toBeVisible({ timeout: TIMEOUT })

    // Interact: pressure 1 knight from the first senator and submit
    await numberInputs.first().fill("1")
    await dialog.getByRole("button", { name: "Confirm" }).click()

    await expect(dialog).not.toBeVisible({ timeout: TIMEOUT })
  })
})
