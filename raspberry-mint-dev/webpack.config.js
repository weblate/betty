'use strict'

import {CleanWebpackPlugin} from 'clean-webpack-plugin'
import CopyWebpackPlugin from 'copy-webpack-plugin'
import CssMinimizerPlugin from 'css-minimizer-webpack-plugin'
import HtmlWebpackPlugin from 'html-webpack-plugin'
import MiniCssExtractPlugin from 'mini-css-extract-plugin'
import path from 'path'
import TerserPlugin from 'terser-webpack-plugin'
import url from 'node:url'

const __dirname = url.fileURLToPath(new URL('.', import.meta.url))

const webpackConfiguration = {
    mode: 'development',
    devtool: 'eval-source-map',
    entry: path.join(__dirname, 'src', 'js', 'main.ts'),
    output: {
        path: path.join(__dirname, 'build'),
        filename: 'js/[name].js'
    },
    /* @todo Do not migrate this to the final product! */
    devServer: {
        watchFiles: {
            paths: [
                "./src/**/*"
            ],
        }
    },
    optimization: {
        concatenateModules: true,
        minimize: false,
        minimizer: [
            new CssMinimizerPlugin(),
            new TerserPlugin({
                extractComments: false,
                terserOptions: {
                    output: {
                        comments: false
                    }
                }
            })
        ],
    },
    plugins: [
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin({
            filename: 'css/[name].css'
        }),
        new HtmlWebpackPlugin({template: path.join(__dirname, './src/www/index.html')}),
        new CopyWebpackPlugin({
            patterns: [
                {
                    from: path.join(__dirname, '../betty/assets/public/static/betty-192x192.png'),
                    to: './images/',
                }
            ],
        })

    ],
    module: {
        rules: [
            {
                test: /\.(js|ts)$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'babel-loader',
                        options: {
                            cacheDirectory: path.resolve(__dirname, 'cache'),
                            presets: [
                                [
                                    '@babel/preset-env', {
                                    debug: true,
                                    modules: false,
                                    useBuiltIns: 'usage',
                                    corejs: 3
                                },
                                ],
                                '@babel/preset-typescript',
                            ]
                        }
                    }
                ]
            },
            {
                test: /\.s?css$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            publicPath: '/'
                        }
                    },
                    {
                        loader: 'css-loader',
                        options: {
                            url: {
                                // Betty's own assets are generated through the assets file system,
                                // so we use Webpack for vendor assets only.
                                filter: (url, resourcePath) => resourcePath.includes('/node_modules/'),
                            }
                        }
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: () => [
                                    require('autoprefixer')
                                ]
                            }
                        }
                    },
                    {
                        loader: 'sass-loader',
                        options: {
                            sassOptions: {
                                silenceDeprecations: ["color-functions", "global-builtin", "import", "mixed-decls"]
                            }
                        }
                    }
                ]
            },
            {
                test: /.*\.png|gif|jpg|jpeg|svg/,
                type: 'asset/resource',
                generator: {
                    filename: 'images/[hash][ext]'
                }
            }
        ]
    }
}

export default webpackConfiguration
