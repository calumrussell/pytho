import {
  select,
} from 'd3-selection';
import {
  scaleLinear, scaleTime,
} from 'd3-scale';
import {
  axisBottom, axisLeft,
} from 'd3-axis';
import {
  extent, max, min,
} from 'd3-array';

export const writeAxis = ( chartState, axis ) => {
  const [
    x,
    y,
  ] = axis;
  const {
    invariants: {
      rootWrapper,
      hasY,
      axisName,
      yAxisMarginAdj,
      size: {
        height,
        margin,
      },
    },
  } = chartState;

  const bottomMargin = yAxisMarginAdj ?
    height - margin.bottom :
    height;

  select(`#${rootWrapper}`)
      .append('g')
      .attr('class', `${axisName}-xaxis`)
      .attr('transform', `translate(0, ${bottomMargin})`)
      .call(axisBottom(x));

  if (hasY) {
    select(`#${rootWrapper}`)
        .append('g')
        .attr('class', `${axisName}-yaxis`)
        .call(axisLeft(y));
  }
};

export const updateAxis = (chartState, xValues, yValues) => {
  const [
    x,
    y,
  ] = chartState.axis;
  const {
    invariants: {
      rootWrapper,
      axisName,
      hasY,
    },
    data: {
      xGetter,
      yGetter,
    },
  } = chartState;

  x.domain(extent(xValues, xGetter));

  const minYVal = min(yValues, (d)=> min(d.map(yGetter)));
  const maxYVal = max(yValues, (d) => max(d.map(yGetter)));
  y.domain([
    minYVal,
    maxYVal,
  ]);

  select(`#${rootWrapper}`)
      .select(`.${axisName}-xaxis`)
      .call(axisBottom(x));

  if (hasY) {
    select(`#${rootWrapper}`)
        .select(`.${axisName}-yaxis`)
        .call(axisLeft(y));
  }
};

export const axisBuilder = (chartState) => {
  const {
    data: {
      x,
      y,
      xGetter,
      yGetter,
    },
    invariants: {
      size: {
        height,
        width,
        margin,
      },
      yAxisMarginAdj,
    },
  } = chartState;

  const bottomMargin = yAxisMarginAdj ?
  height - margin.bottom :
  height;

  const xAxis = scaleTime()
      .domain(extent(x, xGetter))
      .range([
        0,
        width,
      ]);

  const minYVal = min(y, (d)=> min(d.map(yGetter)));
  const maxYVal = max(y, (d) => max(d.map(yGetter)));

  const yAxis = scaleLinear()
      .domain([
        minYVal,
        maxYVal,
      ])
      .range([
        bottomMargin,
        0,
      ]);
  return [
    xAxis,
    yAxis,
  ];
};

