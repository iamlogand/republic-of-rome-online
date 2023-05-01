
import { ReactNode } from "react";

interface PageWrapperProps {
  children: ReactNode;
  reference: any
}

// Wraps the top bar, page content and footer
const PageWrapper = (props: PageWrapperProps) => {
  return <div ref={props.reference} className='non-modal-content'>{props.children}</div>;
}

export default PageWrapper;
