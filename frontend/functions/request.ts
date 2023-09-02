import axios from "axios";

export interface ResponseType {
  data: any;  // This is a valid use of `any` because Axios source code also uses `any` for response data
  status: number | null;  // See https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
}

/**
 * Use this function to make HTTP requests to the API. It takes care of refreshing the access token,
 * retrying with the new access token, and signing the user out if their refresh token is invalid.
 * 
 * @param {string} method HTTP method
 * @param {string} path the URL path
 * @param {string} accessToken access token
 * @param {string} refreshToken refresh token
 * @param {Function} setAccessToken used to sign the user out if refresh token is invalid
 * @param {Function} setRefreshToken used to sign the user out if refresh token is invalid
 * @param {Function} setUsername used to sign the user out if refresh token is invalid
 * @param {object | null} data to send in the response
 * 
 * @returns a ResponseType object containing only the response data and response code
 */
export default async function request(
  method: string,
  path: string,
  accessToken: string,
  refreshToken: string,
  setAccessToken?: Function,
  setRefreshToken?: Function,
  setUsername?: Function,
  data?: object
): Promise<ResponseType> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  const requestUrl = baseUrl + path;
  let response;

  // Attempt the request using the current access token
  try {
    response = await axios({
      method: method,
      url: requestUrl,
      headers: { "Authorization": "Bearer " + accessToken },
      data: data
    });
    return {data: response.data, status: response.status};
  } catch (error: any) {
    if (error.message === 'Network Error' && error.response == null) {
      console.log("Network error")
      // The server could not be reached
      if (setAccessToken) setAccessToken('');
      if (setRefreshToken) setRefreshToken('');
      if (setUsername) setUsername('');
      return {data: null, status: null}
    }
    if (error?.response?.status !== 401) {
      // The error is not due to "401 Unauthorized" so no point in trying to refresh the access token
      console.error(`Response ${error.response.status}: ${error.response.data.message}`)
      return {data: error.response.data, status: error.response.status};
    }
  }

  let refreshResponse;

  // If the first attempt fails, then perhaps the access token has expired.
  // Request a new access token using the refresh token
  try {
    refreshResponse = await axios({
      method: 'post',
      url: baseUrl + 'tokens/refresh/',
      headers: { "Content-Type": "application/json" },
      data: JSON.stringify({ "refresh": refreshToken })
    });
  } catch (error: any) {
    // If the request for a new access token fails, sign the user out
    if (setAccessToken) setAccessToken('');
    if (setRefreshToken) setRefreshToken('');
    if (setUsername) setUsername('');
    return {data: error.response?.data, status: 401};  // 401 is the status of the original response
  }

  // If the request for a new access token succeeds, save it
  if (setAccessToken) setAccessToken(refreshResponse.data.access);

  // Retry the original request using the new access token
  try {
    response = await axios({
      method: method,
      url: requestUrl,
      headers: { "Authorization": "Bearer " + refreshResponse.data.access },
      data: data
    });
    return {data: response.data, status: response.status};
  } catch (error: any) {
    console.error(`Response ${error.response.status}: ${error.response.data.message}`)
    return {data: error.response?.data, status: error.response?.status};
  }
}

/**
 * Use this function to make HTTP requests to the API
 * if authentication is not required.
 * 
 * @param {string} method HTTP method
 * @param {string} path the URL path
 * @param {object | null} data to send in the response
 * @returns a ResponseType object containing only the response data and response code
 */

export async function requestWithoutAuthentication(
  method: string,
  path: string,
  data?: object
): Promise<ResponseType> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  const requestUrl = baseUrl + path;
  let response;

  // Attempt the request
  try {
    response = await axios({
      method: method,
      url: requestUrl,
      data: data
    });
    return {data: response.data, status: response.status};
  } catch (error: any) {
    return {data: error.response?.data, status: error.response?.status}
  }
}