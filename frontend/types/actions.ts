// JSON action data is typed so that it can be used in TypeScript

interface ActionType {
  sentence: string
  title: string
}

export default interface ActionsType {
  [key: string]: ActionType
}
