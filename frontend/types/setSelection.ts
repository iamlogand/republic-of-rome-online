import { ActionSelection } from "@/components/GenericActionForm"

export type SetSelection =
  | ActionSelection
  | ((prev: ActionSelection | undefined) => ActionSelection)
