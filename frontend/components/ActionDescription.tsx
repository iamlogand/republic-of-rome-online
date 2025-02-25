const actionDescriptionRegistry = {
  Contribute: (
    <>
      <p>Contribute talents to the State treasury.</p>
      <div className="text-sm">
        <p>10 talents = 1 influence</p>
        <p>25 talents = 3 influence</p>
        <p>50 talents = 7 influence</p>
      </div>
    </>
  ),
  "Sponsor games": (
    <>
      <p>
        A senator can spend talents to sponsor games. These games lower unrest
        and increase the sponsor&apos;s popularity.
      </p>
      <div className="text-sm flex flex-col gap-2">
        <p></p>
        <div>
          <p className="mt-1 font-semibold">Slice and dice costs 7 talents</p>
          <p>-1 unrest, +1 popularity</p>
        </div>
        <div>
          <p className="mt-1 font-semibold">Blood fest costs 13 talents</p>
          <p>-2 unrest, +2 popularity</p>
        </div>
        <div>
          <p className="mt-1 font-semibold">Gladiator gala costs 18 talents</p>
          <p>-3 unrest, +3 popularity</p>
        </div>
      </div>
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
