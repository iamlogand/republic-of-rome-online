import { ContextField } from "@/classes/AvailableAction"

const factionLeaderDescription = (
  <p>Your faction leader will be immune from persuasion attempts.</p>
)

interface ActionDescriptionProps {
  actionName: string
  context: ContextField
}

const ActionDescription = ({ actionName, context }: ActionDescriptionProps) => {
  if (actionName === "Attract knight") {
    return (
      <p>
        A senator may attempt to attract a knight. Each knight a senator
        controls increases their personal revenue and votes by +1.
      </p>
    )
  }
  if (actionName === "Contribute") {
    return (
      <>
        <p>
          Senators may contribute talents to the State treasury, which increases
          their influence.
        </p>
        <div className="text-sm">
          <p>10 talents = +1 influence</p>
          <p>25 talents = +3 influence</p>
          <p>50 talents = +7 influence</p>
        </div>
      </>
    )
  }
  if (actionName === "Change faction leader") {
    return factionLeaderDescription
  }
  if (actionName === "Pay for initiative") {
    return <p>Select a senator to pay {context.talents}T for the initiative.</p>
  }
  if (actionName === "Place bid") {
    return (
      <p>
        If you win, one of your senators must pay the bid after the auction.
      </p>
    )
  }
  if (actionName === "Propose raising forces") {
    return (
      <p>
        Raising a legion or fleet costs the State 10T, with a maintenance cost
        of 2T per turn.
      </p>
    )
  }
  if (actionName === "Select faction leader") {
    return factionLeaderDescription
  }
  if (actionName === "Sponsor games") {
    return (
      <>
        <p>
          Senators may spend talents to sponsor games. These games lower
          Rome&apos;s unrest and increase the sponsor&apos;s popularity.
        </p>
        <div className="flex flex-col gap-2 text-sm">
          <div>
            <p className="mt-1 font-semibold">Slice and dice</p>
            <p>Costs 7 talents, -1 unrest, +1 popularity</p>
          </div>
          <div>
            <p className="mt-1 font-semibold">Blood fest </p>
            <p>Costs 13 talents, -2 unrest, +2 popularity</p>
          </div>
          <div>
            <p className="mt-1 font-semibold">Gladiator gala </p>
            <p>Costs 18 talents, -3 unrest, +3 popularity</p>
          </div>
        </div>
      </>
    )
  }
  if (actionName === "Transfer talents") {
    return (
      <p>
        You can move talents between your senators and faction treasury, or send
        talents to a senator in another faction.
      </p>
    )
  }
  return null
}

export default ActionDescription
