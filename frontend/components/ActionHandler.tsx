import { useCallback, useEffect, useRef, useState } from "react"
import React from "react"
import toast from "react-hot-toast"

import * as math from "mathjs"

import AvailableAction, {
  ActionCondition,
  ActionSignals,
  Field,
  SelectOption,
} from "@/classes/AvailableAction"
import PublicGameState from "@/classes/PublicGameState"
import getCSRFToken from "@/utils/csrf"
import getDiceProbability from "@/utils/dice"
import { toSentenceCase } from "@/utils/text"

import ActionDescription from "./ActionDescription"

export type ActionSelection = {
  [key: string]: string | number | (string | number)[] | boolean
}

type SetSelection =
  | ActionSelection
  | ((prev: ActionSelection | undefined) => ActionSelection)

interface ActionHandlerProps {
  availableAction: AvailableAction
  publicGameState: PublicGameState
  selection: ActionSelection
  setSelection: (newSelection: SetSelection) => void
  isExpanded?: boolean
  setIsExpanded?: (expanded: boolean) => void
}

const ActionHandler = ({
  availableAction,
  publicGameState,
  selection,
  setSelection,
  isExpanded,
  setIsExpanded,
}: ActionHandlerProps) => {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const initializedActionRef = useRef<string | null>(null)
  const prevSignalsRef = useRef<ActionSignals>({})
  const [signals, setSignals] = useState<ActionSignals>({})
  const [feedback, setFeedback] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)

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
    [signals],
  )

  const resolveExpression = useCallback(
    (expression: string | number | null | undefined, defaultValue?: number) => {
      if (typeof expression === "string") {
        const components = expression.split(" ")
        let numericLiteral = ""
        for (let i = 0; i < components.length; i++) {
          const resolved = resolveSignal(components[i])
          // Only use defaultValue if explicitly provided and signal is undefined/null
          const value =
            (resolved === undefined || resolved === null) &&
            defaultValue !== undefined
              ? defaultValue
              : resolved
          numericLiteral += " " + value
        }
        try {
          // Resolve numeric literal expression
          return math.evaluate(numericLiteral)
        } catch {
          // Not a valid numeric literal expression - just return the expression with resolved signals
          return numericLiteral
        }
      } else {
        return expression
      }
    },
    [resolveSignal],
  )

  const resolveLimit = useCallback(
    (
      limits: (number | string)[] | undefined,
      type: "min" | "max",
    ): number | undefined => {
      let selectedLimit = undefined
      if (Array.isArray(limits)) {
        for (const limit of limits) {
          const resolvedLimit = resolveExpression(limit, 0)
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
      if (!Array.isArray(limits) && limits !== undefined) {
        console.warn(
          "resolveLimit expected an array or undefined, got:",
          limits,
        )
      }
      return selectedLimit
    },
    [resolveExpression],
  )

  const checkConditions = useCallback(
    (conditions: ActionCondition[]) =>
      conditions.every((condition: ActionCondition) => {
        // Determine if this is a numeric comparison operation
        const isNumericOperation = [">=", ">", "<=", "<"].includes(
          condition.operation,
        )

        // For numeric operations, default undefined/null to 0
        // For equality operations, keep raw values (undefined, null, etc.)
        const resolvedValue1 = isNumericOperation
          ? resolveExpression(condition.value1, 0)
          : resolveExpression(condition.value1)
        const resolvedValue2 = isNumericOperation
          ? resolveExpression(condition.value2, 0)
          : resolveExpression(condition.value2)

        // For equality operations, allow null/undefined comparisons
        if (condition.operation == "==") {
          const result = resolvedValue1 == resolvedValue2
          return result
        }
        if (condition.operation == "!=") {
          const result = resolvedValue1 != resolvedValue2
          return result
        }

        // For numeric comparison operations, check for valid numeric values
        if (
          resolvedValue1 === undefined ||
          resolvedValue1 === null ||
          resolvedValue1 === "" ||
          isNaN(resolvedValue1)
        )
          return false
        if (
          resolvedValue2 === undefined ||
          resolvedValue2 === null ||
          resolvedValue2 === "" ||
          isNaN(resolvedValue2)
        )
          return false

        if (condition.operation == ">=") {
          const result = resolvedValue1 >= resolvedValue2
          return result
        }
        if (condition.operation == ">") {
          const result = resolvedValue1 > resolvedValue2
          return result
        }
        if (condition.operation == "<=") {
          const result = resolvedValue1 <= resolvedValue2
          return result
        }
        if (condition.operation == "<") {
          const result = resolvedValue1 < resolvedValue2
          return result
        }
        return false
      }),
    [resolveExpression, signals],
  )

  const setInitialValues = useCallback(
    (reset: boolean = false) => {
      setSelection((prev: ActionSelection | undefined) => {
        if (!prev) return {}

        const newSelection: ActionSelection = { ...prev }
        let hasChanges = false
        availableAction.schema.forEach((field: Field) => {
          if (field.type === "number") {
            if (prev[field.name] !== "" && (!prev[field.name] || reset)) {
              const newValue = resolveLimit(field.min, "min")
              if (newValue !== undefined && prev[field.name] !== newValue) {
                newSelection[field.name] = newValue
                hasChanges = true
              }
            }
          }
          if (field.type === "select") {
            if (!prev[field.name] || reset) {
              if (prev[field.name] !== "") {
                newSelection[field.name] = ""
                hasChanges = true
              }
            }
          }
        })
        return hasChanges ? newSelection : prev
      })
    },
    [setSelection, availableAction.schema, resolveLimit],
  )

  // Initialize form values only once per action
  useEffect(() => {
    if (initializedActionRef.current !== availableAction.identifier) {
      initializedActionRef.current = availableAction.identifier
      setInitialValues()
    }
  }, [availableAction.identifier, setInitialValues])

  // Update signals when selection changes
  useEffect(() => {
    const newSignals: ActionSignals = {}

    availableAction.schema.forEach((field: Field) => {
      const selectedValue = selection[field.name]
      if (field.type === "select" && field.options) {
        const selectedOption = field.options.find((option: SelectOption) => {
          return option.value == selectedValue // Non strict comparison is intentional - allows numbers and string numbers to be considered equal
        })
        Object.assign(newSignals, selectedOption?.signals)
      }
      if (field.type === "multiselect" && field.options) {
        if (Array.isArray(selectedValue)) {
          selectedValue.forEach((value) => {
            const matchedOption = field.options.find((option: SelectOption) => {
              return option.value == value // Non strict comparison is intentional
            })

            if (matchedOption?.signals) {
              for (const key in matchedOption.signals) {
                const signalValue = matchedOption.signals[key]

                if (typeof signalValue === "number") {
                  newSignals[key] = (newSignals[key] || 0) + signalValue
                } else {
                  newSignals[key] = signalValue
                }
              }
            }
          })
        }
      }
      if (field.type === "number" && field.signals) {
        for (const key in field.signals) {
          if (field.signals[key] === "VALUE") {
            Object.assign(newSignals, {
              [key]: String(selectedValue),
            })
          }
        }
      }
    })

    setSignals(newSignals)
  }, [selection, availableAction.schema])

  // Clean up invalid field values when signals change
  useEffect(() => {
    // Only clean if signals actually changed
    const signalsStr = JSON.stringify(signals)
    const prevSignalsStr = JSON.stringify(prevSignalsRef.current)

    if (signalsStr === prevSignalsStr) {
      return
    }

    prevSignalsRef.current = signals

    setSelection((prev) => {
      if (!prev) return {}

      const newSelection: ActionSelection = { ...prev }
      let hasChanges = false

      availableAction.schema.forEach((field: Field) => {
        // Clear fields that are hidden due to unmet conditions
        if ("conditions" in field && field.conditions) {
          const conditionsMet = checkConditions(field.conditions)
          if (!conditionsMet && newSelection[field.name] !== undefined) {
            delete newSelection[field.name]
            hasChanges = true
            return // Skip to next field
          }
        }

        // Validate select field value
        if (field.type === "select" && field.options) {
          const validOptions = field.options.filter((o) =>
            o.conditions ? checkConditions(o.conditions) : true,
          )
          const currentValue = newSelection[field.name]

          // Check if current value is valid using loose equality (handles string/number mismatch)
          const isValid =
            currentValue === undefined ||
            currentValue === "" ||
            validOptions.some((o) => o.value == currentValue) // Use == for loose equality

          if (!isValid) {
            newSelection[field.name] = ""
            hasChanges = true
          }
        }
        // Filter multiselect to only valid options
        if (field.type === "multiselect" && field.options) {
          const validOptions = field.options.filter((o) =>
            o.conditions ? checkConditions(o.conditions) : true,
          )
          const currentSelection = newSelection[field.name]

          if (Array.isArray(currentSelection)) {
            // Use loose equality to handle string/number mismatches
            const cleanedSelection = currentSelection.filter((v) =>
              validOptions.some((o) => o.value == v),
            )
            if (cleanedSelection.length !== currentSelection.length) {
              newSelection[field.name] = cleanedSelection
              hasChanges = true
            }
          }
        }
      })

      return hasChanges ? newSelection : prev
    })
  }, [signals, availableAction.schema, setSelection])

  useEffect(() => {
    setFeedback("")
  }, [selection, setFeedback])

  useEffect(() => {
    if (isExpanded) {
      dialogRef.current?.showModal()
    }
  }, [isExpanded])

  const openDialog = () => {
    dialogRef.current?.showModal()
    setIsExpanded?.(true)
  }

  const closeDialog = () => {
    setFeedback("")
    dialogRef.current?.close()
    setIsExpanded?.(false)
  }

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
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
      },
    )
    setLoading(false)
    if (response.ok) {
      closeDialog()
      setInitialValues(true)
    } else {
      const result = await response.json()
      if (result.message) {
        setFeedback(result.message)
      } else {
        toast.error("Action failed")
      }
    }
  }

  const renderObject = (objectClass: string, id: number) => {
    if (objectClass === "campaign") {
      const campaign = publicGameState.campaigns.find((c) => c.id === id)
      const war = publicGameState.wars.find((w) => w.id === campaign?.war)
      return (
        <>
          {toSentenceCase(campaign?.displayName ?? "")} ({war?.name})
        </>
      )
    } else if (objectClass === "faction") {
      const faction = publicGameState.factions.find((f) => f.id === id)
      return <>{faction?.displayName}</>
    } else if (objectClass === "fleet") {
      const fleet = publicGameState.fleets.find((l) => l.id === id)
      return <>Fleet {fleet?.name}</>
    } else if (objectClass === "legion") {
      const legion = publicGameState.legions.find((l) => l.id === id)
      return <>Legion {legion?.name}</>
    } else if (objectClass === "senator") {
      const senator = publicGameState.senators.find((s) => s.id === id)
      return <>{senator?.displayName}</>
    } else if (objectClass === "war") {
      const war = publicGameState.wars.find((w) => w.id === id)
      return <>{war?.name}</>
    }
  }

  const renderField = (field: Field, index: string) => {
    const id = `${field.name}_${index}`

    if (field.type === "select") {
      const validOptions = field.options?.filter((o) =>
        o.conditions ? checkConditions(o.conditions) : true,
      )

      return (
        <div key={index} className="flex flex-col gap-1">
          <label htmlFor={id} className="font-semibold">
            {field.name}
          </label>
          <select
            id={id}
            value={selection[field.name] as string | number}
            onChange={(e) => {
              setSelection((prev) => ({
                ...prev,
                [field.name]: e.target.value,
              }))
            }}
            required
            className="rounded-md border border-blue-600 p-1"
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

    if (field.type === "multiselect") {
      const validOptions = field.options?.filter((o) =>
        o.conditions ? checkConditions(o.conditions) : true,
      )

      const toggleValue = (value: string | number) => {
        const currentValue = selection[field.name]

        if (Array.isArray(currentValue)) {
          if (currentValue.includes(value)) {
            setSelection((prev) => ({
              ...prev,
              [field.name]: currentValue.filter((v) => v !== value),
            }))
          } else {
            setSelection((prev) => ({
              ...prev,
              [field.name]: [...currentValue, value],
            }))
          }
        } else {
          setSelection((prev) => ({
            ...prev,
            [field.name]: [value],
          }))
        }
      }

      const selectAll = () => {
        setSelection((prev) => ({
          ...prev,
          [field.name]: validOptions.map((option) => option.value),
        }))
      }

      const selectNone = () => {
        setSelection((prev) => ({
          ...prev,
          [field.name]: [],
        }))
      }

      const rawValue = selection[field.name]
      const selectedValues = Array.isArray(rawValue)
        ? (rawValue as (string | number)[])
        : []

      return (
        <div key={index} className="flex flex-col gap-1">
          <label className="font-semibold">{field.name}</label>
          <div className="flex flex-col gap-1 overflow-hidden rounded-md border border-blue-600">
            <div className="inline-block w-full min-w-[180px] select-none px-2 pt-1 text-sm">
              Selected: {selectedValues.length}{" "}
              <span className="text-neutral-500">/</span>{" "}
              <button
                type="button"
                onClick={selectAll}
                className="text-blue-600 hover:underline"
              >
                All
              </button>{" "}
              <span className="text-neutral-500">/</span>{" "}
              <button
                type="button"
                onClick={selectNone}
                className="text-blue-600 hover:underline"
              >
                None
              </button>
            </div>

            <div className="flex max-h-48 flex-col gap-x-4 gap-y-1 overflow-auto pb-1 pl-2.5">
              {validOptions?.map((option, idx: number) => (
                <label
                  key={idx}
                  className="inline-flex items-center gap-2 whitespace-nowrap"
                >
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(option.value)}
                    onChange={() => toggleValue(option.value)}
                    className="rounded border-blue-600"
                  />
                  <span className="inline-block pr-4">
                    {option.name ??
                      (option.object_class && option.id
                        ? renderObject(option.object_class, option.id)
                        : "")}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>
      )
    }

    if (field.type === "number") {
      const selectedMin = resolveLimit(field.min, "min")
      const selectedMax = resolveLimit(field.max, "max")

      const handleMinusClick = () =>
        setSelection((prev) => {
          if (!prev) return {}
          return {
            ...prev,
            [field.name]:
              selectedMax !== undefined &&
              Number(prev[field.name]) > selectedMax
                ? selectedMax
                : Number(prev[field.name]) - 1,
          }
        })

      const handlePlusClick = () =>
        setSelection((prev) => {
          if (!prev) return {}
          return {
            ...prev,
            [field.name]:
              selectedMin !== undefined &&
              Number(prev[field.name]) < selectedMin
                ? selectedMin
                : Number(prev[field.name]) + 1,
          }
        })

      return (
        <div key={index} className="flex max-w-[350px] flex-col gap-1">
          <label htmlFor={id} className="font-semibold">
            {field.name}
          </label>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleMinusClick}
                disabled={
                  selectedMin === undefined
                    ? false
                    : Number(selection[field.name]) <= selectedMin
                }
                className="relative h-6 min-w-6 rounded-full border border-red-500 text-red-500 hover:bg-red-100 disabled:border-neutral-400 disabled:text-neutral-400 disabled:hover:bg-transparent"
              >
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                  &minus;
                </div>
              </button>
              <input
                id={id}
                type="number"
                min={selectedMin}
                max={selectedMax}
                value={
                  (selection[field.name] ?? selectedMin) as string | number
                }
                onChange={(e) =>
                  setSelection((prev) => ({
                    ...prev,
                    [field.name]: Number(e.target.value),
                  }))
                }
                required
                className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5"
              />
              <button
                type="button"
                onClick={handlePlusClick}
                disabled={
                  selectedMax === undefined
                    ? false
                    : Number(selection[field.name]) >= selectedMax
                }
                className="relative h-6 min-w-6 rounded-full border border-green-500 text-green-500 hover:bg-green-100 disabled:border-neutral-400 disabled:text-neutral-400 disabled:hover:bg-transparent"
              >
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                  +
                </div>
              </button>
            </div>
            {selectedMin === undefined ||
              selectedMax === undefined ||
              (selectedMin < selectedMax && (
                <div className="flex w-full items-center justify-center">
                  <button
                    type="button"
                    className={`w-10 cursor-default px-2 text-sm ${
                      selection[field.name] !== selectedMin &&
                      "text-neutral-400"
                    }`}
                    onClick={() =>
                      setSelection((prev) => ({
                        ...prev,
                        [field.name]: selectedMin,
                      }))
                    }
                  >
                    {selectedMin}
                  </button>

                  <input
                    type="range"
                    min={selectedMin}
                    max={selectedMax}
                    value={
                      (selection[field.name] ?? selectedMin) as string | number
                    }
                    onChange={(e) =>
                      setSelection((prev) => ({
                        ...prev,
                        [field.name]: Number(e.target.value),
                      }))
                    }
                    className="w-full"
                  ></input>
                  <button
                    type="button"
                    className={`w-10 cursor-default px-2 text-sm ${
                      selection[field.name] !== selectedMax &&
                      "text-neutral-400"
                    }`}
                    onClick={() =>
                      setSelection((prev) => ({
                        ...prev,
                        [field.name]: selectedMax,
                      }))
                    }
                  >
                    {selectedMax}
                  </button>
                </div>
              ))}
          </div>
        </div>
      )
    }

    if (field.type === "calculation") {
      if (field.conditions && !checkConditions(field.conditions)) {
        return null
      }
      const expression = field.value
      const resolved = resolveExpression(expression, 0)
      const labelText =
        field.label === "HIDDEN" ? "" : (field.label ?? field.name)

      const label = labelText && <>{labelText}: </>
      const paragraph = (
        <p>
          {label}
          {resolved ?? "—"}
        </p>
      )
      if (field.style === "warning") {
        return (
          <div
            key={index}
            className="inline-flex max-w-[400px] rounded-md bg-red-50 px-2 py-1 text-red-600"
          >
            {paragraph}
          </div>
        )
      } else {
        return (
          <div
            key={index}
            className="inline-flex max-w-[400px] rounded-md bg-blue-50 px-2 py-1 text-blue-600"
          >
            {paragraph}
          </div>
        )
      }
    }

    if (field.type === "chance" && field.dice) {
      if (field.conditions && !checkConditions(field.conditions)) {
        return null
      }

      let netModifier = 0
      field.modifiers?.forEach((modifier: string | number) => {
        const possibleModifier = resolveExpression(modifier, 0)
        netModifier += Number(possibleModifier)
      })
      const probability = getDiceProbability(
        field.dice,
        netModifier,
        {
          min: field.target_min,
          max: field.target_max,
          exacts:
            field.target_exacts?.map((value) => resolveExpression(value, 0)) ??
            [],
        },
        field.ignored_numbers?.map((value) => resolveExpression(value, 0)) ??
          [],
      )
      const probabilityPercentage = Math.round(probability * 100)

      const label = field.label === "HIDDEN" ? "" : (field.label ?? field.name)
      return (
        <div
          key={index}
          className="inline-flex max-w-[400px] gap-2 rounded-md bg-neutral-100 px-2 py-1 text-neutral-600"
        >
          <p key={index}>
            {label && <>{label}: </>}
            <span className="inline-block">{probabilityPercentage}%</span>
          </p>
        </div>
      )
    }

    if (field.type === "boolean") {
      if (field.conditions) {
        const conditionsMet = checkConditions(field.conditions)
        console.log("Boolean field conditions check:", {
          fieldName: field.name,
          conditions: field.conditions,
          signals,
          conditionsMet,
        })
        if (!conditionsMet) {
          return null
        }
      }
      return (
        <div key={index} className="flex">
          <input
            type="checkbox"
            id={id}
            checked={!!selection[field.name]}
            onChange={() =>
              setSelection((prev) => ({
                ...(prev ?? {}),
                [field.name]: !(prev?.[field.name] ?? false),
              }))
            }
          />
          <label htmlFor={id} className="pl-2 font-semibold">
            {field.name}
          </label>
        </div>
      )
    }
  }

  // Group fields
  const groupedFields: (Field | Field[])[] = []
  let currentGroup: Field[] = []

  for (const field of availableAction.schema) {
    if (field.inline && currentGroup.length > 0) {
      currentGroup.push(field)
    } else {
      if (currentGroup.length > 0) groupedFields.push(currentGroup)
      currentGroup = [field]
    }
  }
  if (currentGroup.length > 0) groupedFields.push(currentGroup)

  const renderedItems = groupedFields
    .map((group, index) => {
      const key = `field-${index}`

      const isInfo = (f: Field) =>
        f.type === "calculation" || f.type === "chance"

      const getFirstField = (g: Field | Field[]) =>
        Array.isArray(g) ? g[0] : g

      const renderGroup = () => {
        if (Array.isArray(group)) {
          const children = group
            .map((field, i) => {
              const content = renderField(field, `${index}-${i}`)
              return content ? (
                <div key={i} className="flex-1">
                  {content}
                </div>
              ) : null
            })
            .filter((item): item is NonNullable<typeof item> => item !== null)

          return children.length > 0 ? (
            <div className={"flex flex-col gap-6 sm:flex-row"}>{children}</div>
          ) : null
        } else {
          const content = renderField(group, index.toString())
          return content ? <div>{content}</div> : null
        }
      }

      const content = renderGroup()
      return content
        ? {
            key,
            content,
            isInfo: isInfo(getFirstField(group)),
          }
        : null
    })
    .filter((item): item is NonNullable<typeof item> => item !== null)

  const renderFeedback = (feedback: string) => {
    if (feedback.includes(":")) {
      const colonIndex = feedback.indexOf(":")
      const boldText = feedback.slice(0, colonIndex)
      const normalText = feedback.slice(colonIndex)
      return (
        <p>
          <strong className="font-semibold">{boldText}</strong>
          {normalText}
        </p>
      )
    } else {
      return <p>{feedback}</p>
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {availableAction.schema.length === 0 ? (
        <button
          type="submit"
          className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
        >
          {availableAction.name}
        </button>
      ) : (
        <button
          type="button"
          onClick={openDialog}
          className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
        >
          {availableAction.name}...
        </button>
      )}

      <dialog ref={dialogRef} className="rounded-lg bg-white p-6 shadow-lg">
        <div className="flex flex-col gap-6">
          <div className="flex max-w-[400px] flex-col gap-4">
            <h3 className="text-xl">{availableAction.name}</h3>
            <ActionDescription
              actionName={availableAction.name}
              context={availableAction.context}
            />
          </div>
          {feedback && (
            <div className="inline-flex max-w-[400px] rounded-md bg-red-50 px-2 py-1 text-red-600">
              {renderFeedback(feedback)}
            </div>
          )}
          <div className="flex flex-col overflow-y-auto">
            {renderedItems.map((item, index) => {
              const prev = renderedItems[index - 1]
              const needsSmallGap = prev && prev.isInfo && item.isInfo

              return (
                <React.Fragment key={item.key}>
                  {index > 0 && (
                    <div className={needsSmallGap ? "h-1" : "h-6"} />
                  )}
                  <div
                    className={
                      item.isInfo && renderedItems.length > 5 ? "text-sm" : ""
                    }
                  >
                    {item.content}
                  </div>
                </React.Fragment>
              )
            })}
          </div>
          <div className="mt-4 flex justify-end gap-4">
            <button
              type="button"
              onClick={closeDialog}
              className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="select-none rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:opacity-50"
              disabled={loading}
            >
              Confirm
            </button>
          </div>
        </div>
      </dialog>
    </form>
  )
}

export default ActionHandler
