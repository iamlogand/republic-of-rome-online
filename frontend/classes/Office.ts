interface OfficeData {
  id: number
  senator: number
  name: string
  start_step: number
  end_step: number | null
}

class Office {
  id: number
  senator: number
  name: string
  start_step: number
  end_step: number | null

  constructor(data: OfficeData) {
    this.id = data.id
    this.name = data.name
    this.senator = data.senator
    this.start_step = data.start_step
    this.end_step = data.end_step
  }
}

export default Office
