import { CONCESSION_INCOME } from "@/data/concessions"
import { STATESMAN_ABILITIES, STATESMAN_NAMES } from "@/data/statesmen"

const cardLabel = (card: string): string => {
  if (card.startsWith("statesman:")) return STATESMAN_NAMES[card.split(":")[1]]
  if (card.includes(":")) return card.split(":")[1]
  return card
}

const INTRIGUE_DETAILS: Record<string, string> = {
  tribune: "Raise or veto a proposal",
  assassin: "Attempt to assassinate a senator",
  "secret bodyguard": "Protect a senator from assassination",
  blackmail: "Prevent counter-bribes during persuasion",
  seduction: "Prevent counter-bribes during persuasion",
  "influence peddling": "Steal a random card from another faction",
}

type CardCategory = "statesman" | "concession" | "senator" | "intrigue"

const CATEGORY_LABEL: Record<CardCategory, string> = {
  statesman: "Statesmen",
  concession: "Concessions",
  senator: "Senator families",
  intrigue: "Intrigue",
}

const CATEGORY_TIMING: Record<CardCategory, string | undefined> = {
  statesman: "Play during revolution phase to add to your faction",
  concession: "Play during revolution phase to award to a senator",
  senator: "Drawn from the deck — enters play as unaligned",
  intrigue: undefined,
}

const CATEGORY_ORDER: CardCategory[] = [
  "statesman",
  "concession",
  "senator",
  "intrigue",
]

const getCategory = (card: string): CardCategory => {
  if (card.startsWith("statesman:")) return "statesman"
  if (card.startsWith("concession:")) return "concession"
  if (card.startsWith("senator:")) return "senator"
  return "intrigue"
}

const getDetail = (card: string): string | undefined => {
  if (card.startsWith("statesman:"))
    return STATESMAN_ABILITIES[card.split(":")[1]]
  if (card.startsWith("concession:"))
    return CONCESSION_INCOME[card.split(":")[1].trim()]
  return INTRIGUE_DETAILS[card]
}

interface FactionCardsProps {
  cards: string[]
}

const FactionCards = ({ cards }: FactionCardsProps) => {
  if (cards.length === 0) {
    return <span className="text-neutral-600">None</span>
  }

  const groupMap = new Map<CardCategory, string[]>()
  for (const card of cards) {
    const category = getCategory(card)
    if (!groupMap.has(category)) groupMap.set(category, [])
    groupMap.get(category)!.push(card)
  }

  const groups = CATEGORY_ORDER.filter((cat) => groupMap.has(cat)).map(
    (cat) => ({ category: cat, cards: groupMap.get(cat)! }),
  )

  return (
    <div className="flex flex-col gap-4">
      {groups.map(({ category, cards: groupCards }, index) => (
        <div key={category} className="flex flex-col gap-2">
          {index > 0 && <hr className="-mx-4 border-neutral-300" />}
          <div>{CATEGORY_LABEL[category]}</div>
          {CATEGORY_TIMING[category] && (
            <div className="text-sm text-neutral-500">
              {CATEGORY_TIMING[category]}
            </div>
          )}
          <ul className="flex flex-col gap-1">
            {groupCards.map((card, i) => {
              const detail = getDetail(card)
              return (
                <li
                  key={i}
                  className="flex flex-col rounded border border-neutral-400 px-3 py-2"
                >
                  <div className="first-letter:uppercase">
                    {cardLabel(card)}
                  </div>
                  {detail && (
                    <span className="text-sm text-neutral-600">{detail}</span>
                  )}
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </div>
  )
}

export default FactionCards
