import { expect, Page, test } from "@playwright/test"

import { Player, loginAsBrowserUser } from "./helpers/auth"
import { deleteGame, setupGame } from "./helpers/game"

const TIMEOUT = 15000

function provinceCard(page: Page, name: string) {
  return page
    .locator("div.rounded.border")
    .filter({ has: page.getByRole("heading", { name }) })
}

test.describe("provinces", () => {
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

  test("displays provinces with development and frontier badges", async ({
    page,
    playwright,
  }) => {
    // Arrange
    ;({ gameId, players } = await setupGame(playwright.request, "mortality__provinces"))
    await loginAsBrowserUser(
      playwright.request,
      page.context(),
      players[0].username,
    )

    // Act
    await page.goto(`/games/${gameId}`)

    // Assert
    await expect(page.getByRole("heading", { name: "Provinces" })).toBeVisible({
      timeout: TIMEOUT,
    })

    const sicilia = provinceCard(page, "Sicilia")
    await expect(sicilia.getByText("Undeveloped")).toBeVisible()
    await expect(sicilia.getByText("Frontier")).not.toBeVisible()

    const macedonia = provinceCard(page, "Macedonia")
    await expect(macedonia.getByText("Developed")).toBeVisible()
    await expect(macedonia.getByText("Frontier")).toBeVisible()
  })

  test("hides provinces section when there are no provinces", async ({
    page,
    playwright,
  }) => {
    // Arrange
    ;({ gameId, players } = await setupGame(
      playwright.request,
      "mortality",
    ))
    await loginAsBrowserUser(
      playwright.request,
      page.context(),
      players[0].username,
    )

    // Act
    await page.goto(`/games/${gameId}`)

    // Assert
    await expect(page.getByRole("heading", { name: "Provinces" })).not.toBeVisible(
      { timeout: TIMEOUT },
    )
  })
})
