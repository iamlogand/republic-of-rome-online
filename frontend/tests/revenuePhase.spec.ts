import { expect, test } from "@playwright/test"

import { Player, loginPlayers } from "./helpers/auth"
import { deleteGame, setupGame, skipToNextPhase } from "./helpers/game"

const WHOLE_NUMBER_REGEX = /^\d+$/
const TIMEOUT = 10000

test.describe("revenue phase tests", () => {
  let gameId: number
  let players: Player[]

  test.beforeEach(async ({ playwright }) => {
    const result = await setupGame(playwright.request)
    gameId = result.gameId
    players = result.players

    const { phase, subPhase } = await skipToNextPhase(players[0].api, gameId)
    expect(phase).toBe("revenue")
    expect(subPhase).toBe("redistribution")
  })

  test.afterEach(async () => {
    if (!gameId) return
    await deleteGame(players[0].api, gameId)
    await Promise.all(players.map((p) => p.api.dispose()))
  })

  test("redistribute defaults reflect post-contribution amounts", async ({
    page,
    browser,
    playwright,
  }) => {
    await loginPlayers(playwright.request, browser, page, players)
    await page.goto(`/games/${gameId}`)

    const contributeButton = page
      .getByRole("button", { name: "Contribute" })
      .first()
    await expect(contributeButton).toBeVisible({ timeout: TIMEOUT })
    await contributeButton.click()

    const dialog = page.locator("dialog[open]")
    const contributorSelect = dialog.getByLabel("Contributor")
    await expect(contributorSelect).toBeVisible()
    await expect(
      contributorSelect.locator("option[value]").first(),
    ).toBeAttached()

    await contributorSelect.selectOption({ index: 1 })
    const senatorName = (
      await contributorSelect.locator("option").nth(1).textContent()
    )?.trim()

    const talentsInput = dialog.getByLabel("Talents")
    await expect(talentsInput).toBeVisible()
    await expect(talentsInput).toHaveAttribute("max", WHOLE_NUMBER_REGEX)

    const maxTalents = Number(await talentsInput.getAttribute("max"))
    expect(maxTalents).toBeGreaterThan(0)
    await talentsInput.fill(String(maxTalents))

    await page.getByRole("button", { name: "Confirm" }).click()
    await expect(page.locator("dialog[open]")).not.toBeVisible({
      timeout: TIMEOUT,
    })

    const redistributeButton = page
      .getByRole("button", { name: "Redistribute talents" })
      .first()
    await expect(redistributeButton).toBeVisible()
    await redistributeButton.click()

    const allocationInput = page
      .locator("dialog[open]")
      .getByLabel(senatorName ?? "")

    await expect(allocationInput).toHaveValue("0", { timeout: TIMEOUT })
  })

  test("another player's action does not clear the dialog selection", async ({
    page,
    browser,
    playwright,
  }) => {
    const [player2] = await loginPlayers(
      playwright.request,
      browser,
      page,
      players,
      2,
    )
    await page.goto(`/games/${gameId}`)

    const contributeButton = page
      .getByRole("button", { name: "Contribute" })
      .first()
    await expect(contributeButton).toBeVisible({ timeout: TIMEOUT })
    await contributeButton.click()

    const dialog = page.locator("dialog[open]")
    const contributorSelect = dialog.getByLabel("Contributor")
    await expect(
      contributorSelect.locator("option[value]").first(),
    ).toBeAttached()
    const [selectedValue] = await contributorSelect.selectOption({ index: 1 })

    await player2.goto(`/games/${gameId}`)
    const player2ContributeButton = player2
      .getByRole("button", { name: "Contribute" })
      .first()
    await expect(player2ContributeButton).toBeVisible({ timeout: TIMEOUT })
    await player2ContributeButton.click()

    const player2Dialog = player2.locator("dialog[open]")
    const player2ContributorSelect = player2Dialog.getByLabel("Contributor")
    await expect(
      player2ContributorSelect.locator("option[value]").first(),
    ).toBeAttached()
    await player2ContributorSelect.selectOption({ index: 1 })

    const player2TalentsInput = player2Dialog.getByLabel("Talents")
    await expect(player2TalentsInput).toHaveAttribute("max", WHOLE_NUMBER_REGEX)
    await player2TalentsInput.fill("1")
    await player2.getByRole("button", { name: "Confirm" }).click()
    await expect(player2Dialog).not.toBeVisible({ timeout: TIMEOUT })
    await player2.context().close()

    await expect(contributorSelect).toHaveValue(selectedValue, {
      timeout: TIMEOUT,
    })

    const talentsInput = dialog.getByLabel("Talents")
    await expect(talentsInput).toHaveAttribute("max", WHOLE_NUMBER_REGEX)
    await talentsInput.fill(
      String(Number(await talentsInput.getAttribute("max"))),
    )
    await page.getByRole("button", { name: "Confirm" }).click()
    await expect(dialog).not.toBeVisible({ timeout: TIMEOUT })
  })

  test("in-progress redistribute allocations are preserved when another player transfers", async ({
    page,
    browser,
    playwright,
  }) => {
    const [player2] = await loginPlayers(
      playwright.request,
      browser,
      page,
      players,
      2,
    )
    await page.goto(`/games/${gameId}`)
    await player2.goto(`/games/${gameId}`)

    const p2RedistributeButton = player2
      .getByRole("button", { name: "Redistribute talents" })
      .first()
    await expect(p2RedistributeButton).toBeVisible({ timeout: TIMEOUT })
    await p2RedistributeButton.click()

    const p2Dialog = player2.locator("dialog[open]")
    const firstSenatorLabel = p2Dialog
      .locator('label[for^="allocation-"]')
      .first()
    await expect(firstSenatorLabel).toBeVisible()
    const firstSenatorName =
      (await firstSenatorLabel.textContent())?.trim() ?? ""
    const firstSenatorInput = p2Dialog.getByLabel(firstSenatorName)
    const initialValue = Number(await firstSenatorInput.inputValue())

    const firstSenatorMinusButton = firstSenatorInput.locator(
      "xpath=preceding-sibling::button[1]",
    )
    await firstSenatorMinusButton.click()
    await expect(firstSenatorInput).toHaveValue(String(initialValue - 1))

    const totalDisplay = p2Dialog.locator("div").filter({ hasText: /^Total:/ })
    const initialTotalText = await totalDisplay.textContent()
    const initialTotal = Number(
      initialTotalText?.match(/\/ (\d+) talents/)?.[1],
    )

    const transferButton = page
      .getByRole("button", { name: "Transfer talents" })
      .first()
    await expect(transferButton).toBeVisible({ timeout: TIMEOUT })
    await transferButton.click()

    const dialog = page.locator("dialog[open]")
    const senderSelect = dialog.getByLabel("Sender")
    await expect(senderSelect.locator("option[value]").first()).toBeAttached()
    await senderSelect.selectOption({ index: 1 })

    const recipientSelect = dialog.getByLabel("Recipient")
    await expect(
      recipientSelect.locator("option[value]").first(),
    ).toBeAttached()
    await recipientSelect.selectOption({ label: firstSenatorName })

    const talentsInput = dialog.getByLabel("Talents")
    await expect(talentsInput).toHaveAttribute("max", WHOLE_NUMBER_REGEX)
    await talentsInput.fill("1")
    await page.getByRole("button", { name: "Confirm" }).click()
    await expect(dialog).not.toBeVisible({ timeout: TIMEOUT })

    await expect(firstSenatorInput).toHaveValue(String(initialValue - 1), {
      timeout: TIMEOUT,
    })

    await expect(totalDisplay).toHaveText(
      new RegExp(`/ ${initialTotal + 1} talents`),
      { timeout: TIMEOUT },
    )

    await player2.context().close()
  })

  test("redistribute selection persists after dialog is closed and reopened", async ({
    page,
    browser,
    playwright,
  }) => {
    await loginPlayers(playwright.request, browser, page, players)
    await page.goto(`/games/${gameId}`)

    const redistributeButton = page
      .getByRole("button", { name: "Redistribute talents" })
      .first()
    await expect(redistributeButton).toBeVisible({ timeout: TIMEOUT })
    await redistributeButton.click()

    const dialog = page.locator("dialog[open]")
    await expect(dialog.getByRole("button", { name: "Clear" })).toBeVisible()
    await dialog.getByRole("button", { name: "Clear" }).click()

    const firstLabel = dialog.locator('label[for^="allocation-"]').first()
    await expect(firstLabel).toBeVisible()
    const firstSenatorName = (await firstLabel.textContent())?.trim() ?? ""
    await expect(dialog.getByLabel(firstSenatorName)).toHaveValue("0")

    await dialog.getByRole("button", { name: "Cancel" }).click()
    await expect(dialog).not.toBeVisible()

    await redistributeButton.click()
    await expect(page.locator("dialog[open]").getByLabel(firstSenatorName)).toHaveValue(
      "0",
      { timeout: TIMEOUT },
    )
  })
})
