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

export const axisBuilder = (baseComponents, constants, name) => () => {
  const tParser = constants.tParser;
  const {
    size,
    yAxisMarginAdj,
  } = baseComponents.config;
  const {
    height,
    width,
    margin,
  } = size;
  const {
    data,
  } = constants;

  const bottomMargin = yAxisMarginAdj ?
  height - margin.bottom :
  height;

  const x = scaleTime()
      .domain(extent(data, (d) => tParser(d.date)))
      .range([
        0, width,
      ]);

  const y = scaleLinear()
      .domain([
        min(data, (d) => d.close), max(data, (d) => d.close),
      ])
      .range([
        bottomMargin, 0,
      ]);

  baseComponents.axis = [
    x, y,
  ];
  baseComponents.axisName = name;
};

export const buildAxis = (
    baseComponents,
) => () => {
  const [
    x, y,
  ] = baseComponents.axis;
  const {
    size,
    hasY,
    yAxisMarginAdj,
  } = baseComponents.config;
  const {
    height,
    margin,
  } = size;

  const bottomMargin = yAxisMarginAdj ?
    height - margin.bottom :
    height;

  select(baseComponents.root)
      .append('g')
      .attr('id', `${baseComponents.axisName}-xaxis`)
      .attr('transform', `translate(0, ${bottomMargin})`)
      .call(axisBottom(x));

  if (hasY) {
    select(baseComponents.root)
        .append('g')
        .attr('id', `${baseComponents.axisName}-yaxis`)
        .call(axisLeft(y));
  }
};

export const updateAxis = (baseComponents) => () => {
  const [
    x, y,
  ] = baseComponents.axis;
  const {
    hasY,
  } = baseComponents.config;
  const {
    axisName,
  } = baseComponents;

  select(`#${axisName}-xaxis`)
      .transition()
      .call(axisBottom(x));

  if (hasY) {
    select(`#${axisName}-yaxis`)
        .transition()
        .call(axisLeft(y));
  }
};

