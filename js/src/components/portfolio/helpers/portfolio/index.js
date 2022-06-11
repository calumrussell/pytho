import zip from 'lodash.zip';

export const weightedPortfolio = () => {
  let assets = [
  ];
  let weights = [
  ];

  const getLength = () => assets.length;

  const getCopy = () => {
    const ws = weightedPortfolio();
    const copyAssets = [
      ...assets,
    ];
    const copyWeights = [
      ...weights,
    ];
    const transpose = zip(copyAssets, copyWeights);
    transpose.map((v) => ws.addAsset(...v));
    return ws;
  };

  const getPortfolio = () => ({
    assets,
    weights,
  });
  const addAsset = (asset, weight) => {
    weights = [
      ...weights,
      weight,
    ];
    assets = [
      ...assets,
      asset,
    ];
  };
  const removeAsset = (idx) => {
    assets.splice(idx, 1);
    weights.splice(idx, 1);
  };

  return {
    getPortfolio,
    addAsset,
    removeAsset,
    getLength,
    getCopy,
  };
};

export const sharePortfolio = () => {
  let assets = [
  ];
  let shares = [
  ];

  const getPortfolio = () => {
    assets, shares;
  };
  const addShares = (holding) => {
    shares = [
      ...shares,
      holding,
    ];
  };
  const addAsset = (asset) => {
    assets = [
      ...obj.assets,
      asset,
    ];
  };
  const removeAsset = (idx) => {
    assets.splice(idx, 1);
    shares.splice(idx, 1);
  };

  return {
    getPortfolio,
    addShares,
    addAsset,
    removeAsset,
  };
};
