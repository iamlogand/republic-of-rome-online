import { getCookie } from "cookies-next";
import { GetServerSidePropsContext } from "next";

interface getInitialCookieDataReturnType {
  accessToken: string;
  refreshToken: string;
  username: string;
}

const getInitialCookieData = (context: GetServerSidePropsContext): getInitialCookieDataReturnType => {
  const ssrAccessToken = getCookie('accessToken', { req: context.req, res: context.res });
  const ssrRefreshToken = getCookie('refreshToken', { req: context.req, res: context.res });
  const ssrUsername = getCookie('username', { req: context.req, res: context.res });

  return {
    accessToken: typeof ssrAccessToken === 'string' ? JSON.parse(ssrAccessToken) : "",
    refreshToken: typeof ssrRefreshToken === 'string' ? JSON.parse(ssrRefreshToken) : "",
    username: typeof ssrUsername === 'string' ? JSON.parse(ssrUsername) : ""
  };
};

export default getInitialCookieData;
