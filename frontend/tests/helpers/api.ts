import { APIRequestContext, expect } from "@playwright/test"

export const BACKEND = "http://127.0.0.1:8000"
export const TEST_PASSWORD = "password123"

export async function ensureUser(
  context: APIRequestContext,
  username: string,
): Promise<void> {
  const response = await context.post(`${BACKEND}/api/test/login/`, {
    data: { username, password: TEST_PASSWORD },
  })
  expect(response.ok()).toBeTruthy()
}
