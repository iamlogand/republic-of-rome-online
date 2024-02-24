// JSON action data is typed so that it can be used in TypeScript

interface ActionData {
  sentence: string
  title: string
}

export default interface ActionDataCollection {
  [key: string]: ActionData
}
