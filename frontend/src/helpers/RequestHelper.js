import axios from "axios";

export default async function request(method, path, accessToken, refreshToken, setAuthData) {
  const baseUrl = process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/';
  const requestUrl = baseUrl + path;
  let response;

  try {
    response = await axios({
      method: method,
      url: requestUrl,
      headers: { "Authorization": "Bearer " + accessToken }
    });
    return response;
  } catch (error) { }

  let refreshResponse;

  try {
    refreshResponse = await axios({
      method: 'post',
      url: baseUrl + 'token/refresh/',
      headers: { "Content-Type": "application/json" },
      data: JSON.stringify({ "refresh": refreshToken })
    });
  } catch (error) {
    setAuthData({
      accessToken: '',
      refreshToken: '',
      username: ''
    });
    return;
  }

  accessToken = refreshResponse.data.access;
  setAuthData({accessToken: accessToken});

  try {
    response = await axios({
      method: method,
      url: requestUrl,
      headers: { "Authorization": "Bearer " + accessToken }
    });
    return response;
  } catch (error) { }
}
