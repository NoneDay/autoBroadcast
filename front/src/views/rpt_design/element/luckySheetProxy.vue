<template>
  <div :style="{width:'100%',height:height||'100%'}">
    <div v-if="context.isPreview && useHtml && gridType=='common'" v-html="html_table" ref="htmTalbe"></div>
    <div v-else-if="context.isPreview && useHtml && gridType=='large'" 
    :style="{width:'100%',height:'100%'}"
    v-html="self.content"></div>
    <iframe v-else ref='iframe' style="width:100%;height:100%"></iframe>
  </div>
</template>

<script>
import {designGrid2LuckySheet,loadFile,resultGrid2LuckySheet,
      resultGrid2HtmlTable,output_largeGrid    } from '../utils/util.js'
import mixins from "./mixins"
export default {
 name: "luckySheetProxy",
  mixins:[mixins],
  components: {},
  props: {gridName:String,height:String},
  data(){
    return {
      _window:{},
      useHtml:true,
      html_table:"",
      scriptArr:[],
      gridType:"common",
      delayShowType:"none" // or block
    }
  },
  computed:{
  },
  watch: {
    //"context.report":function(){this.buildDisplayData() },
    gridName(newVal,oldVal){
      let grid=this.context.report.AllGrids.grid.find(a=>a._name==oldVal)
      this._window.gridName=newVal
      this.self.gridName=newVal
      if(grid)
        grid._name=newVal
    }
  },
  created(){
    //let script = document.createElement('script'); 
    //this.scriptArr.push(script);
    //script.type ='text/javascript'; 
    //script.text = `${this.self.gridName}grid_sort(){}`
    //document.head.appendChild(script)    

  },
  mounted(){
    this.self.gridName=this.gridName
    this.buildDisplayData()
  },
  beforeDestroy(){
    this.scriptArr.forEach(ele=>{
        ele.remove()
    });
    this.$refs.htmTalbe?.querySelector(`#reportDiv${this.gridName}`)?.removeEventListener('scroll',this.scrollFunc)
    if(this.context.isPreview)
        return
      let grid= this.context.report.AllGrids.grid.find(a=>a._name==this.gridName)
      if(this.self.isDelete){
        if(grid!=undefined)
          this.context.report.AllGrids.grid.splice(this.context.report.AllGrids.grid.indexOf(grid), 1) 
        if(this.context.report_result)
          delete this.context.report_result.data[this.gridName]
        return
      }  
  },
  methods:{
    my_click(){
      console.info('my_click');
    },
    scrollFunc (evt){
      this.$refs.htmTalbe.querySelector(`#reportDiv${this.gridName}Top`).scrollLeft=(evt.currentTarget.scrollLeft);
      this.$refs.htmTalbe.querySelector(`#reportDiv${this.gridName}Left`).scrollTop=(evt.currentTarget.scrollTop);
    },
    sortFunc(evt){
              this.grid_sort_action(evt.currentTarget.dataset['c'])
    }, 
    grid_sort_action(sort_col){
      let _this=this
      let cur_grid=_this.context.report_result.data[_this.gridName]
      if(cur_grid){
          this.$refs.htmTalbe?.querySelector(`#reportDiv${this.gridName}`)?.removeEventListener('scroll',this.scrollFunc)
          let sortArr=$(_this.$refs.htmTalbe.querySelectorAll('#reportDivmainTop table .s'))
          if(sortArr.length>0)
            sortArr?.off('click',this.sortFunc)
          this.html_table=resultGrid2HtmlTable(cur_grid,sort_col)
          this.$nextTick(x=>{
            $(_this.$refs.htmTalbe.querySelectorAll('#reportDivmainTop table .s')).on('click',_this.sortFunc)            
            _this.$refs.htmTalbe.querySelector(`#reportDiv${_this.gridName}`)?.addEventListener('scroll',_this.scrollFunc)
          })
      }
    },
    buildDisplayData()
    {
      let _this=this

      if(_this.context.isPreview && this.useHtml){
        this.gridType=this.context.report_result.data[_this.gridName].type
        if(this.gridType=='common')
           this.grid_sort_action(this.self.sort_col)
        else{//large
          output_largeGrid(this,this.context.report_result.data[_this.gridName]) 
        }
        return
      }

      let iDocumnet=this.$refs.iframe?.contentDocument
      this._window=this.$refs.iframe?.contentWindow.window  
      //_window.luckysheet=luckysheet
      //_window.jQuery=jQuery
      //_window.$=$
      
      
      let  iframe_html=`<html lang="zh-CN" style="overflow-x: hidden;overflow-y: hidden;"><head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
                  
            <link rel="stylesheet" type="text/css" href="cdn/luckysheet/plugins/css/pluginsCss.css" />
                <link rel="stylesheet" type="text/css" href="cdn/luckysheet/plugins/plugins.css" />
                <link rel="stylesheet" type="text/css" href="cdn/luckysheet/css/luckysheet.css" />
                <link rel="stylesheet" type="text/css" href="cdn/luckysheet/assets/iconfont/iconfont.css" />
              <link rel='stylesheet' href='cdn/luckysheet/plugins/css/pluginsCss.css' />
              <link rel='stylesheet' href='cdn/luckysheet/plugins/plugins.css' />
              <link rel='stylesheet' href='cdn/luckysheet/css/luckysheet.css' />
              <link rel='stylesheet' href='cdn/luckysheet/assets/iconfont/iconfont.css' />
               <style>    .my-options{  cursor: pointer;      position: absolute;      z-index: 20;    }
                    .my-sort-options { color: #897bff;    border-radius: 3px; top: 3px;    
                            margin-left: 0;    display: none;    font-size: 12px;    height: 15px;    background: transparent;
                    },
                    a{ target:"_parent"}
                     
              </style>
            <head><body><div id='report' style = 'margin:0px;padding:0px;position:absolute;width:100%;height:100%;left: 0px;top: 0px;'></div></body></html>
            `
        iDocumnet.write(iframe_html);
        iDocumnet.close()

        this._window.gridName=_this.gridName
        this._window.selectChange=function(sheet,luckysheet_select_save){ 
          _this.context?.selectChange(sheet,luckysheet_select_save,_this._window)
          }
        
        this._window.lucky_updated=_this.context.updated||function(){ }
        this._window.cellRenderBefore=function(cell,p,sheet,ctx) {
            if(cell?.cr?._extendDirection=='row')
            {
               // 设置线条的颜色
              ctx.strokeStyle = 'red';
              // 设置线条的宽度
              ctx.lineWidth = 1;
              ctx.beginPath();
              ctx.moveTo(p.start_c, p.start_r+2);
              ctx.lineTo(p.end_c, p.start_r+2);
              ctx.stroke();

              let img = new Image();    
              img.src = "img/arrow_1.png";  
              img.onload=function(params) {
                ctx.drawImage(img,p.end_c,p.end_r,20,25);
              }
              //<svg t="1610004191863" class="icon" viewBox="0 0 1000 1000" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1103" width="200" height="200"><path d="M227.986 584.688l257.492 257.492c20.11 20.11 52.709 20.11 72.819 0l257.492-257.492c20.11-20.11 20.11-52.709 0-72.819s-52.709-20.11-72.819 0l-169.585 169.585v-493.664c0-28.453-23.046-51.499-51.499-51.499s-51.499 23.046-51.499 51.499v493.664l-169.585-169.585c-10.042-10.043-23.226-15.089-36.41-15.089s-26.367 5.021-36.41 15.089c-20.11 20.11-20.11 52.709 0 72.819z" p-id="1104" fill="#d81e06"></path></svg>
            }
        }
        let sheet_data;
        if(_this.context.isPreview){
            this._window.selectChange=function(){ } 

            let cur_grid=_this.context.report_result.data[_this.gridName]
            if(cur_grid)
                sheet_data=JSON.stringify(resultGrid2LuckySheet( _this.gridName,  cur_grid))
        }
        else{
          let cur_grid=_this.context.report.AllGrids?.grid?.find(a=>a._name==_this.gridName)
          if(!cur_grid){
            cur_grid={}
            _this.context.report.AllGrids.grid.push({_name: _this.gridName})  
          }
          //this._window.cur_grid=reportGrid2LuckySheet(cur_grid)
          sheet_data=JSON.stringify(designGrid2LuckySheet(cur_grid))
        }
        let append
        if(_this.context.isPreview){
            append= `rowHeaderWidth:0,columnHeaderHeight:0,showtoolbar:false,`
        }
        else{
          append=` showtoolbarConfig:{  
                        undoRedo: false, //撤销重做，注意撤消重做是两个按钮，由这一个配置决定显示还是隐藏
                        paintFormat: false, //格式刷
                        currencyFormat: false, //货币格式
                        percentageFormat: false, //百分比格式
                        numberDecrease: false, // '减少小数位数'
                        numberIncrease: false, // '增加小数位数
                        moreFormats: false, // '更多格式'
                        font: true, // '字体'
                        fontSize: true, // '字号大小'
                        bold: true, // '粗体 (Ctrl+B)'
                        italic: true, // '斜体 (Ctrl+I)'
                        strikethrough: true, // '删除线 (Alt+Shift+5)'
                        textColor: true, // '文本颜色'
                        fillColor: true, // '单元格颜色'
                        border: true, // '边框'
                        mergeCell: true, // '合并单元格'
                        horizontalAlignMode: true, // '水平对齐方式'
                        verticalAlignMode: true, // '垂直对齐方式'
                        textWrapMode: true, // '换行方式'
                        textRotateMode: false, // '文本旋转方式'
                        image:true, // '插入图片'
                        link:false, // '插入链接'
                        chart: false, // '图表'（图标隐藏，但是如果配置了chart插件，右击仍然可以新建图表）
                        postil:  false, //'批注'
                        pivotTable: false,  //'数据透视表'
                        function: false, // '公式'
                        frozenMode: true, // '冻结方式'
                        sortAndFilter: false, // '排序和筛选'
                        conditionalFormat: true, // '条件格式'
                        dataVerification: false, // '数据验证'
                        splitColumn: false, // '分列'
                        screenshot: true, // '截图'
                        findAndReplace: false, // '查找替换'
                      protection:false, // '工作表保护'
                      print:false, // '打印'
                    }`
        }
        let showtoolbar=_this.context.isPreview==1?false:true
        let script = iDocumnet.createElement('script'); 
        script.type ='module'; 
        script.async=false;
        script.text = ` function insertScript(src,callback)
          {
            let script = document.createElement('script'); 
            script.type ='text/javascript'; 
            script.src = src
            document.head.appendChild(script)      
            if(callback!=undefined){
                script.onload = script.onreadystatechange = function() {
                  console.info(src)
                  if (!this.readyState || this.readyState === "loaded" || this.readyState === "complete" ) {
                      callback();
                      script.onload = script.onreadystatechange = null;
                  }// end if
              };// end onload function
            }//end if      
          } 
          function buildReport(){
              luckysheet.create({
                    container: 'report',lang: 'zh',forceCalculation:false,showsheetbar:false,
                    showstatisticBarConfig:{count: false,  view: false,   zoom: false,  },
                    enableAddBackTop:false,enableAddRow:false,sheetFormulaBar:false,
                    showinfobar:false,defaultFontSize:11,
                    data:[${sheet_data}],
                    hook:{rangeSelect:selectChange,                      
                      updated:lucky_updated,
                      cellRenderAfter:cellRenderBefore
                      },
                    ${append}
              })
            }
            insertScript("cdn/luckysheet/plugins/js/plugin.js",function(){insertScript("cdn/luckysheet/luckysheet.umd.js",buildReport)})
          `
        iDocumnet.head.append(script);
    }
  }
}
</script>

<style>

</style>