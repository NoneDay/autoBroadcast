<template>
  <basic-container>
    <el-row style="border: 1px blue dotted;">
    <el-tag>{{data.report_name}}</el-tag>
    当前ID:  <span v-html="data.curr_report_id" />  
      已定义数据集：
      
        <el-dropdown split-button type="primary"  v-for="x in all_ds" :key="x.name"   style="margin-right: 10px;"
        @click="create_ds_template_statement(null,x.name)"
        @command="create_ds_template_statement($event,x.name)"
        >
         {{x.name}}
        <el-dropdown-menu slot="dropdown">
          <el-col :span="8" v-for="col in x.last_columns" :key="col">
            <el-dropdown-item :command="col"  >{{col}}</el-dropdown-item>
          </el-col>         
        </el-dropdown-menu>
        
      </el-dropdown>

      <el-dropdown split-button type="success"  v-for="x in data.config_data.vars.filter(x=>x.resultType=='none') " :key="x.name"   style="margin-right: 10px;"
        @click="create_ds_template_statement(null,x.name)"
        @command="create_ds_template_statement($event,x.name)"
        >
         {{x.name}}
        <el-dropdown-menu slot="dropdown">
          <el-col :span="8" v-for="col in all_ds.find(a=>a.name==x.ds).last_columns" :key="col">
            <el-dropdown-item :command="col"  >{{col}}</el-dropdown-item>
          </el-col>         
        </el-dropdown-menu>
      </el-dropdown>

      

       
    </el-row>
    <el-row>
      <el-col :span="22"><div >
        <dataFromUrls :dataFrom.sync="data.config_data.data_from" @select_change="dataFromUrls_select_change" 
        :curr_report_id="data.curr_report_id"
        @reload_define="reload_define"
        />
      </div>
      </el-col>
    </el-row>
    <el-row style="border-top: groove;" >
      <el-col :span="22"><div >
        <dataDetail  :urlData.sync="data.tmp_detail_data" @query_data="query_data" @append_data="append_data"/>
      </div></el-col>
    </el-row>
    <el-row style="border-top: groove;" >
      <el-col :span="6" style="border: 1px red dotted;"
      ><div >
        <el-upload
          ref="upload"
          class="upload-demo"
          :data="{'curr_report_id':data.curr_report_id}"
          action="./aps/mg/file/posts"
          :limit="10"
          :http-request="myUpload"
          :on-preview="file_handlePreview"
          :on-remove="file_handleRemove"
          :on-error="file_error"
          :on-success="file_success"
          :on-change="file_change"
          :file-list.sync="data.fileList"
          :auto-upload="false"
        >
          <el-button slot="trigger" size="small" type="primary">选取文件</el-button>
          <el-button style="margin-left: 10px;" size="small" type="success" @click="file_submitUpload">上传到服务器</el-button>
          <div slot="tip" class="el-upload__tip">只能上传txt/xlxs/html/csv/md文件，且不超过500kb</div>
        </el-upload>
        

      </div>
      </el-col>
    <el-col :span="16" :gutter="20">
      <el-row>
        
        <el-button  type="primary" @click="form_set">参数设置</el-button>
        <el-button  type="primary" @click="look_config">查看设置</el-button>
        <el-button  type="primary" @click="save_config">保存</el-button>
        <el-button  type="success" @click="open_template_output">模板输出动作设置</el-button>
        <el-button  type="primary" @click="files_template_exec">按模板生成</el-button>        
        <el-button  type="primary" @click="workflow_visable=true">工作流</el-button>        

      </el-row>
      
      <el-row style="border: 1px red dotted;">
        <el-col :span="4">定时设置</el-col>   
        
        <el-col :span="8">
          <CronInput  v-model="data.cron_str" @change="change_cron" />
        </el-col>   
        <el-col :span="4">
          <el-switch v-model="data.cron_start" active-text="启动" inactive-text="关闭" :active-value="1" :inactive-value="0" />
        </el-col>     
        <el-col :span="8">
          
        </el-col>   
      </el-row>

      <el-row >
        <el-col :span="10" style="border: 1px red dotted;">
          <el-card class="box-card" >
            <div slot="header" class="clearfix">
              <span>变量</span>
              <el-button style="float: right; padding: 3px 0"  
              @click="varDetailDialog_show('detail')" type="text">添加</el-button>
            </div>
            <el-tag type="danger"  v-for="tag in data.config_data.vars" :key="tag.name"
              closable :disable-transitions="false"  @close="handleDeleteVar(tag)"
              @click="handleEditVar(tag)" style="margin: 10px;"
            >{{tag.name}}</el-tag>            
            
          </el-card>
        </el-col>
        <el-col :span="10" :offset="1" style="border: 1px red dotted;">
          <el-card class="box-card" >
            <div slot="header" class="clearfix">
              <span>文本模板</span>
              <el-button style="float: right; padding: 3px 0"  @click="tplDialog_show" type="text">新建</el-button>
            </div>
            <el-tag type="danger"  v-for="tag in data.config_data.text_tpls" :key="tag.name" style="margin: 10px;"
              closable :disable-transitions="false"  @close="handleDeleteTpl(tag)" @click="handleEditTpl(tag)"
            >{{tag.name}}</el-tag>         
            
          </el-card>

        </el-col>

      </el-row>      
    </el-col>
    </el-row>
    
    <varDetailDialog :visible.sync="data.varDetailDialog_visible" v-if="data.varDetailDialog_visible" :all_ds="all_ds" :target_obj="data.new_form_input"
          @submit="varDetailDialog_submit" 
        ></varDetailDialog>
    <tinymceDialog :visible.sync="data.tplDialog_visible" :target_obj="data.form_input_obj" 
    :all_vars="data.config_data.vars" :all_ds="all_ds"
          @submit="tplDialog_submit" 
    ></tinymceDialog>
    <el-dialog :visible.sync="workflow_visable" v-if="workflow_visable" :fullscreen="true" title="工作流" :close-on-click-modal="false" append-to-body>
      <landingPage :config_data="data.config_data" 
        :fileList="data.fileList"
        @reload_define="reload_define" 
        :report_name="data.report_name"
        :cron_start.sync="data.cron_start"
        :cron_str.sync="data.cron_str"
       :curr_report_id="data.curr_report_id" />
    </el-dialog>
    <el-dialog :visible.sync="data.result_visible" title="结果" :close-on-click-modal="false" append-to-body>
      
      <div v-for="key in data.ds_data.df_arr" :key="key" style="display:inline-block;padding-right:20px">
        <el-tag :style="{'border':key==cur_ds?'2px darkred solid':''}"
         @click="cur_ds=key" effect="dark">{{key}}</el-tag>
      </div>
      <div v-if="tableData.length==0" >无数据</div>
      <el-table stripe border  :height="250" v-if="tableData.length>0" 
                :data="tableData.slice((currentPage - 1) * pageSize, currentPage*pageSize)"  
                style="width: calc(100% -1px)">
                <el-table-column v-for="(one,idx) in Object.keys(tableData[0])"
                sortable :key="one+idx" :prop="one" :label="one"> </el-table-column>
            </el-table>           
            <el-pagination  v-if="tableData.length>0"
                :current-page.sync="currentPage"
                :page-sizes="[2, 5, 10, 20]"
                :page-size.sync="pageSize"
                layout="total, sizes, prev, pager, next, jumper"
                :total.sync="tableData.length">
            </el-pagination>
    </el-dialog>

    <formDialog :title="data.form_input_title" :visible.sync="data.form_input_visible" 
        @form_input_submit="form_input_submit"
        :oldFormInput.sync="data.form_input_obj" append-to-body :form-option="data.form_input_option"
    />

    <el-dialog :visible.sync="data.files_template_exec_result_visilbe" v-if="data.files_template_exec_result_visilbe" title="按模板生成的结果" 
    :close-on-click-modal='false' append-to-body>
        <template>
          <el-tabs value="first">
          <el-tab-pane label="模板结果" name="first">
              <el-table :data="data.files_template_exec_result.ret_files" style="width: 100%">
                <el-table-column prop="name" label="文件名" width="180"> </el-table-column>
                <el-table-column prop="message" label="信息" width="180"> </el-table-column>
                <el-table-column label="操作">
                    <template slot-scope="scope">
                      <span v-if="scope.row.url!=''">
                        <el-button size="mini" @click="file_handlePreview_t(scope.row)">下载</el-button>
                      </span>
                    </template>
                  </el-table-column>
              </el-table>

              <avue-comment :props=" {avatar: 'img',author: 'name',body: 'result'}" 
                :data="one" :key="one.name" v-for="one in data.files_template_exec_result.tpl_results" >
                <i class="el-icon-delete" @click="$message('自定义菜单')"></i>
              </avue-comment>        
          </el-tab-pane>
          <el-tab-pane  label="生成的图片" name="one_png">
            <div style="display: inline-block;    padding: 10px;"  v-for="one in all_image" :key="one">
              <el-image  style="width: 100px; height: 100px"  :z-index="2000000"
              :src="one" 
              :preview-src-list="all_image" 
              ></el-image>
            </div>
          </el-tab-pane>
          
        </el-tabs>
        </template>
        <div slot="footer" class="dialog-footer">
            <el-button @click="data.files_template_exec_result_visilbe = false">关闭</el-button>
        </div>
    </el-dialog>    
  </basic-container>
</template>

<script>
import dataFromUrls from './DataFromUrls2'
import dataDetail from './DataDetail2'
import varDetailDialog from './var_detail_dialog.vue'
import tinymceDialog from './tinymceDialog.vue'
import template_output_dialog from './template_output_dialog'
import formDialog from './formDialog'
import * as service from '@/api/zhanbao'
import CronInput from 'vue-cron-generator/src/components/cron-input'
import { baseUrl } from '@/config/env';
import {convert_array_to_json} from "@/views/rpt_design/utils/util"
import landingPage from "./workflow/plane"
const datas={}
export default {
  name: 'Zhanbao_old',
  components: { dataFromUrls, dataDetail, landingPage,template_output_dialog, formDialog,varDetailDialog,tinymceDialog,CronInput},
  computed:{
    all_image(){
      let rets=[]
      this.data.files_template_exec_result?.all_files?.filter(x=> x.endsWith('.png')|| x.endsWith('.JPG') ).forEach(one_png=>
      {
        rets.push(baseUrl+'/mg/image_file/'+ this.data.curr_report_id+'/'+one_png+`?time=${new Date().getTime()}` )
      })
      return rets
    },
    tableData(){      
      if(this.data.ds_data.ds_dict && this.data.ds_data.ds_dict[this.cur_ds]){
        return this.data.ds_data.ds_dict[this.cur_ds]
      }
      return []
    },
    all_ds(){
      let ret_arr=[]
      if(this.data.config_data.data_from)
        this.data.config_data.data_from.forEach(element => {
          if(element.ds)
            element.ds.forEach(one=>ret_arr.push(one))
      });
      if(this.data.config_data.vars===undefined)
        this.data.config_data.vars=[]
      if(this.data.config_data.text_tpls===undefined)
        this.data.config_data.text_tpls=[]
      return ret_arr
    },
  },
  data() {
    return {
      datas: datas,
      cur_ds:"",
      currentPage:1,
      pageSize:20,
      workflow_visable:false,
      data: this.getDefaultData()
    }
  },
  created() {
    
  },
  methods: {
    workflow_exec(){

    },
    create_ds_template_statement(command,ds_name){
      let text
      if(command===null){
        text="{{"+ ds_name+"}}"
      }
      else{
        text="{{"+ ds_name+"['"+command+"']}}"
      }
      let tag = document.createElement('input');
      tag.setAttribute('id', 'cp_hgz_input');
      tag.value = text;
      document.getElementsByTagName('body')[0].appendChild(tag);
      document.getElementById('cp_hgz_input').select();
      document.execCommand('copy');
      document.getElementById('cp_hgz_input').remove();
      this.$message({
          message: '已复制到剪贴板：'+text,
          type: 'success'
        });
    },
    change_cron(cron) {
      this.data.cron_str = cron
    },
    //变量定义的有关函数
    handleDeleteVar(tag){
      this.data.config_data.vars.splice(this.data.config_data.vars.indexOf(tag), 1);
    },
    handleEditVar(tag){
      this.data.new_form_input=tag
      this.data.varDetailDialog_visible=true
    },
    varDetailDialog_submit(obj){
       
      if(this.data.config_data.vars===undefined)
        this.data.config_data.vars=[this.deepClone(obj.newVal)]
      else{
        const vars=this.data.config_data.vars
        if(obj.old_Val.name){
          let idx=this.findArray(vars,obj.old_Val.name,'name');
          if(idx>=0)
            vars.splice(idx, 1,obj.newVal);
        }else
          vars.push(obj.newVal)
      }
    },
    varDetailDialog_show(var_type){
      this.data.new_form_input={var_type:var_type}
      this.data.varDetailDialog_visible=true
    },
 //以下是模板定义的有关函数
    handleDeleteTpl(tag){
      this.data.config_data.text_tpls.splice(this.data.config_data.text_tpls.indexOf(tag), 1);
    },
    handleEditTpl(tag){
      this.data.form_input_obj=tag
      this.data.tplDialog_visible=true
    },
    tplDialog_submit(obj){   
          
      if(this.data.config_data.text_tpls===undefined)
        this.data.config_data.text_tpls=[this.deepClone(obj.newVal)]
      else{
        const text_tpls=this.data.config_data.text_tpls
        if(obj.old_Val.name){
          let idx=this.findArray(text_tpls,obj.old_Val.name,'name');
          if(idx>=0)
            text_tpls.splice(idx, 1,obj.newVal);
        }else
          text_tpls.push(obj.newVal)
      }
    },
    tplDialog_show(){
      this.data.form_input_obj={name:'',txt:''}
      this.data.tplDialog_visible=true
    },

 
//-------------------------------
    dataFromUrls_select_change(par) {
      this.data.tmp_detail_data = par//?par:{ds:[],form_input:[]}
    },
    append_data(detail_data){
      this.data.form_input_title = '合并其他数据'
      this.data.form_input_option = {
        cellBtn:true,editBtn:false,cellEdit:true, 
        appendTxt:"<b>备份</b>  取历史备份数据，严格按照这个格式写。程序在指定时间执行的时候，会备份当时该数据。任何时候取数"+
      "都会去取前一天(填上次就取当天上次计算取到得报表数据，注意区别)的这个数据，然后按第一列为关键字合并到一起<br>"+
      "<b>group.csv</b> 从csv文件中取数<br>"+
      "<b>b</b>  其他文字，按数据源取数<br>"+
      "合并数据时，以当前表为主表，将附加表附加到当前主表上，如果没有数据，将设置为0"
        ,
        column: [
          { prop: 'from', label: '数据来源', width: 250 ,rules: [{required: true,message: '必填项',trigger: 'blur'}]},
          { prop: 'suffixes', label: '后缀', width: 250 }
        ] 
      }
      this.data.form_input_obj = detail_data.append
      let old_this=this
      this.data.form_input_submit=function(){
        detail_data.append=old_this.data.form_input_obj 
        old_this.data.form_input_obj={}
      }
      this.data.form_input_visible = true
    },
    query_data(url_data, detail_data) {
      let old_this = this
       service.query_data({ config_data: this.data.config_data, 
        curr_report_id: this.data.curr_report_id }
      ).then(res_data=>{
        old_this.data.result_visible = true
        old_this.data.result = res_data.html
        if(res_data.ds_dict){
          res_data.df_arr.forEach(one_df=>{
            old_this.cur_ds=one_df
            let one=JSON.parse( res_data.ds_dict[one_df] )
            res_data.ds_dict[one_df]=convert_array_to_json(one.data,0,-1,one.columns)
          })
        }
        old_this.data.ds_data=res_data
        if (detail_data && detail_data['name']){
          old_this.cur_ds=detail_data['name']
        }else{
          
        }
        Object.assign(old_this.data.config_data=res_data.config_data)
      }).catch(error=>{
        if( typeof(error.config_data)=="object")
            Object.assign(old_this.data.config_data=error.config_data)
      })
      //this.data.config_data.curr_report_id=this.curr_report_id
      //res_data.config_data.data_from.forEach( (df,df_index)=>{
      //  this.data.config_data.data_from[df_index].form_input=df.form_input
      //  this.data.config_data.data_from[df_index].type=df.type
      //  df.ds.forEach((ds,ds_index)=>{ 
      //    if(this.data.config_data.data_from[df_index].ds[ds_index])
      //      Object.assign(this.data.config_data.data_from[df_index].ds[ds_index],ds)
      //    else
      //      this.data.config_data.data_from[df_index].ds.push(ds)
      //    }
      //  )
      //});
    },
    // ---------------------------
    open_template_output() {
      if(!Array.isArray(this.data.config_data.template_output_act))
        this.data.config_data.template_output_act=[]
      let template_output=this.data.config_data.template_output_act
      this.data.fileList.forEach(one=>{
        if(template_output.filter(x=>x.file===one.name).length===0){
          template_output.push({'file':one.name,'canOutput':"false",'wx_file':'','wx_msg':''})
        }
      })
      
      let a_map=new Map()
      this.data.fileList.forEach(one=>{ a_map.set(one.file,one) })

      let b_map=new Map()
      template_output.forEach(one=>{ b_map.set(one.file,one) })

      b_map.forEach(x=>{ 
        if(a_map.has(x.key)==false) 
          template_output.splice(this.data.template_output.indexOf(x.value),1) 
      })
      
      let aa=[];
      this.all_ds.forEach(one => {
          aa.push({'label':one.name,'value':one.name} )
        });
      this.data.config_data.vars.filter(x=>x.resultType=='none').forEach(one => {
          aa.push({'label':one.name,'value':one.name} )
        });
      this.data.form_input_title = '模板输出动作设置'
      this.data.form_input_option = {
        addBtn:false,cellEdit:false,rowKey:'file',
        column: [
            { prop: 'file', label: '名字', cell:false,formslot:true },
            { prop: 'canOutput', label: '作为模板', type:'select',value:false,dicData: [{label: '是',value: "true"}, {label: '否',value: "false"}] },
            { prop: 'wx_file', label: '文件发送' },
            { prop: 'wx_msg', label: '图片或文本发送' },
            { prop: 'loopForDS', label: '针对数据集循环', width: 80,type:'select',
              dicData: aa
            },
          ] ,appendTxt:"如果设置“针对这个数据集中的每条数据执行模板”， 使用_loop_['字段']来引用原数据集中的数据。_idx_ 表示当前取到第几行数据。这个功能只针对PPT模板有作用。"
      }
      this.data.form_input_obj = template_output
      let old_this=this
      this.data.form_input_submit=function(){        
        old_this.data.config_data.template_output_act=old_this.data.form_input_obj 
        old_this.data.form_input_obj={}
        }
      this.data.form_input_visible = true
      
    }, 
    
    look_config() {
      this.data.form_input_obj = {txt:JSON.stringify(this.data.config_data, null, 4)}
      this.data.form_input_title = '模板json，不要修改'
      this.data.form_input_option = {
        column: [{ prop: 'txt', label: '',type:'textarea',minRows:30,maxRows:30 }] 
      }
      let old_this=this
      this.data.form_input_submit=function(){
        //this.data.config_data = JSON.parse(this.data.tmp_text)
      }
      this.data.form_input_visible = true
    },
    form_set() {
      let t_arr = []
      for (let i = 0; i < this.data.config_data.data_from.length; i++) {
        if (this.data.config_data.data_from[i].form_input !== undefined) { t_arr = t_arr.concat(this.data.config_data.data_from[i].form_input) }
      }

      for (let i = 0; i < t_arr.length; i++) {
        if (undefined === this.data.config_data.form_input.find(function(x) { return x.name === t_arr[i].name })) { this.data.config_data.form_input.push(t_arr[i]) }
      }
      this.data.form_input_title = '需要的参数'
      this.data.form_input_option = {
        addBtn:false,delBtn:false,cellBtn:true,editBtn:false,cellEdit:true,rowKey:'name',
        column: [{ prop: 'name', label: '参数名字', cell:false,formslot:true  },{ prop: 'value', label: '参数值', cell:true }] 
      }
      this.data.form_input_obj = this.data.config_data.form_input
      let old_this=this
      this.data.form_input_submit=function(){
        old_this.data.config_data.form_input=old_this.data.form_input_obj 
        old_this.data.form_input_obj={}
        }
      this.data.form_input_visible = true
    },
    jiancha:function(){
      let arr=[]
        let chongfu=false
        this.data.config_data.data_from.forEach(x=>{
          x.ds.forEach(y=>{
            if(arr.includes(y.name))
              chongfu=true
            arr.push(y.name)
          })
        })
        return chongfu
      },
    async files_template_exec() {
      if (this.jiancha()) {
        this.$message.error('请检查name设置，不能重复！！')
        return
      }
      const data = await service.files_template_exec(this.data.curr_report_id, { config_data: this.data.config_data })
      this.data.files_template_exec_result = data
      this.data.files_template_exec_result_visilbe = true
    },
    async save_config() {
      if (this.jiancha()) {
        this.$message.error('请检查name设置，不能重复！！')
        return
      }
      const data = await service.save_config(this.data.curr_report_id, 
          JSON.parse(JSON.stringify( { config_data: this.data.config_data,
            report_name: this.data.report_name,
            cron_str: this.data.cron_str,
            cron_start: this.data.cron_start
          }))
        )
      if(data.errcode && data.errcode!=0){
        this.$message.error(data.message)
        return        
      }
      this.data.curr_report_id = data.lastrowid
    },
    // ----------------------------------------
    file_submitUpload(content) {
      
      if (this.data.curr_report_id === 0) {
        this.$message.error('必须先保存新建文件后才能保存上传文件')
        return
      }
      this.$refs.upload.submit()
    },
    async myUpload(content){
      
      let form = new FormData();
      form.append("file", content.file);
      let ret=await service.file_upload(this.data.curr_report_id,form)
      
      if(ret.errcode==0)
        this.$message.success(ret.message)
      else
        this.$message.error(ret.message)
    },
    async file_handleRemove(file) {
      let ret=await service.file_remove(this.data.curr_report_id,file.name)
      let idx=this.data.fileList.indexOf(file)
      if(idx>=0)
        this.data.fileList.splice(idx,1);
      
      let tmp=this.data.config_data.template_output_act
      let one=tmp.find(x=>x.file==file.name)
      if(one && tmp.indexOf(one)>=0)
        tmp.splice(tmp.indexOf(one),1);

      if(ret.errcode==0)
        this.$message.success(ret.message)
      else
        this.$message.error(ret.message)
    },
    file_success(response, file, fileList) {
       let tmp=this.data.config_data.template_output_act
      let one=tmp.find(x=>x.file==file.name)
      if(!one)
        tmp.push({file:file.name,'canOutput':"false",'wx_file':'','wx_msg':''})
    },
    file_error(error, file, fileList) {
      console.log(file, fileList)
      this.$message.error(error)
    },
    file_change(file, fileList) {
      console.log(file, fileList)
    },
    download(fileName, res) { // 处理返回的文件流
      const blob = res
      if ('download' in document.createElement('a')) { // 非IE下载
        const elink = document.createElement('a')
        elink.download = fileName
        elink.style.display = 'none'
        elink.href = URL.createObjectURL(res)
        document.body.appendChild(elink)
        elink.click()
        URL.revokeObjectURL(elink.href) // 释放URL 对象
        document.body.removeChild(elink)
      } else { // IE10+下载
        navigator.msSaveBlob(blob, fileName)
      }
    },
    async file_handlePreview(file) {
      const res=await service.file_preview(this.data.curr_report_id,file.name)
      this.download(file.name, res)
    },
    async file_handlePreview_t(file) {
      const res=await service.file_preview_t(this.data.curr_report_id,file.name)
      this.download(file.name, res)
    },    
    change_type_detail(row) {
      console.info(row)
    },
    async reload_define(){
        //const data_r = {
        //  ...this.getDefaultData(),
        //  ...await service.getZhanbao(this.data.curr_report_id)
        //}
        //data_r.config_data = JSON.parse(data_r.config_txt)
        //if(undefined== data_r.config_data.template_output_act)
        //  data_r.config_data.template_output_act=[]
        //if(data_r.config_data.ds_queue==undefined)
        //  delete this.data.config_data.ds_queue
        //if(data_r.config_data.ds_depend==undefined)
        //  delete this.data.config_data.ds_depend
        //
        //Object.assign( this.data.config_data , data_r.config_data)
       //
        //if(!Array.isArray(this.data.config_data.template_output_act))
        //    this.data.config_data.template_output_act=[]
        //let template_output=this.data.config_data.template_output_act
        //this.data.fileList.forEach(one=>{
        //    if(template_output.filter(x=>x.file===one.name).length===0){
        //    template_output.push({'file':one.name,'canOutput':"false",'wx_file':'','wx_msg':''})
        //    }
        //})         
      delete this.datas[this.data.curr_report_id+'m']
      this.switchData(this.data.curr_report_id)
    },
    form_input_submit(obj){
      return this.data.form_input_submit(obj)
    },
    getDefaultData() {
      return {
        curr_report_id: -1,
        report_name: '',
        config_data: {},
        cron_start: 0,
        cron_str: '0 30 7,18 * * * *',
        fileList: [],
        template_output: [],
        ds_data:{},
        tmp_detail_data: null,
        

        form_input_title: '',
        form_input_obj: {},
        form_input_option: {},
        form_input_visible: false,
        form_input_submit(obj){},

        new_form_input: {},
        
        result: '',
        result_visible: false,
        
        varDetailDialog_visible:false,
        tplDialog_visible:false,
        files_template_exec_result_visilbe:false,
        files_template_exec_result:{},
        
        
      }
    },
    async switchData(id) {
      const data = this.datas[id+'m']
      
      if (data===undefined) {
        const data_r = {
          ...this.getDefaultData(),
          ...await service.getZhanbao(id)
        }
        data_r.curr_report_id = id
        data_r.config_data = JSON.parse(data_r.config_txt)
        if(undefined== data_r.config_data.template_output_act)
          data_r.config_data.template_output_act=[]
        //if(undefined==data_r.config_data.ds_queue)
        //  data_r.config_data.ds_queue=[]
        //if(undefined==data_r.config_data.ds_depend)
        //  data_r.config_data.ds_depend=[]
          
        this.datas[id+'m'] = data_r
        this.data = data_r
        return
      }
      this.data = data
    }
  },


  async beforeRouteEnter(to, from, next) {
    const id = to.params.id || to.meta.id
    if (id) {
      await next(async instance => await instance.switchData(id))
    } else {
      next(new Error('未指定ID'))
    }
  },
  // 在同一组件对应的多个路由间切换时触发
  async beforeRouteUpdate(to, from, next) {
    const id = to.params.id || to.meta.id
    if (id) {
      await this.switchData(id)
      next()
    } else {
      next(new Error('未指定ID'))
    }
  }
}
</script>
<style >
.inputDialog{
      width:1000px
  }
.avue-crud .el-table--small td, .avue-form .el-table--small td {
    padding: 1px 0!important;
}
.avue-crud__empty {
    padding: 6px 0;
}
.el-table--small td, .el-table--small th {
    padding: 1px 0;
}
.el-form-item--small.el-form-item {
    margin-bottom: 8px;
}
.el-form-item--mini.el-form-item, .el-form-item--small.el-form-item {
    margin-bottom: 8px;
}
.el-dialog__header{
  background-color: blanchedalmond;
}
.el-popover{
  background-color: blanchedalmond;
}
.el-input-number.is-controls-right .el-input__inner {
    padding-left: 5px;
    padding-right: px;
}
.box-card .el-card__header{
  background-color: blanchedalmond;
}
.contextmenu_zb{
      background-color: lightgray!important;
  }
</style>