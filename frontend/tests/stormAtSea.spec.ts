import { expect, test } from "@playwright/test"

import { Player, loginAsBrowserUser } from "./helpers/auth"
import { deleteGame, setupGame } from "./helpers/game"

const TIMEOUT = 15000

test.describe("storm at sea (forum phase)", () => {
  let gameId: number
  let players: Player[]

  test.beforeEach(async ({ playwright }) => {
    const result = await setupGame(playwright.request, "forum__storm_at_sea")
    gameId = result.gameId
    players = result.players
  })

  test.afterEach(async () => {
    if (!gameId) return

    try {
      await deleteGame(players[0].api, gameId)
    } catch (error) {
      console.warn("Game cleanup threw an error:", error)
    }

    await Promise.all(players.map((player) => player.api.dispose()))
  })

  test("lets only the HRAO select the exact number of Roman fleets", async ({
    browser,
    page,
    playwright,
  }) => {
    await loginAsBrowserUser(
      playwright.request,
      page.context(),
      players[0].username,
    )
    await page.goto(`/games/${gameId}`)

    const otherContext = await browser.newContext()
    await loginAsBrowserUser(
      playwright.request,
      otherContext,
      players[1].username,
    )
    const otherPage = await otherContext.newPage()
    await otherPage.goto(`/games/${gameId}`)
    await expect(
      otherPage.getByText("State treasury", { exact: true }),
    ).toBeVisible({ timeout: TIMEOUT })
    await expect(
      otherPage.getByRole("button", {
        name: "Resolve storm at sea...",
        exact: true,
      }),
    ).toHaveCount(0)
    await otherContext.close()

    const actionButton = page.getByRole("button", {
      name: "Resolve storm at sea...",
      exact: true,
    })
    await expect(actionButton).toBeVisible({ timeout: TIMEOUT })
    await actionButton.click()

    const dialog = page.locator("dialog[open]")
    await expect(dialog).toBeVisible({ timeout: TIMEOUT })
    await expect(
      dialog.getByText("Select exactly 2 Roman fleets to eliminate."),
    ).toBeVisible()
    await expect(dialog.getByRole("group", { name: "Reserve" })).toBeVisible()
    await expect(
      dialog.getByRole("button", { name: "Clear", exact: true }),
    ).toBeVisible()
    await expect(
      dialog.getByRole("button", { name: "All", exact: true }),
    ).toHaveCount(0)

    const confirmButton = dialog.getByRole("button", { name: "Confirm" })
    const fleetI = dialog.getByRole("checkbox", {
      name: "Fleet I",
      exact: true,
    })
    const fleetII = dialog.getByRole("checkbox", {
      name: "Fleet II",
      exact: true,
    })
    const fleetIII = dialog.getByRole("checkbox", {
      name: "Fleet III",
      exact: true,
    })

    await expect(confirmButton).toBeDisabled()
    await fleetI.check()
    await expect(dialog.getByText("Selected: 1 / 2 required")).toBeVisible()
    await fleetII.check()
    await expect(confirmButton).toBeEnabled()
    await expect(fleetIII).toBeDisabled()

    await fleetI.uncheck()
    await expect(confirmButton).toBeDisabled()
    await expect(fleetIII).toBeEnabled()
    await fleetIII.check()
    await confirmButton.click()

    await expect(dialog).not.toBeVisible({ timeout: TIMEOUT })
    await expect(
      page.getByText("Storm at sea destroyed 2 fleets (II and III)."),
    ).toBeVisible({
      timeout: TIMEOUT,
    })
  })
})
