import { useState } from "react"

import type { Meta, StoryObj } from "@storybook/react"

import Log from "@/classes/Log"

import LogList from "./LogList"

const sampleTexts = [
  "All senators have survived the mortality phase.",
  "Aurelius contributed 3T to the State treasury. He gained 1 influence.",
  "Cornelius of The Optimates began a persuasion attempt targeting the unaligned senator Flamininus, with a bribe of 5T (42% success chance). Blackmail was used to prevent counter-bribes.",
  "Cornelius successfully persuaded the unaligned senator Flamininus to join The Optimates.",
  "The Imperials drew the 1st Punic War, which is immediately active. The war is joined by Hannibal.",
  "Senators in The Republic voted yea with 4 vote(s).",
  "Motion passed: Aurelius as Rome Consul and Fabius as Field Consul (12 yea, 3 nay).",
  "The Populists sent Calpurnicus to assassinate Scipio. The assassination attempt failed. Calpurnicus was caught!",
  "Calpurnicus of The Populists was executed for attempted murder.",
  "Fabius' delaying tactics saved 2 legions from destruction.",
  "The State Treasury gained 25T in spoils of war.",
  "Military glory rewards Fabius with 5 influence and 3 popularity.",
  "Legion I hardened into a Veteran Legion, owing allegiance to Fabius.",
  "Scipio bought a knight for 2T.",
  "An outraged mob stormed the Senate, killing 2 senators.",
  "Aurelius gave a dull State of the Republic speech. The people were unimpressed, causing unrest to remain unchanged.",
  "Rome's 3 legions deserted, strengthening the 2nd Punic War by 3.",
  "Flamininus profiteered from the famine on the Grain concession, earning an extra 4T. He lost 2 popularity.",
  "The Conservatives used their tribune to propose the motion: Cornelius as Censor.",
  "Motion defeated: Dispatch Fabius against 1st Punic War with 10 legions and 5 fleets (4 yea, 8 nay).",
]

const makeLogs = (count: number): Log[] =>
  Array.from({ length: count }, (_, i) => {
    const id = i + 1
    return new Log({
      id,
      turn: Math.floor(id / 5) + 1,
      phase: ["mortality", "revenue", "forum", "population", "senate"][id % 5],
      created_on: new Date().toISOString(),
      text: sampleTexts[id % sampleTexts.length],
    })
  })

const clearLogListStorage = (key: string) => {
  localStorage.removeItem(`${key}-seenLogs`)
  localStorage.removeItem(`${key}-doneLogs`)
}

const InteractivePlayground = ({
  initialLogCount = 0,
}: {
  initialLogCount?: number
}) => {
  const [logs, setLogs] = useState<Log[]>(() => makeLogs(initialLogCount))
  const [count, setCount] = useState(1)
  const [mounted, setMounted] = useState(true)

  const addLogs = () => {
    setLogs((prev) => {
      const newLogs = Array.from({ length: count }, (_, i) => {
        const nextId = prev.length + i + 1
        return new Log({
          id: nextId,
          turn: Math.floor(nextId / 5) + 1,
          phase: ["mortality", "revenue", "forum", "population", "senate"][
            nextId % 5
          ],
          created_on: new Date().toISOString(),
          text: sampleTexts[nextId % sampleTexts.length],
        })
      })
      return [...prev, ...newLogs]
    })
  }

  return (
    <div className="flex h-screen">
      <div className="flex flex-col justify-end gap-2 p-4">
        <div className="text-sm text-neutral-500">Logs: {logs.length}</div>
        <label className="flex flex-col gap-1 text-sm">
          Add logs count
          <input
            type="number"
            value={count}
            min={1}
            onChange={(e) => setCount(Number(e.target.value))}
            className="border border-black px-2 py-1"
          />
        </label>
        <button
          onClick={addLogs}
          className="cursor-pointer whitespace-nowrap bg-neutral-800 px-4 py-2 text-white"
        >
          Add logs
        </button>
        <button
          onClick={() => setMounted((o) => !o)}
          className="cursor-pointer whitespace-nowrap bg-neutral-800 px-4 py-2 text-white"
        >
          {mounted ? "Unmount" : "Mount"}
        </button>
      </div>
      <div className="h-full border-x border-black">
        {mounted && <LogList logs={logs} storageKey="storybook" />}
      </div>
    </div>
  )
}

const meta: Meta<typeof LogList> = {
  component: LogList,
  parameters: {
    layout: "fullscreen",
  },
  decorators: [
    (Story) => {
      clearLogListStorage("storybook")
      return <Story />
    },
  ],
}

export default meta
type Story = StoryObj<typeof LogList>

export const Empty: Story = {
  render: () => <InteractivePlayground />,
}

export const OneLog: Story = {
  render: () => <InteractivePlayground initialLogCount={1} />,
}

export const FourLogs: Story = {
  render: () => <InteractivePlayground initialLogCount={4} />,
}

export const TwentyLogs: Story = {
  render: () => <InteractivePlayground initialLogCount={20} />,
}
