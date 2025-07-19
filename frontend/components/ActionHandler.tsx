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
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import getCSRFToken from "@/utils/csrf"
import getDiceProbability from "@/utils/dice"

import ActionDescription from "./ActionDescription"

type Selection = {
  [key: string]: string | number | (string | number)[]
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
    (expression: string | number | undefined) => {
      if (typeof expression === "string") {
        const components = expression.split(" ")
        let numericLiteral = ""
        for (let i = 0; i < components.length; i++) {
          numericLiteral += resolveSignal(components[i]) ?? 0
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
          const resolvedLimit = resolveExpression(limit)
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
    [resolveSignal, resolveExpression],
  )

  const setInitialValues = useCallback(
    (reset: boolean = false) => {
      setSelection((previous: Selection) => {
        const newSelection: Selection = reset ? { ...previous } : previous
        availableAction.schema.forEach((field: Field) => {
          if (field.type === "number") {
            if (
              previous[field.name] !== "" &&
              (!previous[field.name] || reset)
            ) {
              const newValue = resolveLimit(field.min, "min")
              if (newValue !== undefined) {
                newSelection[field.name] = newValue
              }
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
    [availableAction.schema, resolveLimit],
  )

  useEffect(() => {
    setInitialValues()
  }, [setInitialValues])

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

  useEffect(() => {
    setFeedback("")
  }, [selection, setFeedback])

  const openDialog = () => {
    dialogRef.current?.showModal()
  }

  const closeDialog = () => {
    setFeedback("")
    dialogRef.current?.close()
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

  const checkConditions = (conditions: ActionCondition[]) =>
    conditions.every((condition: ActionCondition) => {
      const resolvedValue1 = resolveExpression(condition.value1)
      const resolvedValue2 = resolveExpression(condition.value2)
      if (
        resolvedValue1 === undefined ||
        resolvedValue1 === null ||
        resolvedValue1 === ""
      )
        return false
      if (
        resolvedValue2 === undefined ||
        resolvedValue2 === null ||
        resolvedValue2 === ""
      )
        return false

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
      return false
    })

  const renderObject = (objectClass: string, id: number) => {
    if (objectClass === "faction") {
      const faction = publicGameState.factions.find((f) => f.id === id)
      return <>{faction?.displayName}</>
    }
    if (objectClass === "fleet") {
      const fleet = publicGameState.fleets.find((l) => l.id === id)
      return <>Fleet {fleet?.name}</>
    }
    if (objectClass === "legion") {
      const legion = publicGameState.legions.find((l) => l.id === id)
      return <>Legion {legion?.name}</>
    }
    if (objectClass === "senator") {
      const senator = publicGameState.senators.find((s) => s.id === id)
      return <>{senator?.displayName}</>
    }
    if (objectClass === "war") {
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
              setSelection((prevSelection) => ({
                ...prevSelection,
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
            <div className="inline-block w-full select-none px-2 pt-1 text-sm">
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
      return (
        <div key={index} className="flex max-w-[350px] flex-col gap-1">
          <label htmlFor={id} className="font-semibold">
            {field.name}
          </label>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() =>
                  setSelection((prevSelection) => ({
                    ...prevSelection,
                    [field.name]:
                      selectedMax !== undefined &&
                      Number(prevSelection[field.name]) > selectedMax
                        ? selectedMax
                        : Number(prevSelection[field.name]) - 1,
                  }))
                }
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
                type="number"
                min={selectedMin}
                max={selectedMax}
                value={
                  (selection[field.name] ?? selectedMin) as string | number
                }
                onChange={(e) =>
                  setSelection((prevSelection) => ({
                    ...prevSelection,
                    [field.name]: Number(e.target.value),
                  }))
                }
                required
                className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5"
              />
              <button
                type="button"
                onClick={() =>
                  setSelection((prevSelection) => ({
                    ...prevSelection,
                    [field.name]:
                      selectedMin !== undefined &&
                      Number(prevSelection[field.name]) < selectedMin
                        ? selectedMin
                        : Number(prevSelection[field.name]) + 1,
                  }))
                }
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
                      setSelection((prevSelection) => ({
                        ...prevSelection,
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
                      setSelection((prevSelection) => ({
                        ...prevSelection,
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
                      setSelection((prevSelection) => ({
                        ...prevSelection,
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
      const resolved = resolveExpression(expression)
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
        const possibleModifier = resolveExpression(modifier)
        netModifier += Number(possibleModifier)
      })
      const probability = getDiceProbability(
        field.dice,
        netModifier,
        {
          min: field.target_min,
          max: field.target_max,
          exacts:
            field.target_exacts?.map((value) => resolveExpression(value)) ?? [],
        },
        field.ignored_numbers?.map((value) => resolveExpression(value)) ?? [],
      )
      const probabilityPercentage = Math.round(probability * 100)

      const label = field.label === "HIDDEN" ? "" : (field.label ?? field.name)
      return (
        <div
          key={index}
          className="inline-flex max-w-[400px] gap-2 rounded-md bg-neutral-100 px-2 py-0.5 text-neutral-600"
        >
          <p key={index}>
            {label && <>{label}: </>}
            <span className="inline-block">{probabilityPercentage}%</span>
          </p>
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
              <p>{feedback}</p>
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
