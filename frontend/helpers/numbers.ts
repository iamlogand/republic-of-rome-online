export const formatSigned = (n: number): string =>
  n < 0 ? `−${Math.abs(n)}` : String(n)
