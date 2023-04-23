import { getCookie } from "cookies-next";
import { GetServerSidePropsContext } from "next";

interface getInitialCookieDataReturnType {
  ssrAccessToken: string;
  ssrRefreshToken: string;
  ssrUsername: string;
}

const getInitialCookieData = (context: GetServerSidePropsContext): getInitialCookieDataReturnType => {
  const ssrAccessToken = getCookie('accessToken', { req: context.req, res: context.res });
  const ssrRefreshToken = getCookie('refreshToken', { req: context.req, res: context.res });
  const ssrUsername = getCookie('username', { req: context.req, res: context.res });

  return {
    ssrAccessToken: typeof ssrAccessToken === 'string' ? JSON.parse(ssrAccessToken) : "",
    ssrRefreshToken: typeof ssrRefreshToken === 'string' ? JSON.parse(ssrRefreshToken) : "",
    ssrUsername: typeof ssrUsername === 'string' ? JSON.parse(ssrUsername) : ""
  };
};

export default getInitialCookieData;
