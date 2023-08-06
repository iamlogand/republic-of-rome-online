interface Identifiable {
  id: string;
  [key: string]: any;
}

class Collection<T extends Identifiable> {
  byId: { [key: string]: T };
  allIds: string[];

  constructor(instances: T[] = []) {
    this.byId = {};
    this.allIds = [];

    for (let instance of instances) {
      this.add(instance);
    }
  }

  add(instance: T) {
    this.byId[instance.id] = instance;
    this.allIds.push(instance.id);
  }

  remove(id: string) {
    delete this.byId[id];
    this.allIds = this.allIds.filter(instanceId => instanceId !== id);
  }

  update(instance: T) {
    this.byId[instance.id] = instance;
  }

  get asArray(): T[] {
    return this.allIds.map(id => this.byId[id]);
  }
}

export default Collection;
