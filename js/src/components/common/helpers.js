
const roundNumber = (n) => Math.round(n * 100) / 100;
export const strConverterMult = (scalar) => roundNumber(scalar*100).toFixed(2);
export const strConverter = (scalar) => roundNumber(scalar).toFixed(2);
export const annualiseDailyRet = (daily) => Math.pow(1+(daily/100), 252)-1;
export const annualiseMonthlyRet = (monthly) => Math.pow(1+(monthly/100), 12)-1;
export const getCssVar = (name) =>
  getComputedStyle(document.documentElement)
      .getPropertyValue(name);
