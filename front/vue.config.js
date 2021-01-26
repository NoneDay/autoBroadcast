const  path = require('path')

function resolve(dir){
    return path.join(__dirname, dir)
}
// 基础路径 注意发布之前要先修改这里
let baseUrl = './'
const port = process.env.port || process.env.npm_config_port || 8080 // dev port
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
module.exports = {
  publicPath: baseUrl, // 根据你的实际情况更改这里
    lintOnSave: false,
    productionSourceMap: false,
    // configureWebpack: config => {
    //     if (process.env.NODE_ENV === 'production') {
    //         return {
    //             plugins: [
    //                 new BundleAnalyzerPlugin()
    //             ]
    //         }
    //     }
    // },
    devServer: {
        port: port,
        //open: true,
        //overlay: {
        //  warnings: false,
        //  errors: true
        //},before: require('./mock/mock-server.js')
        //,
        proxy: { 
            "/aps/report5": {
                target: "http://report.hn.clic/report5",
                changeOrigin: true,//是否允许跨域
                ws: true,
                pathRewrite: {
                    "^/aps/report5": ""
                }
            },
            "/aps": {
                target: "http://127.0.0.1:5050/",
                changeOrigin: true,
                ws: true,
                pathRewrite: {
                    "^/aps": ""
                }
            },

        }
    },
    chainWebpack: (config) => {
        //忽略的打包文件
        config.externals({
            'vue': 'Vue',
            'vue-router': 'VueRouter',
            'vuex': 'Vuex',
            'axios': 'axios',
            'element-ui': 'ELEMENT',
            'CodeMirror':'CodeMirror',
            'vue-grid-layout':'VueGridLayout',
            "xlsx":"xlsx",//很大的一个包
            'monaco-editor':'monaco-editor',
            'echarts':'echarts',
        })


        //const entry = config.entry('app')
        //entry
        //    .add('babel-polyfill')
        //    .end()
        //entry
        //    .add('classlist-polyfill')
        //    .end()
        //entry
        //    .add('@/mock')
        //    .end()
    }
}