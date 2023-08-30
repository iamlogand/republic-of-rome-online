interface TitleData {
  id: number
  senator: number
  name: string
  start_step: number
  end_step: number | null
}

class Title {
  id: number
  senator: number
  name: string
  start_step: number
  end_step: number | null

  constructor(data: TitleData) {
    this.id = data.id
    this.name = data.name
    this.senator = data.senator
    this.start_step = data.start_step
    this.end_step = data.end_step
  }
}

export default Title
