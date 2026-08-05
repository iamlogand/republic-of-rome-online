import { expect, Page, test } from "@playwright/test"

import { Player, loginPlayers } from "./helpers/auth"
import { deleteGame, setupGame } from "./helpers/game"

const TIMEOUT = 20000

function provincesSection(page: Page) {
  return page
    .locator("div")
    .filter({ has: page.getByRole("heading", { name: "Provinces", exact: true }) })
}

function provinceCard(page: Page, name: string) {
  return provincesSection(page)
    .locator("div.rounded.border")
    .filter({
      has: page.getByRole("heading", { name, exact: true, level: 4 }),
    })
}

async function clickImmediateAction(page: Page, name: string | RegExp) {
  const button = page.getByRole("button", { name }).first()
  await expect(button).toBeVisible({ timeout: TIMEOUT })
  await button.click()
  await expect(button).toBeHidden({ timeout: TIMEOUT })
}

test.describe("governor election full cycle", () => {
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

  test("propose, vote yea from all factions, governor is assigned", async ({
    page,
    browser,
    playwright,
  }) => {
    ;({ gameId, players } = await setupGame(
      playwright.request,
      "senate__governor_election",
    ))
    const extraPages = await loginPlayers(
      playwright.request,
      browser,
      page,
      players,
      3,
    )
    const player2 = extraPages[0]
    const player3 = extraPages[1]

    await page.goto(`/games/${gameId}`)
    await player2.goto(`/games/${gameId}`)
    await player3.goto(`/games/${gameId}`)

    await expect(
      page.getByRole("button", { name: /Elect governor/i }).first(),
    ).toBeVisible({ timeout: TIMEOUT })

    await page.getByRole("button", { name: /Elect governor/i }).first().click()
    const dialog = page.locator("dialog[open]")
    await expect(dialog).toBeVisible({ timeout: TIMEOUT })
    await dialog.getByLabel("Province").selectOption({ index: 1 })
    await dialog.getByLabel("Governor").selectOption({ index: 1 })
    const selectedGovernor = (
      await dialog.getByLabel("Governor").locator("option:checked").textContent()
    )
      ?.trim()
      .replace(/\s*\(.*\)$/, "")
    expect(selectedGovernor).toBeTruthy()
    await dialog.getByRole("button", { name: "Confirm" }).click()
    await expect(dialog).not.toBeVisible({ timeout: TIMEOUT })

    await expect(
      page.getByRole("button", {
        name: /Current proposal.*Elect governor of Sicilia:/i,
      }),
    ).toBeVisible({ timeout: TIMEOUT })

    await clickImmediateAction(page, "Vote yea")

    await clickImmediateAction(page, /Call Faction 2 to vote/i)
    await clickImmediateAction(player2, "Vote yea")

    await clickImmediateAction(page, /Call Faction 3 to vote/i)
    await clickImmediateAction(player3, "Vote yea")

    const sicilia = provinceCard(page, "Sicilia")
    await expect(sicilia.getByText(/Governor:/)).toBeVisible({
      timeout: TIMEOUT,
    })
    await expect(sicilia.getByText("Term 3")).toBeVisible({ timeout: TIMEOUT })
    await expect(sicilia.getByText("Vacant")).not.toBeVisible()
    await expect(sicilia.getByText(`Governor: ${selectedGovernor}`)).toBeVisible()
  })
})
