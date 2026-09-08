import { expect, test } from "@playwright/test"

import { Player, loginPlayers } from "./helpers/auth"
import { deleteGame, setupGame } from "./helpers/game"

const TIMEOUT = 15000

test.describe("private persuasion calculator", () => {
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
    } catch (error) {
      console.warn("Game cleanup threw an error:", error)
    }

    await Promise.all(players.map((player) => player.api.dispose()))
  })

  test("calculates an aligned target and keeps planning private", async ({
    browser,
    page,
    playwright,
  }) => {
    const [secondPage] = await loginPlayers(
      playwright.request,
      browser,
      page,
      players,
      2,
    )

    await Promise.all([
      page.goto(`/games/${gameId}`),
      secondPage.goto(`/games/${gameId}`),
    ])

    const calculatorButton = page.getByRole("button", {
      name: "Persuasion Calculator",
      exact: true,
    })
    await expect(calculatorButton).toBeVisible({ timeout: TIMEOUT })
    await calculatorButton.click()

    const calculator = page.getByRole("region", {
      name: "Persuasion Calculator",
    })
    await expect(calculator).toBeVisible()
    await expect(
      calculator.getByText(/snapshot was taken when the calculator opened/i),
    ).toBeVisible()
    await expect(
      calculator.getByText(/Statesman loyalty modifiers.*not included/),
    ).toBeVisible()

    await expect(
      calculator.getByRole("checkbox", { name: "Seduction" }),
    ).toBeVisible()
    await expect(
      calculator.getByRole("checkbox", { name: "Blackmail" }),
    ).toBeVisible()
    await expect(
      calculator.getByText(/Card availability is not checked/),
    ).toBeVisible()
    await expect(calculator.getByText("Evil Omens")).toBeVisible()
    await expect(calculator.getByText("Era Ends")).toBeVisible()

    await calculator
      .getByRole("combobox", { name: "Persuader", exact: true })
      .selectOption({ label: "Cornelius (ORA 3, INF 10, 10T)" })
    await calculator
      .getByLabel("Target")
      .selectOption({ label: "Claudius (LOY 7, 0T)" })

    await expect(calculator.getByText("0%", { exact: true })).toBeVisible()
    await expect(calculator.getByText(/Base number/)).toHaveCount(0)
    await expect(calculator.getByText(/Roll .* or less/)).toHaveCount(0)

    await calculator.getByLabel("Persuader bribe").fill("3")
    await expect(calculator.getByText("3%", { exact: true })).toBeVisible()

    const counterBribes = calculator
      .getByRole("group", { name: "Counter-bribes" })
      .getByRole("spinbutton")
    await expect(counterBribes).toHaveCount(2)
    await counterBribes.first().fill("1")
    await expect(calculator.getByText("0%", { exact: true })).toBeVisible()

    const seduction = calculator.getByRole("checkbox", { name: "Seduction" })
    const blackmail = calculator.getByRole("checkbox", { name: "Blackmail" })
    await seduction.check()
    await expect(counterBribes.first()).toBeDisabled()
    await expect(calculator.getByText("3%", { exact: true })).toBeVisible()
    await blackmail.check()
    await expect(blackmail).toBeChecked()
    await expect(seduction).not.toBeChecked()
    await blackmail.uncheck()

    await calculator
      .getByRole("button", { name: "Add persuasion calculation" })
      .click()
    await expect(
      calculator.getByRole("tab", { name: "Calculation 2" }),
    ).toBeVisible()
    // The floating panel can cover the game bar. Dispatch the event directly
    // to verify that reopening focuses it without resetting local scenarios.
    await calculatorButton.dispatchEvent("click")
    await expect(
      calculator.getByRole("tab", { name: "Calculation 2" }),
    ).toBeVisible()

    // Keep the snapshot open while a real game action changes live state. The
    // draggable calculator may overlap the action bar in the test viewport.
    await page
      .getByRole("button", { name: "Attract knight...", exact: true })
      .dispatchEvent("click")
    const actionDialog = page.locator("dialog[open]")
    await actionDialog.getByLabel("Senator").selectOption({ index: 1 })
    await actionDialog.getByLabel("Talents").fill("5")
    await actionDialog.getByRole("button", { name: "Confirm" }).click()
    await expect(actionDialog).not.toBeVisible({ timeout: TIMEOUT })

    await calculator.getByRole("tab", { name: "Claudius" }).click()
    await expect(calculator.getByLabel("Persuader bribe")).toHaveValue("3")
    await expect(
      calculator
        .getByRole("combobox", { name: "Persuader", exact: true })
        .locator("option:checked"),
    ).toHaveText("Cornelius (ORA 3, INF 10, 10T)")

    await secondPage
      .getByRole("button", { name: "Persuasion Calculator", exact: true })
      .click()
    const secondCalculator = secondPage.getByRole("region", {
      name: "Persuasion Calculator",
    })
    await expect(
      secondCalculator.getByRole("tab", { name: "Calculation 1" }),
    ).toBeVisible()
    await expect(
      secondCalculator.getByRole("tab", { name: "Calculation 2" }),
    ).toHaveCount(0)
    await expect(
      secondCalculator.getByRole("combobox", {
        name: "Persuader",
        exact: true,
      }),
    ).toHaveValue("")
    await expect(secondCalculator.getByLabel("Target")).toHaveValue("")
    await expect(
      secondCalculator.getByRole("checkbox", { name: "Seduction" }),
    ).not.toBeChecked()
    await expect(
      secondCalculator.getByRole("checkbox", { name: "Blackmail" }),
    ).not.toBeChecked()

    await calculator.getByRole("button", { name: "Close", exact: true }).click()
    await expect(calculator).toHaveCount(0)
    await calculatorButton.click()
    const reopenedCalculator = page.getByRole("region", {
      name: "Persuasion Calculator",
    })
    await expect(
      reopenedCalculator.getByRole("tab", { name: "Calculation 1" }),
    ).toBeVisible()
    await expect(
      reopenedCalculator.getByRole("tab", { name: "Calculation 2" }),
    ).toHaveCount(0)
    await expect(
      reopenedCalculator.getByRole("combobox", {
        name: "Persuader",
        exact: true,
      }),
    ).toHaveValue("")
    await expect(reopenedCalculator.getByLabel("Target")).toHaveValue("")

    await secondPage.context().close()
  })
})
