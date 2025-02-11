"use client"

import toast from "react-hot-toast"

import getCSRFToken from "@/utils/csrf"
import AvailableAction from "@/classes/AvailableActions"
import PublicGameState from "@/classes/PublicGameState"
import PrivateGameState from "@/classes/PrivateGameState"

interface ActionHandlerProps {
  availableAction: AvailableAction
  publicGameState: PublicGameState
  privateGameState: PrivateGameState
}

const ActionHandler = ({
  availableAction,
  publicGameState,
}: ActionHandlerProps) => {
  const handleSubmit = async (
    e: React.SyntheticEvent<HTMLFormElement>,
    selection: object
  ) => {
    e.preventDefault()
    if (!publicGameState.game) return null
    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${publicGameState.game.id}/submit-action/${availableAction.name}`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(selection),
      }
    )
    if (response.ok) {
      toast.success("Action submitted")
    } else {
      toast.error("Failed to submit action")
    }
  }

  return (
    <form onSubmit={(e) => handleSubmit(e, {})}>
      {availableAction.schema.length === 0 ? (
        <button
          type="submit"
          className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
        >
          {availableAction.name}
        </button>
      ) : (
        <span className="capitalize">
          {availableAction.name} (fields are not yet supported)
        </span>
      )}
    </form>
  )
}

export default ActionHandler
