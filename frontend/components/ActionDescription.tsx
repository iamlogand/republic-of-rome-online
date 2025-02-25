const factionLeaderDescription = (
  <p>Your faction leader will be immune from persuasion attempts.</p>
)

const actionDescriptionRegistry = {
  "Attract knight": (
    <p>
      A senator may spend talents to attempt to attract a knight. Each knight
      a senator controls increases their personal revenue and votes by +1.
    </p>
  ),
  "Change faction leader": factionLeaderDescription,
  Contribute: (
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
  ),
  "Select faction leader": factionLeaderDescription,
  "Sponsor games": (
    <>
      <p>
        Senators may spend talents to sponsor games. These games lower
        Rome&apos;s unrest and increase the sponsor&apos;s popularity.
      </p>
      <div className="text-sm flex flex-col gap-2">
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
  ),
  "Transfer talents": (
    <>
      <p>
        You can move talents between your senators and faction treasury, or send
        talents to a senator in another faction.
      </p>
    </>
  ),
}

interface ActionDescriptionProps {
  actionName: string
}

const ActionDescription = ({ actionName }: ActionDescriptionProps) => {
  if (actionName in actionDescriptionRegistry) {
    return actionDescriptionRegistry[
      actionName as keyof typeof actionDescriptionRegistry
    ]
  } else {
    return null
  }
}

export default ActionDescription
