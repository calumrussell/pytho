const path = require('path');
const webpack = require('webpack');
const CompressionPlugin = require('compression-webpack-plugin');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
  devtool: 'source-map',
  entry: {
    app: path.resolve(__dirname, 'src/'),
  },
  output: {
    filename: '[name].js',
    path: __dirname + '/dist',
  },
  plugins: [
    new webpack.EnvironmentPlugin({
      API_URL: 'http://localhost:8000',
      PRODUCTION: true,
    }),
    new CompressionPlugin({
      test: /\.js$|\.css$|/,
    }),
    new webpack.ContextReplacementPlugin(
        /moment[\/\\]locale$/,
        /en/,
    ),
  ],
  module: { rules: [
    {
      test: /\.js$/,
      include: path.resolve(__dirname, 'src'),
      use: [
        'babel-loader',
      ],
    }, {
      test: /\.css$/i,
      use: [
        'style-loader', 'css-loader',
      ],
    },
  ] },
  optimization: {
    minimizer: [new UglifyJsPlugin()],
    usedExports: true,
    splitChunks: { cacheGroups: { vendor: {
      test: /[\\/]node_modules[\\/](react|react-dom|axios)[\\/]/,
      name: 'vendor',
      chunks: 'all',
    } } },
  },
  resolve: { alias: {
    '@Helpers': path.resolve(__dirname, 'src/components/common/helpers.js'),
    '@Common': path.resolve(__dirname, 'src/components/common'),
    '@Style': path.resolve(__dirname, 'src/components/common/style.js'),
    '@Components': path.resolve(__dirname, 'src/components'),
  } },
};
