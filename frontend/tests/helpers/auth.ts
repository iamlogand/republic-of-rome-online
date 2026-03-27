import {
  APIRequest,
  APIRequestContext,
  Browser,
  BrowserContext,
  Page,
  expect,
} from "@playwright/test"

import { BACKEND, TEST_PASSWORD } from "./api"

export interface Player {
  username: string
  api: APIRequestContext
}

export async function loginAsBrowserUser(
  request: APIRequest,
  browserContext: BrowserContext,
  username: string,
): Promise<void> {
  const ctx = await request.newContext()
  const loginResp = await ctx.post(`${BACKEND}/api/test/login/`, {
    data: { username, password: TEST_PASSWORD },
  })
  expect(loginResp.ok()).toBeTruthy()
  const { csrf_token } = await loginResp.json()
  const sessionId = (await ctx.storageState()).cookies.find(
    (c) => c.name === "sessionid",
  )?.value
  await ctx.dispose()

  await browserContext.addCookies([
    {
      name: "sessionid",
      value: sessionId ?? "",
      domain: "127.0.0.1",
      path: "/",
      httpOnly: true,
      secure: false,
      sameSite: "Lax",
    },
    {
      name: "csrftoken",
      value: csrf_token,
      domain: "127.0.0.1",
      path: "/",
      httpOnly: false,
      secure: false,
      sameSite: "Lax",
    },
  ])
}

/**
 * Log in `count` players. Player 1 uses the provided `page`; players 2..N get
 * new browser contexts. Returns the extra pages (indices 1..count-1) — player
 * 1's page is not included.
 */
export async function loginPlayers(
  request: APIRequest,
  browser: Browser,
  page: Page,
  players: Player[],
  count = 1,
): Promise<Page[]> {
  await loginAsBrowserUser(request, page.context(), players[0].username)
  const extraPages: Page[] = []
  for (let i = 1; i < count; i++) {
    const ctx = await browser.newContext()
    await loginAsBrowserUser(request, ctx, players[i].username)
    extraPages.push(await ctx.newPage())
  }
  return extraPages
}
