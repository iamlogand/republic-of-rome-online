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
    const cornelius = page
      .getByRole("heading", { name: "Cornelius", exact: true })
      .locator("..")
      .locator("..")
    await expect(cornelius).toBeVisible({ timeout: TIMEOUT })

    const shipBuilding = cornelius.getByText("Ship building", { exact: true })
    const harborFees = cornelius.getByText("Harbor fees", { exact: true })
    const corrupt = cornelius.getByText("(corrupt)", { exact: true })
    const capitalizedCorrupt = cornelius.getByText("(Corrupt)", { exact: true })
    await expect(shipBuilding).toBeVisible()
    await expect(harborFees).toBeVisible()
    await expect(corrupt).toHaveCount(1)
    await expect(capitalizedCorrupt).toHaveCount(0)

    await harborFees.hover()
    const harborFeesIncome = page.getByText("3T at revenue", { exact: true })
    await expect(harborFeesIncome).toBeVisible()

    const aegyptianGrain = page.getByText("Aegyptian grain", { exact: true })
    await expect(aegyptianGrain).toBeVisible()

    const armaments = page.getByText("Armaments", { exact: true })
    await expect(armaments).toBeVisible()
    await armaments.hover()
    const armamentsIncome = page.getByText("2T per new legion raised", {
      exact: true,
    })
    await expect(armamentsIncome).toBeVisible()

    const mining = page.getByText("Mining", { exact: true })
    await expect(mining).toBeVisible()

    const shipBuildingTitleCase = page.getByText("Ship Building", {
      exact: true,
    })
    const harborFeesTitleCase = page.getByText("Harbor Fees", { exact: true })
    await expect(shipBuildingTitleCase).toHaveCount(0)
    await expect(harborFeesTitleCase).toHaveCount(0)
  })
})
