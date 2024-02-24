// JSON enemy leader data is typed so that it can be used in TypeScript

interface EnemyLeaderData {
  title: string
  location: string
  new_description: string
}

export default interface EnemyLeaderDataCollection {
  [key: string]: EnemyLeaderData
}
