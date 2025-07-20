import { useCallback, useEffect, useRef, useState } from "react"
import React from "react"

import { v4 as uuidv4 } from "uuid"

import PublicGameState from "@/classes/PublicGameState"

import CombatCalculatorTab from "./CombatCalculatorTab"

const defaultTabName = "Combat"

type Tab = {
  id: string
  name: string
}

interface ActionHandlerProps {
  publicGameState: PublicGameState
}

const CombatCalculator = ({ publicGameState }: ActionHandlerProps) => {
  const [tabs, setTabs] = useState<Tab[]>([
    { id: uuidv4(), name: defaultTabName },
  ])
  const [selectedTabId, setSelectedTabId] = useState<string>(tabs[0].id)

  const addTab = () => {
    const newTab: Tab = { id: uuidv4(), name: defaultTabName }
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
    (name: string | null) => {
      setTabs((prevTabs) => {
        const newName = name ?? defaultTabName
        console.log(newName)
        return prevTabs.map((tab) =>
          tab.id === selectedTabId ? { ...tab, name: newName } : tab,
        )
      })
    },
    [selectedTabId],
  )

  const [isOpen, setIsOpen] = useState(false)
  const [position, setPosition] = useState({ x: 100, y: 100 })
  const [dragging, setDragging] = useState(false)
  const offsetRef = useRef({ x: 0, y: 0 })

  useEffect(() => {
    setPosition((pos) => ({
      x: (window.innerWidth - 800) / 2,
      y: pos.y,
    }))
  }, [])

  const handleMouseDown = (e: React.MouseEvent) => {
    setDragging(true)
    offsetRef.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    }
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (dragging) {
      setPosition({
        x: e.clientX - offsetRef.current.x,
        y: e.clientY - offsetRef.current.y,
      })
    }
  }

  const handleMouseUp = () => setDragging(false)

  useEffect(() => {
    if (dragging) {
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
    } else {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [dragging])

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
      >
        Combat Calculator
      </button>

      <div
        className="rounded-lg border bg-white shadow-lg"
        style={{
          position: "fixed",
          top: position.y,
          left: position.x,
          zIndex: 1000,
          cursor: dragging ? "grabbing" : "default",
          width: "800px",
          display: isOpen ? "block" : "none", // <== toggle visibility here
        }}
      >
        <div
          className="flex cursor-grab select-none items-center justify-between px-6 py-4"
          onMouseDown={handleMouseDown}
        >
          <h3 className="text-xl">Combat Calculator</h3>
          <button
            onClick={() => setIsOpen(false)}
            className="text-neutral-600 hover:text-black"
          >
            ✕
          </button>
        </div>

        <div className="px-6 pb-6">
          <div className="mx-[-24px] flex max-w-[800px] select-none flex-wrap items-center gap-2 border-neutral-400 bg-neutral-100 px-6 py-2">
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
              onClick={() => setIsOpen(false)}
              className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

export default CombatCalculator
