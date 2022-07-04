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

  const toPost = () => ({
    'assets': assets.map((i) => parseInt(i.id)),
    'weights': weights.map((i) => parseInt(i)/100),
  })

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
    toPost,
    getLength,
    getCopy,
  };
};
