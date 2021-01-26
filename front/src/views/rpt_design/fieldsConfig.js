import {deepClone} from "./utils/util"

export const widget_row_col_layout=function(item){
  let column=[]
  if(item)
    column.push(item)
  return{
    type:"layout_row_col"  ,
    label: 'row_col布局',span: 24,
    icon: 'icon-group',
    display: true,style:{height:'100%'},
    component:'widget-form-group',
    prop:"_random_",
    children: {
      column: column
    }
  }
}
export const widget_div_layout=function(item){
  let column=[]
  if(item)
    column.push(item)
  return {
    type:"layout_div" , 
    label: 'div布局',span: 24,
    icon: 'icon-group',
    display: true,style:{height:'100%'},
    component:'widget-form-group',
    prop:"_random_",
    children: {
      column: column
    }
  }
}
function default_chart(chart_name,series_type,chart_option=`{
  legend: {},
  tooltip: {},
  dataset: {
      // 提供一份数据。valid_data为自动生成，如果全自定义，就不要使用
      source: valid_data
  },
  grid:{left :30,right:10,top:10,bottom:30},
  // 声明一个 X 轴，类目轴（category）。默认情况下，类目轴对应到 dataset 第一列。
  yAxis: {},
  // 声明一个 Y 轴，数值轴。
  xAxis: {type: 'category',"axisLabel": {
    "margin": 8,
    "interval":0,//解决代码
    "textStyle": {
        "color": "#676767"
    }}},
  // 声明多个 bar 系列，默认情况下，每个系列会自动对应到 dataset 的每一列。
    series:series_type
}`){
  return  {
    "type":"echart",'label':chart_name,gridName:"_random_",icon: 
      'icon-table','color':'#fff',display: true,
      'component':'echarts',style:{height:'100%'}, 
      "series_type":series_type,
      
        fields:[{key:'product',label:'product',selected:true,type: 'bar'},
            {key:'2015',label:'2015年',selected:true,type: 'bar'},
            {key:'2016',label:'2016年',selected:true,type: 'bar'},
            {key:'2017',label:'2017年',selected:true,type: 'bar'}
          ],
        datasource:'示例',fresh_ds:[],fresh_params:[],
        data:[
            ['product', '2015', '2016', '2017'],
            ['Matcha Latte', 43.3, 85.8, 93.7],
            ['Milk Tea', 83.1, 73.4, 55.1],
            ['Cheese Cocoa', 86.4, 65.2, 82.5],
            ['Walnut Brownie', 72.4, 53.9, 39.1]
        ]
        ,content:`option = `+chart_option
      
    }     
}
export default [
    {
        title: '布局字段',
        list: [widget_row_col_layout(),
            widget_div_layout(),       
        {
          type: 'tabs',
          label: 'tab面板',
          icon: 'icon-table',
          span: 24,
          display: true,style:{height:'100%'},
          component:'widget-form-tabs',
          children: {
            align: 'center',
            headerAlign: 'center',
            column: [widget_div_layout()
            ]
          }
        }  
      ]
    },
    { title: '元素',
        list: [ 
            {"type":"test_blue_div",'label':'blue测试div组件',icon: 'icon-table','color':'#fff',display: true, 'component':'testdiv'},
            {"type":"dync-template",'label':'动态模板',icon: 'icon-table','color':'#fff',display: true, 
            'content':`
        <div>
        <div>Hello {{ name }}!</div>
        <button @click="sayHi">Say Hi!</button>
      </div>`,
            'component':'dync-template'},

            {type:"ele-grid",'label':'ele_grid',icon: 'icon-table','color':'#fff',display: true, 
            pageSize:20,
            gridName:'_random_',
           datasource:"示例",fresh_ds:[],fresh_params:[],
            fields:[{key:'product',label:'product',selected:true,type: 'bar'},
            {key:'2015',label:'2015年',selected:true,type: 'bar'},
            {key:'2016',label:'2016年',selected:true,type: 'bar'},
            {key:'2017',label:'2017年',selected:true,type: 'bar'}
          ],style:{height:'100%'},
            content:`<div style="width:100%;height:100%" v-if="tableData.length>0"> 
            <el-table stripe border height="calc(100% - 28px)"  @cell-click="cell_click"
              :data="tableData.slice((currentPage - 1) * self.pageSize, currentPage*self.pageSize)" 
            >
                <el-table-column v-for="(one,idx) in Object.keys(tableData[0])"  sortable
                  :key="one+idx" :prop="one" :label="one"> 
                </el-table-column>
            </el-table>
            <el-pagination  
                :current-page.sync="currentPage"
                :page-sizes="[2, 5, 10, 20]"
                :page-size.sync="self.pageSize" 
                layout="total, sizes, prev, pager, next, jumper"
                :total.sync="tableData.length">
            </el-pagination>
            </div> `
        ,
            'component':'ele-grid'},

            {"type":"luckySheetProxy",'label':'自由格式报表',icon: 'icon-table',display: true,style:{height:'100%'},
              gridName:"_random_",span: 24,'component':'luckySheetProxy'},
              

            {"type":"html-text",'label':'html-text',gridName:"_random_",icon: 'icon-table','color':'#fff',display: true, 'component':'html-text',style:{height:'100px'},
                'content':"<h1>哈==哈哈</h1>"},              
            ]
    },
    { title: '图',
    list: [
          default_chart('柱状图','{"type":"bar"}') ,
          default_chart('极坐标堆叠图',
            '{"type": "bar", "coordinateSystem": "polar","stack": "a"}'
            ,`{
              legend: {},
              tooltip: {},
              "polar": {},"angleAxis":{},
              dataset: {
                  // 提供一份数据。valid_data为自动生成，如果全自定义，就不要使用
                  source: valid_data
              },
              // 声明一个 X 轴，类目轴（category）。默认情况下，类目轴对应到 dataset 第一列。
              
              // 声明一个 Y 轴，数值轴。
              radiusAxis: {type: 'category'},
              // 声明多个 bar 系列，默认情况下，每个系列会自动对应到 dataset 的每一列。
                series:series_type
            }`            
            ) ,
          default_chart('堆叠图','{"type": "bar", "stack": "one"}') ,
          default_chart('面积图','{"type":"line","stack":"z","areaStyle": {}}') ,
          default_chart('line_symbol',`{
            "type": "line",
            "smooth": true,
            "showAllSymbol": true,
            "symbol": "emptyCircle",
            "symbolSize": 15
        }`) ,
          default_chart('线型图','{"type":"line"}') ,
          default_chart('多饼图','{"type":"pie"}',`{
            legend: {},
            tooltip: {},
             
            dataset: {
                // 提供一份数据。valid_data为自动生成，如果全自定义，就不要使用
                source: valid_data
            }, 
              series:series_type
          }`) ,
          default_chart('上饼下线','{"type": "line", "smooth": true, "seriesLayoutBy": "row"}',
          `{
            legend: {},
            tooltip: {
              trigger: 'axis',
              showContent: false
          },
            xAxis: {type: 'category'},
            yAxis: {gridIndex: 0},
            grid: {top: '55%'}, 
            dataset: {
                // 提供一份数据。valid_data为自动生成，如果全自定义，就不要使用
                source: valid_data
            }, 
              series:series_type.concat([{
                type: 'pie',
                id: 'pie',
                radius: '30%',
                center: ['50%', '25%'],
                label: {
                    formatter: '{b}: {@2012} ({d}%)'
                },
                encode: {
                    itemName: valid_data[0][0],
                    value: valid_data[0][1],
                    tooltip: valid_data[0][1]
                }
            }])
          }
          myChart.on('updateAxisPointer', function (event) {
            var xAxisInfo = event.axesInfo[0];
            if (xAxisInfo) {
                var dimension = xAxisInfo.value + 1;
                myChart.setOption({
                    series: {
                        id: 'pie',
                        label: {
                            formatter: '{b}: {@[' + dimension + ']} ({d}%)'
                        },
                        encode: {
                            value: dimension,
                            tooltip: dimension
                        }
                    }
                });
            }
        });
          `) ,
          
          default_chart('仪表盘', '{"type": "gauge"}'),
          default_chart('漏斗图', `{"type": "funnel"}`,`{
            legend: {},
            tooltip: {},
            dataset: {
                // 提供一份数据。valid_data为自动生成，如果全自定义，就不要使用
                source: valid_data
            },
            grid:{left :30,right:10,top:10,bottom:30},
            // 声明一个 X 轴，类目轴（category）。默认情况下，类目轴对应到 dataset 第一列。
            yAxis: {},
            // 声明一个 Y 轴，数值轴。
            xAxis: {type: 'category' },
            // 声明多个 bar 系列，默认情况下，每个系列会自动对应到 dataset 的每一列。
              series:series_type
          }`),     
          
        ]
      }
]
  