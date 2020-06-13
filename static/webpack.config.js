const webpack = require('webpack');
const path = require('path');
const CompressionPlugin = require('compression-webpack-plugin');

const config = {
   devtool: 'eval-source-map',
   entry: __dirname + '/js/index.jsx',
   output: {
      path: path.resolve('../public/'),
      publicPath: 'public/',
      filename: 'bundle.js',
      chunkFilename: '[name].chunk.js'
   },
   resolve: {
      extensions: ['.js', '.jsx', '.css']
   },
   module: {
      rules: [
         {
            test: /\.jsx?$/,
            loader: 'babel-loader',
            exclude: /node_modules/,
         },{
            test: /\.css$/,
            use: ['style-loader', 'css-loader']
         },{
            test: /\.svg$/,
            use: ['react-svg-loader']
         }
      ]
   },
   plugins: [
      new CompressionPlugin({
         filename: '[path].gz[query]',
         algorithm: 'gzip',
         test: /\.js$/,
         threshold: 10240,
         minRatio: 0.8
      })
   ]
};

module.exports = config;
