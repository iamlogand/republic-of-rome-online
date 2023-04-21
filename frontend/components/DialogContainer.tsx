import DialogBackdrop from '@/components/DialogBackdrop';
import SignInDialog from '@/components/SignInDialog';
import SignOutDialog from '@/components/SignOutDialog';
import { useDialogContext } from '@/contexts/DialogContext';

function DialogContainer() {
  const { dialog, setDialog } = useDialogContext();

  const renderDialog = () => {
    switch (dialog) {
      case "sign-in":
        return <SignInDialog setDialog={setDialog} />
      case "sign-out":
        return <SignOutDialog setDialog={setDialog} />
    }
  }
  
  return (
    <>
      {dialog !== "" && <DialogBackdrop/>}
      {renderDialog()}
    </>
  );
}

export default DialogContainer;
