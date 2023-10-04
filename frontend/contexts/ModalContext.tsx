import { ReactNode, createContext, useContext, useState } from "react"

interface ModalContextType {
  modal: string
  setModal: (value: string) => void
}

const ModalContext = createContext<ModalContextType | null>(null)

export const useModalContext = (): ModalContextType => {
  const context = useContext(ModalContext)
  if (!context) {
    throw new Error("useModalContext must be used within a ModalProvider")
  }
  return context
}

interface ModalProviderProps {
  children: ReactNode
}

export const ModalProvider = (props: ModalProviderProps) => {
  const [modal, setModal] = useState<string>("")

  return (
    <ModalContext.Provider value={{ modal, setModal }}>
      {props.children}
    </ModalContext.Provider>
  )
}
