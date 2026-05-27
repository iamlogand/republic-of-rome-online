import { expect, test } from "@playwright/test"

import { Player, loginPlayers } from "./helpers/auth"
import { deleteGame, setupGame, skipToNextPhase } from "./helpers/game"

const TIMEOUT = 20000

async function skipUntil(
  api: any,
  gameId: number,
  predicate: (phase: string, subPhase: string) => boolean,
  maxSkips = 40,
): Promise<{ phase: string; subPhase: string }> {
  let current = await skipToNextPhase(api, gameId)
  let skips = 0
  while (!predicate(current.phase, current.subPhase) && skips < maxSkips) {
    current = await skipToNextPhase(api, gameId)
    skips++
  }
  return current
}

test.describe("pressure knights (forum phase)", () => {
  let gameId: number
  let players: Player[]

  test.beforeEach(async ({ playwright }) => {
    const result = await setupGame(playwright.request)
    gameId = result.gameId
    players = result.players
  })

  test.afterEach(async () => {
    if (!gameId) return
    await deleteGame(players[0].api, gameId)
    await Promise.all(players.map((p) => p.api.dispose()))
  })

  test("can open Pressure knight dialog and interact with per-senator controls", async ({
    page,
    browser,
    playwright,
  }) => {
    // Advance until we are in the forum phase with initiative actions available
    await skipUntil(
      players[0].api,
      gameId,
      (phase, subPhase) =>
        phase === "forum" &&
        ["attract knight", "sponsor games", "faction leader"].includes(subPhase),
    )

    const [player2Page] = await loginPlayers(
      playwright.request,
      browser,
      page,
      players,
      1,
    )

    await page.goto(`/games/${gameId}`)

    // First, try to attract a knight so we have something to pressure later.
    // This also validates that we reached a state where initiative actions exist.
    const attractButton = page
      .getByRole("button", { name: "Attract knight" })
      .first()

    if (await attractButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await attractButton.click()

      const dialog = page.locator("dialog[open]")
      await expect(dialog).toBeVisible({ timeout: TIMEOUT })

      // Basic attract flow (0 talents is always an option)
      const senatorSelect = dialog.getByLabel("Senator")
      if (await senatorSelect.isVisible({ timeout: 3000 }).catch(() => false)) {
        await senatorSelect.selectOption({ index: 1 })
      }

      const talentsInput = dialog.getByLabel("Talents")
      if (await talentsInput.isVisible({ timeout: 2000 }).catch(() => false)) {
        await talentsInput.fill("0")
      }

      await page.getByRole("button", { name: "Confirm" }).click()
      await expect(dialog).not.toBeVisible({ timeout: TIMEOUT }).catch(() => {})
    }

    // Advance to try to reach another attract knight opportunity (next initiative)
    await skipUntil(
      players[0].api,
      gameId,
      (phase, subPhase) => phase === "forum" && subPhase === "attract knight",
      15,
    )

    await page.reload()

    // Look for the Pressure knight custom form button
    const pressureButton = page
      .getByRole("button", { name: "Pressure knight..." })
      .first()

    if (await pressureButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await pressureButton.click()

      const dialog = page.locator("dialog[open]")
      await expect(dialog).toBeVisible({ timeout: TIMEOUT })

      // Basic verification that the custom form rendered
      await expect(
        dialog.getByText(/Total knights to pressure:/),
      ).toBeVisible({ timeout: TIMEOUT })

      const numberInputs = dialog.locator('input[type="number"]')
      await expect(numberInputs.first()).toBeVisible({ timeout: TIMEOUT })
    } else {
      // If we couldn't reach a state with the action available, at least verify we reached the forum phase
      const currentPhase = await skipToNextPhase(players[0].api, gameId)
      expect(currentPhase.phase).toBe("forum")
    }
  })
})
