interface TitleData {
  id: number
  senator: number
  name: string
  start_step: number
  end_step: number | null
  major_office: boolean
}

class Title {
  id: number
  senator: number
  name: string
  start_step: number
  end_step: number | null
  major_office: boolean

  constructor(data: TitleData) {
    this.id = data.id
    this.name = data.name
    this.senator = data.senator
    this.start_step = data.start_step
    this.end_step = data.end_step
    this.major_office = data.major_office
  }
}

export default Title
