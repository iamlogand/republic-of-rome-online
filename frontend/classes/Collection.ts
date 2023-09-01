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
      this.add(instance)
    }
  }

  add(instance: T) {
    this.byId[instance.id] = instance
    this.allIds.push(instance.id)
    return this
  }

  remove(id: number) {
    delete this.byId[id]
    this.allIds = this.allIds.filter(instanceId => instanceId !== id)
    const newInstances = this.allIds.map(instanceId => this.byId[instanceId])
    return new Collection(newInstances)
  }

  get asArray(): T[] {
    return this.allIds.map(id => this.byId[id])
  }
}

export default Collection
