import { useCallback, useEffect, useRef, useState } from "react"
import toast from "react-hot-toast"

import getCSRFToken from "@/utils/csrf"
import AvailableAction, {
  ActionCondition,
  ActionField,
  ActionSignals,
} from "@/classes/AvailableAction"
import PublicGameState from "@/classes/PublicGameState"
import PrivateGameState from "@/classes/PrivateGameState"
import ActionDescription from "./ActionDescription"

type Selection = {
  [key: string]: string | number
}

interface ActionHandlerProps {
  availableAction: AvailableAction
  publicGameState: PublicGameState
  privateGameState: PrivateGameState
}

const ActionHandler = ({
  availableAction,
  publicGameState,
}: ActionHandlerProps) => {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [selection, setSelection] = useState<Selection>({})
  const [signals, setSignals] = useState<ActionSignals>({})

  const resolveSignal = useCallback(
    (value: string | number | undefined) => {
      const signalPrefix = "signal:"
      if (typeof value === "string" && value.startsWith(signalPrefix)) {
        const signalKey = value.slice(signalPrefix.length)
        return signals[signalKey]
      } else {
        return value
      }
    },
    [signals]
  )

  const resolveLimit = (
    limits: (number | string)[] | undefined,
    type: "min" | "max"
  ): number | undefined => {
    let selectedLimit = undefined
    if (limits) {
      for (const limit of limits) {
        const resolvedLimit = resolveSignal(limit)
        if (
          typeof resolvedLimit === "number" &&
          (selectedLimit === undefined ||
            (type == "min" && resolvedLimit > selectedLimit) ||
            (type == "max" && resolvedLimit < selectedLimit))
        ) {
          selectedLimit = resolvedLimit
        }
      }
    }
    return selectedLimit
  }

  const setInitialValues = useCallback(
    (reset: boolean = false) => {
      setSelection((previous: Selection) => {
        const newSelection: Selection = reset ? { ...previous } : previous
        availableAction.schema.forEach((field: ActionField) => {
          if (field.type === "number") {
            if (!previous[field.name] || reset) {
              const newValue = resolveLimit(field.min, "min")
              if (newValue) newSelection[field.name] = newValue
            }
          }
          if (field.type === "select") {
            if (!previous[field.name] || reset) {
              newSelection[field.name] = ""
            }
          }
        })
        return newSelection
      })
    },
    [availableAction.schema, resolveSignal]
  )

  useEffect(() => {
    setInitialValues()
  }, [setInitialValues])

  // Update signals when selection changes
  useEffect(() => {
    const newSignals: ActionSignals = {}

    availableAction.schema.forEach((field: ActionField) => {
      const selectedValue = selection[field.name]
      if (field.type === "select" && field.options) {
        const selectedOption = field.options.find((option) => {
          return option.value == selectedValue // Non strict comparison is intentional - allows numbers and string numbers to be considered equal
        })
        Object.assign(newSignals, selectedOption?.signals)
      }
    })

    setSignals(newSignals)
  }, [selection, availableAction.schema])

  const openDialog = () => {
    dialogRef.current?.showModal()
  }

  const closeDialog = () => {
    dialogRef.current?.close()
  }

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!publicGameState.game) return null
    const csrfToken = getCSRFToken()
    closeDialog()

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
      setInitialValues(true)
      toast.success("Action succeeded")
    } else {
      toast.error("Action failed")
    }
  }

  const checkConditions = (conditions: ActionCondition[]) =>
    conditions.some((condition: ActionCondition) => {
      const resolvedValue1 = resolveSignal(condition.value1)
      const resolvedValue2 = resolveSignal(condition.value2)
      if (!resolvedValue1 || !resolvedValue2) return true
      if (condition.operation == "==") {
        return resolvedValue1 == resolvedValue2
      }
      if (condition.operation == "!=") {
        return resolvedValue1 != resolvedValue2
      }
      if (condition.operation == ">=") {
        return resolvedValue1 >= resolvedValue2
      }
      if (condition.operation == ">") {
        return resolvedValue1 > resolvedValue2
      }
      if (condition.operation == "<=") {
        return resolvedValue1 <= resolvedValue2
      }
      if (condition.operation == "<") {
        return resolvedValue1 < resolvedValue2
      }
    })

  const renderObject = (objectClass: string, id: number) => {
    if (objectClass === "senator") {
      const senator = publicGameState.senators.find((s) => s.id === id)
      return <>{senator?.displayName}</>
    }
  }

  const renderField = (field: ActionField, index: number) => {
    const id = `${field.name}_${index}`

    if (field.type === "select") {
      const validOptions = field.options?.filter((o) =>
        o.conditions ? checkConditions(o.conditions) : true
      )

      return (
        <div key={index} className="flex flex-col gap-1">
          <label htmlFor={id} className="font-semibold">
            {field.name}
          </label>
          <select
            id={id}
            value={selection[field.name]}
            onChange={(e) => {
              setSelection((prevSelection) => ({
                ...prevSelection,
                [field.name]: e.target.value,
              }))
            }}
            required
            className="p-1 border border-blue-600 rounded-md"
          >
            <option value="">-- select an option --</option>
            {validOptions?.map((option, index: number) => (
              <option key={index} value={option.value}>
                {option.name ??
                  (option.object_class && option.id
                    ? renderObject(option.object_class, option.id)
                    : "")}
              </option>
            ))}
          </select>
        </div>
      )
    }

    if (field.type === "number") {
      let selectedMin = resolveLimit(field.min, "min")
      let selectedMax = resolveLimit(field.max, "max")
      return (
        <div key={index} className="flex flex-col gap-1">
          <label htmlFor={id} className="font-semibold">
            {field.name}
          </label>
          <input
            type="number"
            min={selectedMin}
            max={selectedMax}
            value={selection[field.name] ?? selectedMin}
            onChange={(e) =>
              setSelection((prevSelection) => ({
                ...prevSelection,
                [field.name]: e.target.value,
              }))
            }
            required
            className="p-1 px-1.5 border border-blue-600 rounded-md"
          />
        </div>
      )
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {availableAction.schema.length === 0 ? (
        <button
          type="submit"
          className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md bg-white hover:bg-blue-100"
        >
          {availableAction.name}
        </button>
      ) : (
        <button
          type="button"
          onClick={openDialog}
          className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md bg-white hover:bg-blue-100"
        >
          {availableAction.name}...
        </button>
      )}

      <dialog ref={dialogRef} className="p-6 bg-white rounded-lg shadow-lg">
        <div className="flex flex-col gap-6 w-[350px]">
          <div className="flex flex-col gap-4">
            <h3 className="text-xl">{availableAction.name}</h3>
            <ActionDescription actionName={availableAction.name} />
          </div>
          <div className="flex flex-col gap-6">
            {availableAction.schema.map((field: ActionField, number: number) =>
              renderField(field, number)
            )}
          </div>
          <div className="mt-4 flex gap-4 justify-end">
            <button
              type="button"
              onClick={closeDialog}
              className="px-4 py-1 text-neutral-500 border border-neutral-500 rounded-md hover:bg-neutral-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
            >
              Submit
            </button>
          </div>
        </div>
      </dialog>
    </form>
  )
}

export default ActionHandler
