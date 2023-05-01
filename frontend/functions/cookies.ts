import { getCookie } from "cookies-next";
import { GetServerSidePropsContext } from "next";

interface getInitialCookieDataReturnType {
  clientAccessToken: string;
  clientRefreshToken: string;
  clientUsername: string;
  clientTimezone: string;
}

const getInitialCookieData = (context: GetServerSidePropsContext): getInitialCookieDataReturnType => {
  const clientAccessToken = getCookie('accessToken', { req: context.req, res: context.res });
  const clientRefreshToken = getCookie('refreshToken', { req: context.req, res: context.res });
  const clientUsername = getCookie('username', { req: context.req, res: context.res });
  const clientTimezone = getCookie('timezone', { req: context.req, res: context.res });

  return {
    clientAccessToken: typeof clientAccessToken === 'string' ? clientAccessToken : "",
    clientRefreshToken: typeof clientRefreshToken === 'string' ? clientRefreshToken : "",
    clientUsername: typeof clientUsername === 'string' ? clientUsername : "",
    clientTimezone: typeof clientTimezone === 'string' ? clientTimezone : ""
  }
}

export default getInitialCookieData;
