<template>
  <div class="form-designer"  >
    <div style="position: absolute;right:40px;top:10px;">
    <div v-if="!executed || showLog" style="display:inline-block;">  
      <div v-for="([key,val]) in Object.entries(ds_log)" :key="key" style="display:inline-block;padding-right:20px">
        <el-tag :type="val.color" :style="{'border':key==show_type?'2px darkgreen solid':''}"
         @click="tag_click(key,val)" effect="dark"
        >{{key}}</el-tag>
      </div>
      </div>
      
    <div  style="display:inline-block;padding-right:20px">
    <el-button 
      v-if="executed"
     @click="showLog=!showLog;show_type='______ALL_____';">显示{{showLog?'报表':'日志'}}
     </el-button>
     </div>
  </div>
  <div  v-if="!executed || showLog" style="height:100%" >
    <textarea ref="textarea" :style="{height:show_type=='______ALL_____'?'100%':'50%',width:'100%'}" :value="show_content">
    </textarea>
    
    <el-table stripe border  :height="'50%'" v-if="show_type!='______ALL_____' && tableData.length>0" 
        :data="tableData.slice((currentPage - 1) * pageSize, currentPage*pageSize)"  
        style="width: calc(100% -1px)">
        <el-table-column v-for="(one,idx) in Object.keys(tableData[0])" 
        sortable :key="one+idx" :prop="one" :label="one"> </el-table-column>
    </el-table>           
    <el-pagination  v-if="show_type!='______ALL_____' && tableData.length>0"
        :current-page.sync="currentPage"
        :page-sizes="[2, 5, 10, 20]"
        :page-size.sync="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total.sync="tableData.length">
    </el-pagination>    
  </div>
  <template v-else>
    <div> 
      <el-form :inline="true" >
        <el-input hidden v-for="one in result.form.filter(x=>x.hide=='True')" :key="one.name" v-model="queryForm[one.name]">
        </el-input>
      
        <div style="display:inline" v-for="one in result.form.filter(x=>x.hide=='False')" :key="one.name">
          <el-form-item :label="one.prompt">
          <el-input v-if="one.data_type=='string' && one.tagValueList.length==0" v-model="queryForm[one.name]"></el-input>
          <el-select v-if="one.data_type=='string' && one.tagValueList.length>0" v-model="queryForm[one.name]" :multiple="one.allowMutil=='False'?false:true">
             <el-option
                v-for="item in one.tagValueList"
                :key="item[1]"
                :label="item[0]"
                :value="item[1]">
              </el-option>
          </el-select>
          <el-date-picker v-if="one.data_type=='date'" value-format="yyyy-MM-dd" 
                    v-model="queryForm[one.name]"></el-date-picker>
          <el-date-picker v-if="one.data_type=='dateTime'" :value-format="one.dateTimeFormat" :format="one.dateTimeFormat" 
          :type="['yyyyMM','yyyy-MM'].includes(one.dateTimeFormat)?'month':'datetime'"
                    v-model="queryForm[one.name]"></el-date-picker>
          </el-form-item>
          
           </div>
            <el-form-item>
            <el-button type="primary">查询</el-button>
            
          </el-form-item>
      </el-form>
    </div>
    <div style="height:90%">
        <grid-layout-form v-if="layoutType=='gridLayout'" :layout="layout" >
        </grid-layout-form>          
        <widget-form v-else   :data="layout"   
        ></widget-form>
    </div>
    </template>
  </div>
</template>

<script>
import widgetForm from './WidgetForm'
import {loadFile,deepClone,build_layout,get_signalR_connection,convert_array_to_json} from './utils/util.js'
import Textarea from './config/textarea.vue'
import {preview_one} from "./api/report_api"
export default {
    name: 'preview',  
    props:{context:Object},
    components:{widgetForm },
    mounted() {
        preview_one(this)
    }, 
  inject: ["context"],
  provide() {
    return {
      context: {
          canDraggable:false,
          report:this.context?.report,
          report_result:this.result,
          isPreview:1,
          event:{},
          clickedEle:this.clickedEle,
          //不放到这里，会导致动态runtime-template重算，如果是有滚动行的，会每次都重新跑到顶部
          in_exec_url:this.in_exec_url,
          fresh_ele:this.fresh_ele,
      },      

    }
  },  
  data () {
    return {
        queryForm:{},
        exec_log:"",
        result:{},
        clickedEle:{},
        executed:false,
        layout:[],
        showLog:false,
        ds_log:{},
        show_type:"______ALL_____",
        currentPage:1,
        pageSize:20,
        fresh_ele:[],
        in_exec_url:{stat:false},
    }
  },
  
  computed: {
    tableData(){
      let ret=this.context.report_result?.dataSet[this.show_type]
      if(ret)
        return convert_array_to_json(ret[0])
      else
        return convert_array_to_json([['a']])
    },
    show_content(){
      if(this.ds_log[this.show_type])
        return this.ds_log[this.show_type].content.join("\n")
      else 
      return this.exec_log
    },
    parentHeight(){
        return this.$parent.$el.clientHeight
    },
    layoutType(){
      if (Array.isArray(this.layout))
      return 'gridLayout'
      else
      return 'divLayout'
    },
  },
  methods: {
    tag_click(key,val){
      console.info(val.color); 
      this.show_type=key
    }
  },   

}
</script>

<style>

</style>