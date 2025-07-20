import { useCallback, useRef, useState } from "react"
import React from "react"

import { v4 as uuidv4 } from "uuid"

import PublicGameState from "@/classes/PublicGameState"

import CombatCalculatorTab from "./CombatCalculatorTab"

type Tab = {
  id: string
  name: string
}

interface ActionHandlerProps {
  publicGameState: PublicGameState
}

const CombatCalculator = ({ publicGameState }: ActionHandlerProps) => {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [tabs, setTabs] = useState<Tab[]>([{ id: uuidv4(), name: "Combat" }])
  const [selectedTabId, setSelectedTabId] = useState<string>(tabs[0].id)

  const openDialog = () => {
    dialogRef.current?.showModal()
  }

  const closeDialog = () => {
    dialogRef.current?.close()
  }

  const addTab = () => {
    const newTab: Tab = {
      id: uuidv4(),
      name: "Combat",
    }
    setTabs([...tabs, newTab])
    setSelectedTabId(newTab.id)
  }

  const removeTab = (id: string) => {
    if (tabs.length > 1) {
      const filtered = tabs.filter((tab) => tab.id !== id)
      setTabs(filtered)
      if (selectedTabId === id && filtered.length > 0) {
        setSelectedTabId(filtered[0].id)
      }
    }
  }

  const renameTab = useCallback(
    (name: string) => {
      setTabs((prevTabs) =>
        prevTabs.map((tab) =>
          tab.id === selectedTabId ? { ...tab, name } : tab,
        ),
      )
    },
    [selectedTabId],
  )

  return (
    <>
      <button
        type="button"
        onClick={openDialog}
        className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
      >
        Combat Calculator
      </button>
      <dialog ref={dialogRef} className="rounded-lg bg-white p-6 shadow-lg">
        <h3 className="text-xl">Combat Calculator</h3>

        <div className="mx-[-24px] mt-4 flex max-w-[800px] select-none flex-wrap items-center gap-2 border-neutral-400 bg-neutral-100 px-6 py-2">
          {tabs.map((tab, index) => {
            const isLast = index === tabs.length - 1
            const tabContent = (
              <div
                key={tab.id}
                className={`flex flex-row items-center rounded-md ${
                  tab.id === selectedTabId
                    ? "border border-neutral-400 bg-white"
                    : "p-px text-neutral-600 hover:bg-white"
                }`}
              >
                <button
                  className="px-2 py-1"
                  onClick={() => setSelectedTabId(tab.id)}
                  disabled={tab.id === selectedTabId}
                >
                  {tab.name}
                </button>
                {tabs.length > 1 && (
                  <button
                    className="mr-1.5 flex h-5 w-5 items-center justify-center rounded-full text-xs font-semibold text-neutral-500 hover:bg-neutral-200"
                    onClick={() => removeTab(tab.id)}
                  >
                    ✕
                  </button>
                )}
              </div>
            )

            // Wrap last tab + plus button together
            if (isLast) {
              return (
                <div key={tab.id} className="flex items-center gap-2">
                  {tabContent}
                  <button
                    className="flex h-8 w-8 items-center justify-center rounded-full text-2xl hover:bg-neutral-200"
                    onClick={addTab}
                  >
                    +
                  </button>
                </div>
              )
            }

            return tabContent
          })}
        </div>

        {tabs.map((tab) => (
          <div
            key={tab.id}
            style={{ display: tab.id === selectedTabId ? "block" : "none" }}
          >
            <CombatCalculatorTab
              publicGameState={publicGameState}
              renameTab={renameTab}
            />
          </div>
        ))}

        <div className="mt-4 flex justify-end gap-4">
          <button
            type="button"
            onClick={closeDialog}
            className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
          >
            Close
          </button>
        </div>
      </dialog>
    </>
  )
}

export default CombatCalculator
