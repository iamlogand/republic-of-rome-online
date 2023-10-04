interface Identifiable {
  id: number
  [key: string]: any
}

class Collection<T extends Identifiable> {
  byId: { [key: number]: T }
  allIds: number[]

  constructor(instances: T[] = []) {
    this.byId = {}
    this.allIds = []

    for (let instance of instances) {
      this.byId[instance.id] = instance
      this.allIds.push(instance.id)
    }
  }

  add(instance: T) {
    // Perform the mutation
    this.byId[instance.id] = instance
    this.allIds.push(instance.id)

    // Create a new collection to force re-render
    return new Collection(this.asArray)
  }

  remove(id: number) {
    // Perform the mutation
    delete this.byId[id]
    this.allIds = this.allIds.filter((instanceId) => instanceId !== id)

    // Return new collection to force re-render
    return new Collection(this.asArray)
  }

  get asArray(): T[] {
    return this.allIds.map((id) => this.byId[id])
  }
}

export default Collection
