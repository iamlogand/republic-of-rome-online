import axios from "axios"
import User from "@/classes/User"

/**
 * Use this function when you just want to refresh the user's access token,
 * or sign the user out if their refresh token is invalid.
 *
 * @param {string} refreshToken refresh token
 * @param {(accessToken: string) => void} setAccessToken used to update the access token, or sign the user out if refresh token is invalid
 * @param {(refreshToken: string) => void} setRefreshToken used to sign the user out if the refresh token is invalid
 * @param {(user: User | null) => void} setUser used to sign the user out if refresh token is invalid
 *
 * @returns the new access token, or null if the refresh token is invalid
 */
export default async function refreshAccessToken(
  refreshToken: string,
  setAccessToken?: (accessToken: string) => void,
  setRefreshToken?: (refreshToken: string) => void,
  setUser?: (user: User | null) => void
): Promise<string | null> {
  let refreshResponse
  try {
    // Request a new access token using the refresh token
    refreshResponse = await axios({
      method: "post",
      url: process.env.NEXT_PUBLIC_API_URL + "tokens/refresh/",
      headers: { "Content-Type": "application/json" },
      data: JSON.stringify({ refresh: refreshToken }),
    })
    if (setAccessToken && refreshResponse)
      setAccessToken(refreshResponse.data.access)

    return refreshResponse.data.access
  } catch (error: any) {
    // If the request for a new access token fails, sign the user out
    if (setAccessToken) setAccessToken("")
    if (setRefreshToken) setRefreshToken("")
    if (setUser) setUser(null)
    return null
  }
}
