import { useAuthContext } from "@/contexts/AuthContext";
import { useModalContext } from "@/contexts/ModalContext";
import { ReactNode, useEffect } from "react";

interface PageWrapperProps {
  children: ReactNode;
  pageStatus: number | null;
  setPageStatus: Function;
  ref: any
}

// Wraps the top bar, page content and footer
const PageWrapper = (props: PageWrapperProps) => {
  const { username } = useAuthContext();
  const { setModal } = useModalContext();

  // Ensure that the sign in modal appears immediately after a 401 with a forced sign out
  // This gives the user an opportunity to sign in and continue at that address
  useEffect(() => {
    if (props.pageStatus == 401 && username == '') {
      setModal("sign-in-required");
      props.setPageStatus(null)
    }
  }, [props, username, setModal])

  return <div ref={props.ref} className='non-modal-content'>{props.children}</div>;
}

export default PageWrapper;
