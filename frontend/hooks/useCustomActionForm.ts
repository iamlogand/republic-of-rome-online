import { useEffect, useRef, useState } from "react"

import AvailableAction from "@/classes/AvailableAction"
import PublicGameState from "@/classes/PublicGameState"
import getCSRFToken from "@/helpers/csrf"

interface Options {
  availableAction: AvailableAction
  publicGameState: PublicGameState
  isExpanded?: boolean
  setIsExpanded?: (expanded: boolean) => void
  onSubmitSuccess?: () => void
}

const useCustomActionForm = ({
  availableAction,
  publicGameState,
  isExpanded,
  setIsExpanded,
  onSubmitSuccess,
}: Options) => {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [feedback, setFeedback] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)

  const openDialog = () => {
    dialogRef.current?.showModal()
    setIsExpanded?.(true)
  }

  const closeDialog = () => {
    dialogRef.current?.close()
    setIsExpanded?.(false)
  }

  const handleDialogClose = () => {
    setFeedback("")
    setIsExpanded?.(false)
  }

  useEffect(() => {
    if (isExpanded) {
      dialogRef.current?.showModal()
    }
  }, [isExpanded])

  const submit = async (payload: object): Promise<boolean> => {
    if (!publicGameState.game) return false
    setLoading(true)
    const csrfToken = getCSRFToken()
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${publicGameState.game.id}/submit-action/${availableAction.id}`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
      },
    )
    setLoading(false)
    if (response.ok) {
      closeDialog()
      requestAnimationFrame(() => onSubmitSuccess?.())
      return true
    } else {
      const result = await response.json()
      if (result.message) {
        setFeedback(result.message)
      }
      return false
    }
  }

  return { dialogRef, feedback, loading, openDialog, closeDialog, handleDialogClose, submit }
}

export default useCustomActionForm
