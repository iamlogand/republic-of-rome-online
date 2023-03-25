import axios from "axios";

/**
 * Makes a request to the backend API using JWT authentication tokens.
 * @param {string} method HTTP method
 * @param {string} path the URL path
 * @param {string} accessToken the access token
 * @param {string} refreshToken the refresh token
 * @param {Function} setAccessToken the function used to set the access token
 * @param {Function} setRefreshToken the function used to set the refresh token
 * @param {Function} setUsername the function used to set the username
 * @returns the response
 */
export default async function request(
  method: string,
  path: string,
  accessToken: string,
  refreshToken: string,
  setAccessToken: Function,
  setRefreshToken: Function,
  setUsername: Function,
  data: object | null = null
) {
  const baseUrl = process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/';
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
    return response;
  } catch (error: any) {
    // If the error is not due to an authentication issue, return the response
    if (error.response && error.response.status !== 401 && error.response.status !== 403) {
      return error.response;
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
  } catch (error) {

    // If the request for a new access token fails, sign the user out
    setAccessToken('');
    setRefreshToken('');
    setUsername('');
    return;
  }

  // If the request for a new access token succeeds, save it
  setAccessToken(refreshResponse.data.access);

  // Retry the original request using the new access token
  try {
    response = await axios({
      method: method,
      url: requestUrl,
      headers: { "Authorization": "Bearer " + accessToken },
      data: data
    });
    return response;
  } catch (error: any) {
    // If the error is not due to an authentication issue, return the response
    if (error.response && error.response.status !== 401 && error.response.status !== 403) {
      return error.response;
    }
  }
}
