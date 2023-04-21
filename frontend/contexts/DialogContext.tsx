import { ReactNode, createContext, useContext, useState } from 'react';

interface DialogContextType {
  dialog: string;
  setDialog: (value: string) => void;
}

const DialogContext = createContext<DialogContextType | undefined>(undefined);

export const useDialogContext = (): DialogContextType => {
    const context = useContext(DialogContext);
  if (!context) {
    throw new Error("useDialogContext must be used within a DialogProvider");
  }
  return context;
};

interface DialogProviderProps {
  children: ReactNode
}

export const DialogProvider = ( props: DialogProviderProps ) => {

  const [dialog, setDialog] = useState<string>('');

  return (
    <DialogContext.Provider value={{ dialog, setDialog }}>
      {props.children}
    </DialogContext.Provider>
  );
};