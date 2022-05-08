import React from 'react';
import PropTypes from 'prop-types';

import {
  Text,
} from '@Common';

export const Table = ({
  fundamentals,
}) => {
  const annualFinancials = fundamentals['Income_Statement']['yearly'];
  const revenues = Object.keys(annualFinancials).map((date) => {
    const row = annualFinancials[date];
    if (row['totalRevenue'] != null) {
      return [
        row['date'],
        row['totalRevenue']/1000000,
      ];
    }
  }).filter(Boolean);

  const tableStyle = {
    display: 'block',
    overflowX: 'auto',
    whiteSpace: 'nowrap',
  };

  const firstColOverlayStyle = {
    left: '-1px',
    position: 'absolute',
    top: '0',
    zIndex: '90',
  };

  const firstColWidth = {
    minWidth: '140px',
    width: '140px',
    paddingRight: '0.5rem',
    display: 'flex',
    justifyContent: 'flex-end',
    backgroundColor: 'var(--default-background-color)',
  };

  return (
    <div
      style={
        {
          display: 'block',
          position: 'relative',
        }
      }>
      <div>
        <table
          style={ tableStyle }>
          <tr>
            <th
              style={ firstColWidth }>
              <Text>
                Date
              </Text>
            </th>
            {
              revenues.map((d, i) => (
                <th
                  key={ i }>
                  <Text>
                    {d[0]}
                  </Text>
                </th>))
            }
          </tr>
          <tr>
            <td
              style={ firstColWidth }>
              <Text>
                Revenue
              </Text>
            </td>
            {
              revenues.map((r, i) => (
                <td
                  key={ i }>
                  <Text>
                    {r[1]}
                  </Text>
                </td>))
            }
          </tr>
        </table>
      </div>
      <div
        style={ firstColOverlayStyle }>
        <table>
          <tr>
            <th
              style={ firstColWidth }>
              <Text>
                Date
              </Text>
            </th>
          </tr>
          <tr>
            <td
              style={ firstColWidth }>
              <Text>
                Revenue
              </Text>
            </td>
          </tr>
        </table>
      </div>
    </div>
  );
};

Table.propTypes = {
  fundamentals: PropTypes.object.shape({
    Income_Statement: PropTypes.object.shape({
      yearly: PropTypes.object.shape({
        totalRevenue: PropTypes.number.isRequired,
        date: PropTypes.number.isRequired,
      }),
    }).isRequired,
  }).isRequired,
};
