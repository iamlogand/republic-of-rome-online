"use client"

import { ComponentType } from "react"

import AvailableAction from "@/classes/AvailableAction"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import { SetSelection } from "@/types/setSelection"

import GenericActionForm, { ActionSelection } from "./GenericActionForm"
import { customActionFormRegistry } from "./customActionForms/meta/registry"

export interface CustomActionFormProps {
  availableAction: AvailableAction
  publicGameState: PublicGameState
  privateGameState: PrivateGameState
  selection: ActionSelection
  setSelection: (newSelection: SetSelection) => void
  isExpanded?: boolean
  setIsExpanded?: (expanded: boolean) => void
  resetKey?: number
  onSubmitSuccess?: () => void
}

interface ActionFormDispatcherProps {
  availableAction: AvailableAction
  publicGameState: PublicGameState
  privateGameState: PrivateGameState
  selection: ActionSelection
  setSelection: (newSelection: SetSelection) => void
  isExpanded?: boolean
  setIsExpanded?: (expanded: boolean) => void
  resetKey?: number
  onSubmitSuccess?: () => void
}

const ActionDispatcher = ({
  availableAction,
  publicGameState,
  privateGameState,
  selection,
  setSelection,
  isExpanded,
  setIsExpanded,
  resetKey,
  onSubmitSuccess,
}: ActionFormDispatcherProps) => {
  const CustomActionForm: ComponentType<CustomActionFormProps> | undefined =
    customActionFormRegistry[availableAction.base_name]

  if (CustomActionForm) {
    return (
      <CustomActionForm
        availableAction={availableAction}
        publicGameState={publicGameState}
        privateGameState={privateGameState}
        selection={selection}
        setSelection={setSelection}
        isExpanded={isExpanded}
        setIsExpanded={setIsExpanded}
        resetKey={resetKey}
        onSubmitSuccess={onSubmitSuccess}
      />
    )
  }

  return (
    <GenericActionForm
      availableAction={availableAction}
      publicGameState={publicGameState}
      selection={selection}
      setSelection={setSelection}
      isExpanded={isExpanded}
      setIsExpanded={setIsExpanded}
      resetKey={resetKey}
      onSubmitSuccess={onSubmitSuccess}
    />
  )
}

export default ActionDispatcher
