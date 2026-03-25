const STATESMAN_NAMES: Record<string, string> = {
  "1a": "P. Cornelius Scipio Africanus",
  "2a": "Q. Fabius Maximus Verrucosus Cunctator",
  "18a": "T. Quinctius Flamininus",
  "19a": "L. Aemilius Paullus Macedonicus",
  "22a": "M. Porcius Cato the Elder",
  "1b": "P. Cornelius Scipio Aemilianus Africanus",
  "1c": "L. Cornelius Sulla",
  "7a": "M. Fulvius Flaccus",
  "21a": "C. Servilius Glaucia",
  "23a": "P. Popillius Laenas",
  "25a": "T. Sempronius Gracchus",
  "25b": "C. Sempronius Gracchus",
  "27a": "C. Marius",
  "4a": "C. Julius Caesar",
  "22b": "M. Porcius Cato the Younger",
  "28a": "M. Tullius Cicero",
  "29a": "M. Licinius Crassus",
  "29b": "L. Licinius Lucullus",
  "30a": "Cn. Pompeius Magnus",
}

export const cardLabel = (card: string): string => {
  if (card.startsWith("statesman:")) {
    const code = card.split(":")[1]
    return STATESMAN_NAMES[code]
  }
  if (card.includes(":")) {
    return card.split(":")[1]
  }
  return card
}
