export interface Region {
  name: string
  svg: string
}

export const REGIONS: Record<string, Region> = {
  "gallia-cisalpina": {
    name: "Gallia Cisalpina",
    svg: "gallia-cisalpina.svg",
  },
  italia: {
    name: "Italia",
    svg: "italia.svg",
  },
  sicilia: {
    name: "Sicilia",
    svg: "sicilia.svg",
  },
  "corsica-et-sardinia": {
    name: "Corsica et Sardinia",
    svg: "corsica-et-sardinia.svg",
  },
}
