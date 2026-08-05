import { expect, Page, test } from "@playwright/test"

import { Player, loginAsBrowserUser } from "./helpers/auth"
import { deleteGame, setupGame } from "./helpers/game"

const TIMEOUT = 15000

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
    ;({ gameId, players } = await setupGame(
      playwright.request,
      "mortality__provinces",
    ))
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

  test("displays vacant and governed province details", async ({
    page,
    playwright,
  }) => {
    // Arrange — Cornelius (code 1) is seeded as Macedonia's governor
    ;({ gameId, players } = await setupGame(
      playwright.request,
      "mortality__provinces_with_governor",
    ))
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
    await expect(sicilia.getByText("Vacant")).toBeVisible({ timeout: TIMEOUT })
    await expect(sicilia.getByText("Governor:")).not.toBeVisible()

    const macedonia = provinceCard(page, "Macedonia")
    await expect(macedonia.getByText(/Governor:\s*Cornelius/)).toBeVisible({
      timeout: TIMEOUT,
    })
    await expect(macedonia.getByText("Term 3")).toBeVisible({ timeout: TIMEOUT })
    await expect(macedonia.getByText("Vacant")).not.toBeVisible()
  })

  test("hides provinces section when there are no provinces", async ({
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
    await expect(page.getByRole("heading", { name: "Provinces" })).not.toBeVisible(
      { timeout: TIMEOUT },
    )
  })

  test("governor election form renders unaligned senators under Unaligned optgroup", async ({
    page,
    playwright,
  }) => {
    // Arrange
    ;({ gameId, players } = await setupGame(
      playwright.request,
      "senate__governor_election_unaligned",
    ))
    await loginAsBrowserUser(
      playwright.request,
      page.context(),
      players[0].username,
    )
    await page.goto(`/games/${gameId}`)

    // Act
    const electButton = page
      .getByRole("button", { name: /Elect governor/i })
      .first()
    await expect(electButton).toBeVisible({ timeout: TIMEOUT })
    await electButton.click()

    const dialog = page.locator("dialog[open]")
    await expect(dialog).toBeVisible({ timeout: TIMEOUT })

    const provinceSelect = dialog.getByLabel("Province")
    await expect(provinceSelect).toBeVisible({ timeout: TIMEOUT })
    await provinceSelect.selectOption({ index: 1 })

    const governorSelect = dialog.getByLabel("Governor")
    await expect(governorSelect).toBeVisible({ timeout: TIMEOUT })

    // Assert
    const unalignedGroup = governorSelect.locator('optgroup[label="Unaligned"]')
    await expect(unalignedGroup).toBeAttached({ timeout: TIMEOUT })
    await expect(
      unalignedGroup.getByRole("option", {
        name: /Testonius/i,
      }),
    ).toBeAttached({ timeout: TIMEOUT })

    const factionGroups = governorSelect.locator(
      "optgroup:not([label='Unaligned'])",
    )
    await expect(factionGroups.first()).toBeAttached({ timeout: TIMEOUT })
  })

  test("governor election propose submits the motion", async ({
    page,
    playwright,
  }) => {
    // Arrange
    ;({ gameId, players } = await setupGame(
      playwright.request,
      "senate__governor_election",
    ))
    await loginAsBrowserUser(
      playwright.request,
      page.context(),
      players[0].username,
    )
    await page.goto(`/games/${gameId}`)

    // Act
    const electButton = page
      .getByRole("button", { name: /Elect governor/i })
      .first()
    await expect(electButton).toBeVisible({ timeout: TIMEOUT })
    await electButton.click()

    const dialog = page.locator("dialog[open]")
    await expect(dialog).toBeVisible({ timeout: TIMEOUT })

    const provinceSelect = dialog.getByLabel("Province")
    await provinceSelect.selectOption({ index: 1 })

    const governorSelect = dialog.getByLabel("Governor")
    await expect(governorSelect).toBeVisible({ timeout: TIMEOUT })
    const optionCount = await governorSelect.locator("option").count()
    expect(optionCount).toBeGreaterThan(1)
    await governorSelect.selectOption({ index: 1 })
    const selectedGovernorText = (
      await governorSelect.locator("option:checked").textContent()
    )?.trim()
    expect(selectedGovernorText).toBeTruthy()

    await dialog.getByRole("button", { name: "Confirm" }).click()
    await expect(dialog).not.toBeVisible({ timeout: TIMEOUT })

    // Assert — motion is open for voting (assignment covered by unit tests)
    await expect(
      page.getByRole("button", { name: /Current proposal.*Elect governor of Sicilia:/i }),
    ).toBeVisible({
      timeout: TIMEOUT,
    })
  })

  test("unaligned governor is shown on province and not in Forum list", async ({
    page,
    playwright,
  }) => {
    // Arrange — Testonius already assigned as Sicilia governor (left Rome)
    ;({ gameId, players } = await setupGame(
      playwright.request,
      "mortality__unaligned_governor",
    ))
    await loginAsBrowserUser(
      playwright.request,
      page.context(),
      players[0].username,
    )
    await page.goto(`/games/${gameId}`)

    // Assert
    const sicilia = provinceCard(page, "Sicilia")
    await expect(sicilia.getByText("Governor: Testonius")).toBeVisible({
      timeout: TIMEOUT,
    })
    await expect(sicilia.getByText("Term 3")).toBeVisible({ timeout: TIMEOUT })

    // Unaligned Forum list is only Rome-resident unaligned senators (1.09.53).
    // Scope to the section element itself — not page ancestors that also contain
    // the province card / action forms.
    const unalignedSection = page
      .locator("div.flex.flex-col.gap-2.px-10.py-6")
      .filter({
        has: page.getByRole("heading", {
          name: "Unaligned senators",
          exact: true,
        }),
      })
    if ((await unalignedSection.count()) > 0) {
      await expect(
        unalignedSection.getByText("Testonius", { exact: false }),
      ).toHaveCount(0)
    }
  })
})
