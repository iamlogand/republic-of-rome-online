"use client"

import { useState } from "react"

interface AccordionItem {
  label: React.ReactNode
  content: React.ReactNode
}

interface AccordionProps {
  items: AccordionItem[]
}

const Accordion = ({ items }: AccordionProps) => {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <div className="flex flex-col gap-2">
      {items.map((item, index) => (
        <div key={index}>
          <button
            type="button"
            className="mt-1 flex items-center gap-1 text-blue-600"
            onClick={() => setOpenIndex(openIndex === index ? null : index)}
          >
            <div className="w-4 select-none text-xs">
              {openIndex === index ? "▼" : "▶"}
            </div>
            <div>{item.label}</div>
          </button>
          {openIndex === index && <div className="mt-1">{item.content}</div>}
        </div>
      ))}
    </div>
  )
}

export default Accordion
