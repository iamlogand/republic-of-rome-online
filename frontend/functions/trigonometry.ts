export const getXOffset = (angle: number, radius: number) => {
  return Math.sin((-(angle + 180) * Math.PI) / 180) * radius
}

export const getYOffset = (angle: number, radius: number) => {
  return Math.cos((-(angle + 180) * Math.PI) / 180) * radius
}
