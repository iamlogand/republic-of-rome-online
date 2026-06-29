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

type UpdateSelection = (
  id: string,
  newSelection:
    | ActionSelection
    | ((prev: ActionSelection | undefined) => ActionSelection),
) => void

interface Props {
  privateGameState: PrivateGameState
  publicGameState: PublicGameState
  selectionMap: Record<string, ActionSelection>
  updateSelection: UpdateSelection
  expandedActionId: string | null
  setExpandedActionId: (id: string | null) => void
  actionResetKey: number
  onSubmitSuccess: (id: string) => void
}

const ActionBar = ({
  privateGameState,
  publicGameState,
  selectionMap,
  updateSelection,
  expandedActionId,
  setExpandedActionId,
  actionResetKey,
  onSubmitSuccess,
}: Props) => (
  <div className="flex shrink-0 flex-col gap-4 border-t border-neutral-300 px-10 py-6">
    <div className="flex flex-wrap gap-x-4 gap-y-2">
      {privateGameState.availableActions.length > 0 ? (
        privateGameState.availableActions
          .sort((a, b) => a.position - b.position)
          .map((availableAction: AvailableAction) => {
            const id = availableAction.identifier
            const CustomForm: ComponentType<CustomActionFormProps> | undefined =
              customActionFormRegistry[availableAction.base_name]
            const sharedProps = {
              availableAction,
              publicGameState,
              privateGameState,
              selection: selectionMap[id] ?? {},
              setSelection: (newSelection: SetSelection) =>
                updateSelection(id, newSelection),
              isExpanded: expandedActionId === id,
              setIsExpanded: (expanded: boolean) =>
                setExpandedActionId(expanded ? id : null),
              resetKey: actionResetKey,
              onSubmitSuccess: () => onSubmitSuccess(id),
            }
            return CustomForm ? (
              <CustomForm key={id} {...sharedProps} />
            ) : (
              <GenericActionForm key={id} {...sharedProps} />
            )
          })
      ) : (
        <p className="text-neutral-600">None right now</p>
      )}
    </div>
  </div>
)

export default ActionBar
