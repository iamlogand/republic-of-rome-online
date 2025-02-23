const actionDescriptionRegistry = {
  Contribute: (
    <>
      <p>Contribute talents to the State treasury</p>
      <div className="text-sm">
        <p>10 talents = 1 influence</p>
        <p>25 talents = 3 influence</p>
        <p>50 talents = 7 influence</p>
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
