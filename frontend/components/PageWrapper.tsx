import { ReactNode, useEffect } from "react";
import Cookies from 'js-cookie';

interface PageWrapperProps {
  children: ReactNode;
  reference: any
}

// Wraps the top bar, page content and footer
const PageWrapper = (props: PageWrapperProps) => {

  useEffect(() => {
    if (!Cookies.get('timezone')) {
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      Cookies.set('timezone', timezone);
    }
  }, [])

  return <div ref={props.reference} className='non-modal-content'>{props.children}</div>;
}

export default PageWrapper;
