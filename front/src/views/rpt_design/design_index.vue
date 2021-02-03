<template>
  <div  style="height:calc(100% - 30px); border: 1px solid #eee" class="report_define">
    <ExprEditorDialog  :visible.sync="ExprEditorDialog_visible"
      :target_obj="action_target"
      :prop="action_name" 
      :report="report">
    </ExprEditorDialog>
    <el-dialog v-draggable v-if="preview_dialogVisible" style="text-align: left;" class="report_define"
        :visible.sync="preview_dialogVisible" :title="'预览'" 
            :close-on-click-modal="false"   :fullscreen="true"
              direction="btt" append-to-body  
        > 
        <preview />
    </el-dialog>    
    <datasetManger2 v-if="datamanger_dialogVisible"  :visible.sync="datamanger_dialogVisible"  > 
    </datasetManger2>  

    <el-drawer :width="leftWidth" title="参数管理" :visible.sync="paramMangerDrawerVisible" :modal="false"> 
        <paramManger :report="report" />          
    </el-drawer>

    <el-container class="form-designer">
     
      <el-container style="height: 100%; border: 1px solid #eee">
          <el-header class="widget-container-header"  >
            
            <el-button @click="change_layout" style="float: right; ">切换布局{{formType }}</el-button>
            
            <el-button @click="gridLayoutAddItem(null)" type="success" v-if="formType=='gridLayout'" >
              增加一个GRID元素
            </el-button>
            <el-button @click="save_report" >保存</el-button>
            <el-button @click="preview_run" >预览</el-button>

            <el-button @click="paramMangerDrawerVisible=true" >参数管理</el-button>
            <el-button @click="datamanger_dialogVisible=true" >数据管理</el-button>
            <el-button v-if="canDraggable==false" @click="canDraggable=true" >启用编辑</el-button>
            <el-button v-if="canDraggable==true" @click="canDraggable=false" >关闭编辑</el-button>
           
          </el-header>
          <!-- 中间主布局 -->
          <el-main  class="widget-container" :style="{background: formIsEmpty ? `url(${widgetEmpty}) no-repeat 50%`: ''}"
          v-if="widgetForm!=null"
          >
               <grid-layout-form v-if="formType=='gridLayout'" 
               :layout="widgetForm" 
               :select.sync="selectWidget"
                
                @change="handleHistoryChange(widgetForm)"
                >
              </grid-layout-form>          
              <widget-form v-else  ref="widgetForm"
                          :data="widgetForm" 
                          :select.sync="selectWidget"
                          
                          @change="handleHistoryChange(widgetForm)"
                          ></widget-form>
            </el-main>
      </el-container>
      <!-- 右侧配置 -->
      <el-aside class="widget-config-container" :width="rightWidth"> 
        <el-tabs type="border-card">
        <el-tab-pane label="属性" >
                <ul v-if="cur_select_type=='cell'" ghost-class="ghost" style="padding-left: 10px;">
                  <li  style="display: flex;padding-bottom: 10px;" >
                    <el-tag style="color:black" >扩展方向</el-tag>
                    <el-select v-model="cur_cell.cr._extendDirection" placeholder="扩展方向">
                      <el-option label="行" value="row"></el-option>
                      <el-option label="列" value="column"></el-option>
                      <el-option label="无" value="none"></el-option>
                    </el-select>
                  </li>
                  <li v-for="item in [{display:'计算级别',val:'_calcLevel'},{display:'左顶格',val:'_leftHead'},
                            {display:'上顶格',val:'_topHead'},
                            {display:'文字颜色',val:'_color'},
                            {display:'背景色',val:'_background-color'},
                            {display:'_BOLD',val:'_BOLD'},
                            {display:'链接',val:'_link'},                            
                            {display:'显示值表达式',val:'_displayValueExpr'},
                             {display:'值表达式',val:'_valueExpr'}]"  
                      style="display: flex;padding-bottom: 10px;" :key="item.display" >
                    
                    <el-tag style="color:black;width:100px">{{item.display}}</el-tag>
                    <el-input :placeholder="'请输入内容:'+item.display" v-model="cur_cell.cr[item.val]" :disabled="item.val=='_calcLevel'">
                    </el-input>
                      <el-button  @click="expr_edit(cur_cell.cr,item)" v-if="item.val!='_calcLevel' && item.val!='_leftHead' && item.val!='_topHead'"
                                circle  :type="item.val=='_valueExpr'?'danger': 'success'" size="mini" icon="el-icon-edit"
                                style="padding: 4px;margin-left: 5px;">
                      </el-button>
                  </li>
                </ul>
        <widget-config  v-else 
          :data="selectWidget" 
        ></widget-config>
        </el-tab-pane>
      <el-tab-pane label="工具箱" >
        <div class="fields-list">
          <div v-for="(field, index) in fields" :key="index">
            <div v-if="!field.disabled">
              <div class="field-title">{{field.title}}</div>
              <draggable tag="ul"
                          :list="field.list"
                          :group="{ name: 'form', pull: 'clone', put: false }"
                          ghost-class="ghost"
                          :sort="false">
                <li class="field-label"
                    v-for="(item, index) in field.list"
                    :key="index">
                  <a>
                    <i class="icon iconfont"
                        :class="item.icon"></i>
                    <span>{{item.label}}</span>
                  </a>
                </li>
              </draggable>
            </div>
            <div v-else>
              <div class="field-title">{{field.title}}
                <span class="danger">（开发中）</span>
              </div>
              <ul>
                <li class="field-label-disabled"
                    v-for="(item, index) in field.list"
                    :key="index">
                  <a>
                    <i class="icon iconfont"
                        :class="item.icon"></i>
                    <span>{{item.label}}</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>        
      </el-tab-pane>          
      </el-tabs>  
      
      </el-aside>
    </el-container>
  </div>
</template>

<script>
var color = require('onecolor');
import Draggable from 'vuedraggable'
import paramManger from './paramManger.vue'
import datasetManger2 from './datasetManger2'
import ExprEditorDialog from './ExprEditorDialog.vue'
import widgetEmpty from './assets/widget-empty.png'
import WidgetForm from './WidgetForm'
import WidgetConfig from './WidgetConfig'
import fields from './fieldsConfig.js'
import {widget_div_layout,widget_row_col_layout} from './fieldsConfig.js'
import history from './mixins/history'
import {luckySheet2ReportGrid,loadFile,deepClone,build_layout,get_signalR_connection,getObjType} from './utils/util.js'
import {open_one} from "./api/report_api"
import Preview from './preview.vue'
import Config from './config'
import index_priview from './index_priview'
import x2js from 'x2js' 
const x2jsone=new x2js(); //实例
export default {
  name: "FormDesign",
  mixins: [history],
  components: {paramManger,ExprEditorDialog,Draggable,widgetEmpty,WidgetForm,WidgetConfig,datasetManger2, Preview, },
  
  async beforeRouteEnter(to, from, next) {
    const id = to.query.label || to.meta.id
    if (id) {
      await next(async instance => await instance.init(id))
    } else {
      next(new Error('未指定ID'))
    }
  },
    // 在同一组件对应的多个路由间切换时触发
  beforeRouteUpdate(to, from, next) {
    const id = to.query.label || to.meta.id
    if (id) {
      this.init(id)
      next()
    } else {
      next(new Error('未指定ID'))
    }
  },
  created() {
    Vue.use(Config)
    Vue.use(index_priview)

    this.handleLoadCss();
    //this.init()
  },
  props: {
    options: {
      type: [Object, String],
      default: () => {
        return {
          column: []
        }
      }
    },
    storage: {
      type: Boolean,
      default: false
    },
    asideLeftWidth: {
      type: [String, Number],
      default: '200px'
    },
    asideRightWidth: {
      type: [String, Number],
      default: '310px'
    },
    showGithubStar: {
      type: Boolean,
      default: true
    },
    toolbar: {
      type: Array,
      default: () => {
        return ['import', 'generate', 'preview', 'clear']
      }
    }
  },
  provide() {
    return {
      context:{
        report_result:this.report_result,
        report:this.report,
        canDraggable:this.canDraggable,
        selectChange:this.selectChange,        
        updated:this.lucky_updated,
        design:true,
        clickedEle:this.clickedEle,
        in_exec_url:this.in_exec_url,
        isPreview:false,
        allElementSet:this.allElementSet
      }, 
      fresh_ele:this.fresh_ele,
      clickedEle:this.clickedEle,
    }
  },
  computed: {
    cull_cell_cr(){
      if(this.cur_cell.cr)
        return JSON.parse(JSON.stringify(this.cur_cell.cr))
      else
        return JSON.parse('{ }')
    },
    formIsEmpty(){
      return (this.formType=='gridLayout' && this.widgetForm.length == 0) 
           ||(this.formType!='gridLayout' && this.widgetForm?.children?.column?.length == 0)
    },
    formType(){
      if (Array.isArray(this.widgetForm))
      return 'gridLayout'
      else
      return 'divLayout'
    },
    leftWidth() {
      if (typeof this.asideLeftWidth == 'string') {
        return this.asideLeftWidth
      } else {
        return `${this.asideLeftWidth}px`
      }
    },
    rightWidth() {
      if (typeof this.asideRightWidth == 'string') {
        return this.asideRightWidth
      } else {
        return `${this.asideRightWidth}px`
      }
    }
  },
  data(){
      return {              
        clickedEle:{},//存放点击后的数据，可以被其他元素引用
        report_result:{},//报表运行后的结果
        in_exec_url:{stat:false},//当前是否已经在点击后取数
        preview_dialogVisible:false,
        datamanger_dialogVisible:false,
        paramDialog_visible:false,
        ExprEditorDialog_visible:false,
        fresh_ele:[],//存放点击后更新的元素名称
        allElementSet:new Set(),//所有有ID名称的集合
        paramMangerDrawerVisible:false,
        fieldsDrawerVisible:false,
        action_target:{sql:'',dataSource:'',name:'',type:''},
        action_name:{display:'-',val:'-'},
        cur_cell:{"cr":{"_leftHead":"","_topHead":"","_color":"","_background-color":"",
"_link":"","_BOLD":"","_displayValueExpr":"=@value","_valueExpr":"",
"_calcLevel":"","_FONT-SIZE":"","_text-align":"",}},
        cur_sheet:null,
        sheet_window:null,
        
        can_watch_cell:false,//因为第一次切换单元格后就会执行update cell ，用他来避免首次更新不必要的计算

        cur_select_type:'cell',
        fields,
        widgetEmpty, 
        canDraggable:true,
        selectWidget: {},
        in_cub:false,
        report:{//报表定义内容
              datasources:[],
              dataSets:{dataSet:[]}
              ,params:{param:[]}
              ,AllGrids:{HtmlText:[],grid:[]}
          },
        widgetForm: widget_row_col_layout(),//布局显示
       
      }
  },
  methods:{
    init(report_name){
      let signalR_connection=get_signalR_connection()
      let _this=this
      let _report
      
      //'2019/2jidu/kb_dangri2.cr'
      let isNew=false;
      if(isNew){
        this.report={
                datasources:[{'name':'clicapp'},{'name':'amis'}],
                dataSets:{dataSet:[]}
                ,params:{param:[]}
                ,AllGrids:{HtmlText:[],grid:[{_name:"grid1609810532562",_title:"grid1609810532562" }]}
            }
        this.widgetForm=widget_div_layout({
                  "type": "luckySheetProxy",
                  "label": "自由格式报表",
                  "display": true,
                  "style": {
                      "height": "100%"
                  },
                  "gridName": "grid1609810532562",
                  "span": 24,
                  "component": "luckySheetProxy",
                  "prop": "1609810549191_18237"
              })
        return
      }
      _this.widgetForm=null
      setTimeout(function(){
        open_one(_this,report_name).then(response_data => {      
          if(response_data.errcode)
          {
            _this.$notify({title: '提示',message: response_data.message,type: 'error',duration:0});
            return
          }
          let _report=x2jsone.xml2js(response_data)
          //_report=x2jsone.xml2js(loadFile('kb_dangri2.cr'))
          Object.assign(_this.report,_report.report)
          if(getObjType(_this.report.grid)=='object')
            _this.report.AllGrids.grid=[_this.report.grid]
          if(getObjType(_this.report.AllGrids.grid)=='object')
            _this.report.AllGrids.grid=[_this.report.AllGrids.grid]
          if(getObjType(_this.report.AllGrids.HtmlText)=='object'){
            _this.report.AllGrids.HtmlText=[_this.report.AllGrids.HtmlText]
          }
          if(_this.report.AllGrids.grid==undefined)
            _this.report.AllGrids.grid=[]
          if(_this.report.AllGrids.LargeDataGrid){
              if(getObjType(_this.report.AllGrids.LargeDataGrid) =="object")
              _this.report.AllGrids.grid.push(_this.report.AllGrids.LargeDataGrid)
              else
              _this.report.AllGrids.LargeDataGrid.forEach(ele=>{
                  _this.report.AllGrids.grid.push(ele)
              })
            delete _this.report.AllGrids.LargeDataGrid
          }
          
          if(_this.report.layout)
          _this.widgetForm=JSON.parse(_this.report.layout)
          else{
            _this.widgetForm=build_layout(_this.report.AllGrids)      
          }
            
          if(getObjType(_this.report.dataSets.dataSet)=="object")
            _this.report.dataSets.dataSet=[_this.report.dataSets.dataSet]
          if(getObjType(_this.report.params.param)=="object")
            _this.report.params.param=[_this.report.params.param]

          console.info(_this.report)
          _this.report.dataSets.dataSet.forEach(element => {
              if(element._fields==undefined){
                element._fields="[]"
              }
          });
        }).catch(error=> {
            _this.$notify({title: '提示',message: error.toString(),type: 'error',duration:0});
            if(error.response_data)
              _this.$notify({title: '提示',message: error.response_data,type: 'error',duration:0});          
        })
      })      
    },
    change_layout(){
       if (Array.isArray(this.widgetForm))//gridLayout=>divLayout
       {
          let children=this.widgetForm
          this.widgetForm=widget_div_layout()
          children.forEach(ele=>{
            ele.element.children.column.forEach(one_ele=>{
              one_ele.span=ele.w*2
              this.widgetForm.children.column.push(one_ele)
            })
          });
      }
      else// divLayout=>gridLayout
      {
        let children=this.widgetForm.children.column
        this.widgetForm=[]
        children.forEach(ele=>{
          this.gridLayoutAddItem(ele,ele.span/2,10);
        });
      }
      
    },
    gridLayoutAddItem(item,p_w,p_h){
        let insert_item=widget_div_layout(item)
        let x=0,w=p_w||2,   h=p_h||2,y=0             
        while(true){
            let all_correct=true
            this.widgetForm.forEach(element => {
                if( ((x>= element.x && x< element.x +element.w ) && (y>= element.y && y< element.y +element.h ) ) ||
                    ((element.y>= y && element.y< y +h ) && (element.x>= x && element.x< x +w ) )
                ){
                    all_correct=false
                      return false
                }
            });
              if(all_correct)
                    break;
            x++
            if(x+2>12) //col_num
            {
                x=0
                y++
            }
        }
        let idx=0;
        while(this.widgetForm.find(element => element.i==idx )){
          idx++
        }
        this.widgetForm.push({x,y,w,h,i: idx,element:insert_item });
    },
        // 加载icon
    handleLoadCss() {
      const head = document.getElementsByTagName('head')[0]
      const script = document.createElement('link')
      script.rel = 'stylesheet'
      script.type = 'text/css'
      script.href = 'https://at.alicdn.com/t/font_1254447_zc9iezc230c.css'
      head.appendChild(script)
      // this.loadScript('css', 'https://at.alicdn.com/t/font_1254447_zc9iezc230c.css')
    },
    //-=========================    
  selectChange(sheet,luckysheet_select_save,sheet_window){
        this.cur_select_type='cell'
        this.selectWidget={prop:'--'}
        this.cur_sheet=sheet
        this.sheet_window=sheet_window
        let cur_postion=sheet.luckysheet_select_save[0]
        let cell=sheet.data[cur_postion.row_focus][cur_postion.column_focus]
        this.cur_cell= cell?? {"cr":{"_displayValueExpr":"=@value","_valueExpr":""}}  
        this.can_watch_cell=false//切换单元格后，对cur_cell.cr的第一次监控 ，不需要监控
    },
    
    expr_edit(cur_cell,prop){
        this.action_name=prop
        this.action_target=cur_cell
        this.ExprEditorDialog_visible=true
    },
    lucky_updated(val,from_cull_cell_cr){
// 如果从这里的setCellValue API进入，则不执行，防止递归循环
      if(this.setCellFromAPI){
        return
      }
      let grid= this.report.AllGrids.grid.find(a=>a._name==this.sheet_window.gridName)
      this.setCellFromAPI = true;
      try{
        let _this=this
        if(!grid || !val || !val.range){
          return
        }
        let cacheCells=[]
        let data=this.sheet_window.luckysheet.getSheet(0).data
        val.range?.forEach(one_range=>{
          for(let r=one_range.row[0];r<=one_range.row[1];r++){
            for(let c=one_range.column[0];c<=one_range.column[1];c++){
              let cell=data[r][c]
              if(cell ){
                if(cell.v==undefined && cell.mc)//不处理合并单元格
                  continue
                if(!cell.cr) cell.cr={}
                if(cell.bg && !cell.cr['_background-color']?.startsWith("=") && !from_cull_cell_cr) 
                  cell.cr["_background-color"]=cell.bg
                if(cell.fc && !cell.cr['_color']?.startsWith("=") && !from_cull_cell_cr) 
                  cell.cr['_color']=cell.fc

                if(cell.fs) cell.cr['_FONT-SIZE']=cell.fs
                //cell.cr['_FONT']=4
                if(cell.bl!=undefined) cell.cr['_BOLD']=(cell?.bl==1?"True":"False")
                cell.cr['_text-align']=(cell.ht==0?"center":(cell.ht==1?"left":'right'))
                if(cell.it!=undefined) cell.cr['ITALIC']=cell.it==1 ?"True" :"False"
                if(cell.v&& cell.v.startsWith("#") && cell.f.startsWith("="))
                  cell.cr._valueExpr=cell.v=cell.f
                else
                  cell.cr._valueExpr=cell.v??""
                // 重新设置单元格参数
                let cellCopy=JSON.parse(JSON.stringify(cell))  //$.extend(true,{},cell)
                cacheCells.push({r,c,cellCopy})
              }
            }
          }
        })
        cacheCells.forEach(one=>{
          this.sheet_window.luckysheet.setCellValue(one.r,one.c,one.cellCopy);  
        })
        if(cacheCells.length>0){
          this.can_watch_cell=false//切换单元格后，对cur_cell.cr的第一次监控 ，不需要监控
          this.cur_cell=cacheCells[0].cellCopy
        }
      }
      finally{
        setTimeout(() => {
            let aaa=luckySheet2ReportGrid( this.sheet_window)
            $.extend(grid,aaa.grid);          
            this.setCellFromAPI = false; //状态重置
          }, 0);
      }
    },  
    preview_run(){
      this.report.layout=JSON.stringify( this.widgetForm, null, 4)
      this.preview_dialogVisible=true
    },
    save_report(){
      this.report.layout=JSON.stringify( this.widgetForm, null, 4)
      //console.info(JSON.stringify( this.widgetForm, null, 4))
      console.info(x2jsone.js2xml({report:this.report}))
    }
  },
  watch: { 
    selectWidget (newVal,oldval) {
      if(JSON.stringify(this.selectWidget)=='{"prop":"--"}')
        return
      this.cur_select_type='widget'
    },
//======================

    "cull_cell_cr":{
      handler(newVal,oldVal){        
        if(!this.can_watch_cell)
        {
          this.can_watch_cell=true
          return
        }
        let cacheUpdate=[]
        Object.keys(newVal).forEach(k=>{
          if(newVal[k]!=oldVal[k]){
            cacheUpdate.push({k,v:newVal[k]})
          }
        })
        let data=this.sheet_window.luckysheet.getSheet(0).data
        this.cur_sheet.luckysheet_select_save?.forEach(one_range=>{
          for(let r=one_range.row[0];r<=one_range.row[1];r++){
            for(let c=one_range.column[0];c<=one_range.column[1];c++){
              let cell=data[r][c]
              if(cell==null){
                  cell={m:'',v:'',cr:{"_displayValueExpr":"=@value"}}
                  this.sheet_window.luckysheet.setCellValue(r,c,cell);  
              }
              if(cell.v==undefined && cell.mc)//不处理合并单元格
                continue
              if(cell.cr==undefined)
                  cell.cr={"_displayValueExpr":"=@value"}
              cacheUpdate.forEach(one=>{
                cell.cr[one.k]=one.v
              })
              cell.v=cell.m=newVal._valueExpr
              if(cell.cr['_color'])
                  cell.fc=color(cell.cr['_color']) ? cell.cr['_color'] :"#000"
              if(cell.cr["_background-color"])
                  cell.bg=color(cell.cr['_background-color']) ? cell.cr["_background-color"] : "#fff"              
            }
          }
        })
        this.lucky_updated({range:this.cur_sheet.luckysheet_select_save },true) 
      },
      deep:true,immediate: true
    }
 }
}
</script>

<style lang="scss">
@import './styles/index.scss';

</style>