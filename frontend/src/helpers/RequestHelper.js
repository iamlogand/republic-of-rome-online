import axios from "axios";

/**
 * Makes a request to the backend API using JWT authentication tokens.
 * @param {string} method HTTP method
 * @param {string} path the URL path
 * @param {string} accessToken the current JWT access token
 * @param {string} refreshToken the current JWT refresh token
 * @param {Function} setAuthData the function used to save a new access token
 * @returns the response
 */
export default async function request(method, path, accessToken, refreshToken, setAuthData) {
  const baseUrl = process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/';
  const requestUrl = baseUrl + path;
  let response;

  // Attempt the request using the current access token
  try {
    response = await axios({
      method: method,
      url: requestUrl,
      headers: { "Authorization": "Bearer " + accessToken }
    });
    return response;
  } catch (error) { }

  let refreshResponse;

  // If that fails, perhaps the access token has expired.
  // Request a new access token using the refresh token
  try {
    refreshResponse = await axios({
      method: 'post',
      url: baseUrl + 'token/refresh/',
      headers: { "Content-Type": "application/json" },
      data: JSON.stringify({ "refresh": refreshToken })
    });
  } catch (error) {

    // If the request for a new access token fails, sign the user out
    setAuthData({
      accessToken: '',
      refreshToken: '',
      username: ''
    });
    return;
  }

  // If the request for a new access token succeeds, save it
  accessToken = refreshResponse.data.access;
  setAuthData({accessToken: accessToken});

  // Retry the original request using the new access token
  try {
    response = await axios({
      method: method,
      url: requestUrl,
      headers: { "Authorization": "Bearer " + accessToken }
    });
    return response;
  } catch (error) { }
}
