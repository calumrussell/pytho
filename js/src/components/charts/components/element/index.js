import {
  select,
} from 'd3-selection';
import {
  line,
} from 'd3-shape';

export const writeLine = (chartState, line) => {
  const {
    invariants: {
      rootWrapper,
      colours,
    },
    data: {
      y,
    },
  } = chartState;

  select(`#${rootWrapper}`)
      .append('g')
      .attr('class', 'chart-lines')
      .selectAll('path')
      .data(y)
      .join('path')
      .attr('class', 'chart-line')
      .attr('fill', 'none')
      .attr('stroke', (d, i) => colours[i%colours.length])
      .attr('stroke-width', 1.5)
      .attr('d', line);
};

export const updateLine = (chartState, xValues, yValues) => {
  const {
    invariants: {
      rootWrapper,
    },
    data: {
      xGetter,
      yGetter,
    },
    axis,
  } = chartState;

  const [
    x,
    y,
  ] = axis;

  const newLine = line()
      .x((d, i)=> x(xGetter(xValues[i])))
      .y((d) => y(yGetter(d)));

  select(`#${rootWrapper}`)
      .selectAll('.chart-line')
      .data(yValues)
      .attr('d', newLine);

  return newLine;
};

export const lineBuilder = (chartState, axis) => {
  const {
    xGetter,
    yGetter,
    x: xValues,
  } = chartState.data;
  const [
    x,
    y,
  ] = axis;

  return line()
      .x((d, i)=> x(xGetter(xValues[i])))
      .y((d) => y(yGetter(d)));
};
