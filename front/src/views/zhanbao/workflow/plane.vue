<template>
    <div style="height: calc(100vh);">
        <el-row>
            <!--顶部工具菜单-->
            <el-col :span="24">
                <div class="ef-tooltar">
                    
      已定义数据集：
      
        <el-dropdown split-button type="primary"  v-for="x in all_ds" :key="x.name" size="mini"  style="margin-right: 10px;"
        @click="create_ds_template_statement(null,x.name)"
        @command="create_ds_template_statement($event,x.name)"
        >
         {{x.name}}
        <el-dropdown-menu slot="dropdown">
          <el-col :span="6" v-for="col in x.last_columns" :key="col">
            <el-dropdown-item :command="col"  >{{col}}</el-dropdown-item>
          </el-col>         
        </el-dropdown-menu>
        
      </el-dropdown>

      <el-dropdown split-button type="success" size="mini" v-for="x in config_data.vars.filter(x=>x.resultType=='none') " :key="x.name"   style="margin-right: 10px;"
        @click="create_ds_template_statement(null,x.name)"
        @command="create_ds_template_statement($event,x.name)"
        >
         {{x.name}}
        <el-dropdown-menu slot="dropdown">
          <el-col :span="6" v-for="col in all_ds.find(a=>a.name==x.ds).last_columns" :key="col">
            <el-dropdown-item :command="col"  >{{col}}</el-dropdown-item>
          </el-col>         
        </el-dropdown-menu>
      </el-dropdown>

                </div>
            </el-col>
        </el-row>
        <div style="display: flex;height: calc(100% - 47px);" @contextmenu="showMenu('画布',null,$event,null)">
            <div   id="efContainer" ref="efContainer">
                <div  class="line-wrap" :key="idx" v-for="(data_from,idx) in config_data.data_from"  >
                    <zbnode type='URL' :node='data_from' :node_name='idx' 
                    :txt="data_from.desc ? data_from.desc:('file'==data_from.type || data_from.url.startsWith('结果') ?data_from.url: data_from.type)"
                    />
                    
                    <div>
                        <div :key="idx1" class="line-wrap"  v-for="(ds,idx1) in data_from.ds" >
                            <div  >
                                <template v-if="!['sql','file'].includes( data_from.type) && !data_from.url.startsWith('结果://')">
                                    <zbnode type='裁剪' :node='ds' :node_name='ds.name' />
                                    <zbnode type='昨日' :node='ds' :node_name='ds.name'  v-if="ds.backup"/>
                                    <zbnode type='上次' :node='ds' :node_name='ds.name'  v-if="ds.backup"/>
                                </template>
                                <div v-else style="width:164px">
                                    
                                </div>
                            </div>
                                <zbnode type='合并' :node='ds' :node_name='ds.name'/>
                                
                                <zbnode type='最终' :node='ds' :node_name='ds.name' />
                                
                            <div style="width:230px;border:1px #e84f4f dotted;display: flex;flex-wrap: wrap;" 
                                :id="'来自:'+ds.name" v-if="config_data.vars.filter(x=>x.ds==ds.name).length>0">
                                <zbnode  v-for="one_var in config_data.vars.filter(x=>x.ds==ds.name)" 
                                    :key="one_var" style="margin: 2px;" 
                                    type='变量' :node='one_var' :node_name='one_var.name' />
                                
                            </div>
                        </div>
                    </div>
                
                </div>
                <div class="line-wrap" >
                    <div style="width:250px; min-height:10px;border:1px black dotted;margin-bottom: 10px; min-height:100px">
                        <div style="background:#d0cbcb;color:#4f4c4c;">
                            <div style="display: inline-block;"> 数据文件</div>
                            <el-tooltip content="上传文件"  style="float:right">
                            <el-upload
                                ref="upload" 
                                class="upload-demo" style="display: inline-block;"
                                :data="{'curr_report_id':curr_report_id}"
                                :action="baseUrl+'/mg/file/posts'"
                                :limit="10" :show-file-list="false"
                                :http-request="myUpload"
                                :on-preview="file_handlePreview"
                                :on-remove="file_handleRemove"
                                :on-error="file_error"
                                :on-success="file_success"
                                :on-change="file_change"
                                >        
                                <el-button type="text" style="padding: 0px;">
                                    <svg t="1614997253342" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="20551" width="20" height="20"><path d="M887.3472 697.2416h-100.352v-100.352a33.4848 33.4848 0 1 0-66.9184 0v100.352H619.52a33.4336 33.4336 0 0 0 0 66.8672h100.352v100.352a33.4848 33.4848 0 1 0 66.9184 0v-100.352h100.352a33.4336 33.4336 0 0 0 0-66.8672z" fill="#1296db" p-id="20552"></path><path d="M197.9904 846.1312V200.0384a23.04 23.04 0 0 1 22.7328-22.7328h533.7088a23.04 23.04 0 0 1 22.784 22.7328v280.8832h66.8672V200.0384a89.7536 89.7536 0 0 0-89.6512-89.6512H220.7232A89.8048 89.8048 0 0 0 131.072 200.0384v646.0928a89.8048 89.8048 0 0 0 89.6512 89.6512h266.8544V868.864H220.7232a23.04 23.04 0 0 1-22.7328-22.7328z" fill="#1296db" p-id="20553"></path><path d="M296.96 278.9376a33.536 33.536 0 0 0 0 66.9184h330.9056a33.536 33.536 0 0 0 0-66.9184zM487.424 447.488H296.96a33.536 33.536 0 0 0 0 66.9184h190.464a33.536 33.536 0 0 0 0-66.9184zM431.2576 682.9568a33.536 33.536 0 0 0 0-66.9184H296.96a33.536 33.536 0 0 0 0 66.9184z" fill="#1296db" p-id="20554"></path></svg>
                                </el-button>
                                </el-upload> 
                            </el-tooltip> 
                            
                        </div>
                        <div class="line-wrap" :key="idx" v-for="(data_from,idx) in config_data.template_output_act"  >
                                <zbnode type='文件' :node='data_from' :node_name='data_from.file' style="width: 200px;" />
                        </div>
                    </div>
                    <div style="width:200px;border: 1px gray dotted">
                            <div>定时设置</div>
                            <div>
                                <CronInput  v-model="cron_str" @change="change_cron" />
                            </div>   
                            <div>
                                <el-switch v-model="cron_start" 
                                active-text="启动" inactive-text="关闭" 
                                :active-value="1" :inactive-value="0" />
                            </div>   
                            <div>战报名称:{{report_name}}</div>
                            <div>报表ID:{{curr_report_id}}</div>
                    </div>
                    <div style="width:250px;border: 1px gray dotted" >
                        <div style="background:#d0cbcb;color:#4f4c4c;">
                        <span>文本模板</span>
                        <el-button style="float: right; padding: 3px 0"  @click="tplDialog_show" type="text">新建</el-button>
                        </div>
                        <zbnode v-for="tag in config_data.text_tpls" :key="tag.name" style="margin: 10px;"
                             type='文本模板' :node='tag' :node_name='tag.name' 
                        >
                        </zbnode>
                        
                    </div>
                    <div style="width:200px;border:1px black dotted"  v-if="config_data.ds_queue">
                        <div style="background:#d0cbcb;color:#4f4c4c;">
                            <div style="display: inline-block;">变量</div>
                            <el-tooltip content="添加变量" style="float:right">
                                <el-button type="text" style="padding: 0px;"  @click="varDetailDialog_show('detail')">
                                    <svg t="1614996996177" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="18610" width="20" height="20"><path d="M512 56.888889C261.688889 56.888889 56.888889 261.688889 56.888889 512s204.8 455.111111 455.111111 455.111111 455.111111-204.8 455.111111-455.111111-204.8-455.111111-455.111111-455.111111z m0-56.888889c284.444444 0 512 227.555556 512 512s-227.555556 512-512 512-512-227.555556-512-512 227.555556-512 512-512zM261.688889 620.088889v-45.511111h455.111111v45.511111c-39.822222 56.888889-91.022222 102.4-153.6 142.222222 73.955556 34.133333 164.977778 56.888889 284.444444 62.577778-17.066667 22.755556-28.444444 39.822222-39.822222 56.888889-119.466667-17.066667-216.177778-45.511111-295.822222-91.022222-73.955556 39.822222-170.666667 68.266667-295.822222 96.711111l-34.133334-51.2c113.777778-22.755556 210.488889-45.511111 278.755556-79.644445-51.2-34.133333-91.022222-85.333333-125.155556-136.533333H261.688889zM193.422222 312.888889h301.511111c-11.377778-22.755556-22.755556-45.511111-34.133333-62.577778L512 227.555556c22.755556 34.133333 34.133333 56.888889 45.511111 73.955555l-28.444444 11.377778h301.511111v45.511111h-216.177778v187.733333h-51.2V358.4H460.8v187.733333h-56.888889V358.4H193.422222v-45.511111z m455.111111 307.2H398.222222c34.133333 51.2 68.266667 85.333333 113.777778 113.777778 51.2-28.444444 96.711111-68.266667 136.533333-113.777778z m5.688889-187.733333l39.822222-34.133334c56.888889 51.2 102.4 96.711111 142.222223 136.533334l-45.511111 34.133333c-39.822222-45.511111-85.333333-91.022222-136.533334-136.533333zM318.577778 398.222222l39.822222 34.133334c-45.511111 51.2-91.022222 96.711111-136.533333 142.222222-11.377778-17.066667-22.755556-28.444444-34.133334-39.822222 45.511111-39.822222 91.022222-85.333333 130.844445-136.533334z" p-id="18611" fill="#1296db"></path></svg>
                                </el-button>
                            </el-tooltip>
                        </div>
                        <zbnode  v-for="one_var in config_data.vars.filter(x=>!config_data.ds_queue.includes(x.ds))" 
                            :key="one_var" style="margin: 2px;" 
                            type='变量' :node='one_var' :node_name='one_var.name' />
                    </div>
                </div>
                <div>
                计算顺序 {{config_data.ds_queue}}
                <template v-if="activeElement.node">
                <div v-if="activeElement.node.exec_stat" :style="{'color':activeElement.node.exec_stat.split(':')[0]=='9'?'green':'red'}">
                        执行状态：{{activeElement.node.exec_stat}}<br>
                </div>
                <div v-if="activeElement.node.append">
                        合并数据：{{activeElement.node.append}}<br>
                </div>
                {{config_data.ds_depend}}
                </template> 
                </div>
            </div>
            
            <!-- 右侧表单 
            <div style="width: 300px;border-left: 1px solid #dce3e8;background-color: #FBFBFB">
                <div class="ef-node-form">
                    <div class="ef-node-form-header">
                        编辑
                    </div>
                    <div class="ef-node-form-body" v-if="activeElement.node">
                        <div v-if="activeElement.node.exec_stat" :style="{'color':activeElement.node.exec_stat.split(':')[0]=='9'?'green':'red'}">
                        执行状态：{{activeElement.node.exec_stat}}<br>
                        </div>

                        <div v-if="['line'].includes(activeElement.type)">
                            {{activeElement.sourceId}} => {{activeElement.targetId}} 
                            
                        </div>
                        <div class="ef-node-form-header">
                            config_data.ds_depend
                        </div>
                        <div>
                            {{config_data.ds_depend}}
                        </div>
                        <div class="ef-node-form-header">
                            activeElement.node
                        </div>
                        <div>
                            activeElement.node}}
                        </div>
                    </div>
                </div>
            </div>-->
        </div>
         
        <el-dialog :visible.sync="urlData_ds_visible" v-if="urlData_ds_visible"  label="。。" :close-on-click-modal="false" append-to-body>
            <avue-form :option="urlData_ds_option()" v-model="tmp_obj" @submit="urlData_ds_submit"> </avue-form>
        </el-dialog>
        <el-dialog :visible.sync="url_visible" v-if="url_visible"  label="。。" 
        :close-on-click-modal="false" append-to-body :fullscreen="true">
            <avue-form :option="url_option()" v-model="tmp_obj" @submit="url_submit"> 
            </avue-form>
        </el-dialog>
        <el-dialog :visible.sync="template_actSet_dialog_visilbe" v-if="template_actSet_dialog_visilbe"  label="。。" :close-on-click-modal="false" append-to-body>
            <avue-form :option="template_actSet_option()" v-model="tmp_obj" @submit="template_actSet_dialog_submit"> 
            </avue-form>
        </el-dialog>


        <el-dialog :visible.sync="sql_visible" v-if="sql_visible"  label="。。" :close-on-click-modal="false" append-to-body>
             <el-tabs value="first">
                <el-tab-pane label="sql管理" name="first">
                    <codemirror v-if='sql_visible' ref="sqlEditor"    v-model="tmp_obj" 
                    :options="{tabSize: 4, mode: 'text/x-sql', styleActiveLine: true,lineWrapping: true,
                        theme: 'cobalt',showCursorWhenSelecting: true }" 
                        @ready="editor_ready"
                    />
                </el-tab-pane>
                <el-tab-pane label="合并后的所有字段" name="second">
                    <el-tag>select </el-tag><br>
                    <template v-for="(one,idx) in activeElement.node.after_append_columns">
                        <span :key="one" v-if="idx!=0">,</span>
                        <span :key="one" v-if="idx%4==0"><br></span>
                        <el-tag  :key="one">[{{one}}]</el-tag>  
                    </template>
                    <br><el-tag>from </el-tag><br>
                    <el-tag>{{activeElement.node.name}}</el-tag>
                </el-tab-pane>

            </el-tabs>
            
            <span slot="footer" class="dialog-footer">
                <el-button @click="tmp_obj=''">清空</el-button>
                <el-button @click="sql_visible = false">取 消</el-button>
                <el-button type="primary" @click="sql_dialog_submit">确 定</el-button>
            </span>
         </el-dialog>
        <var-detail-dialog 
            :visible.sync="varDetailDialog_visible" 
            v-if="varDetailDialog_visible" :all_ds="all_ds" 
            :target_obj="tmp_obj"
            @submit="varDetailDialog_submit" 
        ></var-detail-dialog>
        <tinymceDialog :visible.sync="tplDialog_visible" :target_obj="tmp_obj" 
            :all_vars="config_data.vars" :all_ds="all_ds"
                @submit="tplDialog_submit" 
        ></tinymceDialog>
        <el-dialog :visible.sync="files_template_exec_result_visilbe" v-if="files_template_exec_result_visilbe" title="按模板生成的结果" 
            :close-on-click-modal='false' append-to-body>
            <template>
            <el-tabs value="first">
            <el-tab-pane label="模板结果" name="first">
                <el-table :data="files_template_exec_result.ret_files" style="width: 100%">
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
                    :data="one" :key="one.name" v-for="one in files_template_exec_result.tpl_results" >
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
                <el-button @click="files_template_exec_result_visilbe = false">关闭</el-button>
            </div>
        </el-dialog>
        <el-dialog :visible.sync="query_result_visible" title="结果" :close-on-click-modal="false" append-to-body
            :fullscreen="true"
        >
            <div v-for="key in ds_data.df_arr" :key="key" style="display:inline-block;padding-right:20px">
                <el-tag :style="{'border':key==cur_ds?'2px darkred solid':''}"
                @click="cur_ds=key" effect="dark">{{key}}</el-tag>   
            </div> <el-button @click="export_excel(tableData)">导出到excel</el-button>
           
            <div  style="height:250px">
                <avue-crud size="mini" ref="crud" :data="tableData.slice((page.currentPage - 1) * page.pageSize, page.currentPage*page.pageSize)" 
                :option="tableData_option" :page.sync="page" >
                    <template slot-scope="scope" slot="menuLeft">
                        
                    </template>
                    <template slot-scope="scope" slot="menu">
                        
                    </template>
                </avue-crud>
        </div>
        </el-dialog> 
        <formDialog :title="form_input_title" :visible.sync="form_input_visible" 
          @form_input_submit="form_input_submit"
            :oldFormInput.sync="form_input_obj" append-to-body :form-option="form_input_option"
        />   
    </div>
</template>

<script>
import 'codemirror/lib/codemirror.css' 
import 'codemirror/theme/cobalt.css' 
import tinymceDialog from '../tinymceDialog.vue'
//import {jsPlumb} from 'jsplumb'
import varDetailDialog from '../var_detail_dialog.vue'
import { baseUrl } from '@/config/env';
import mixins_var_url from './mixins_var_url'
import mixins_upload from "./mixins_upload"
import  codemirror  from '../../rpt_design/element/vue-codemirror.vue'
import CronInput from 'vue-cron-generator/src/components/cron-input'
import formDialog from '../formDialog'
import zbnode from './node.vue'
  export default {
    provide() {
        return{
            p_this:this
        }
    },
    name: 'landing-page',
    components:{varDetailDialog,codemirror,tinymceDialog, zbnode,CronInput,formDialog},
    mixins:[mixins_var_url,mixins_upload],
    destroyed(){
        this.plumbIns.destroy()
    },
    mounted () {
        let plumbIns = jsPlumb.getInstance()
        this.plumbIns=plumbIns

        if(!Array.isArray(this.config_data.template_output_act))
            this.config_data.template_output_act=[]
        let template_output=this.config_data.template_output_act
        this.fileList.forEach(one=>{
            if(template_output.filter(x=>x.file===one.name).length===0){
            template_output.push({'file':one.name,'canOutput':"false",'wx_file':'','wx_msg':''})
            }
        })      
            
        let _this=this

        plumbIns.ready(()=> {
            this.$nextTick(function(){
                _this.jsPlumbInit()
                _this.reload_line()
                
            })
            
        })
        
    },
    props:['config_data','fileList','curr_report_id','cron_start','cron_str','report_name'],
    watch:{
        cron_start(){
            this.$emit('update:cron_start',this.cron_start); //有效
        },
        curr_report_id(newVal,oldVal){
            if (newVal!=-1){
                this.activeElement.node=null
                this.fresh_plumb()
            }
        }
    },
    computed:{
        this_config_data(){
            return this.config_data
        },
        default_sql(){
            let tmp_sql = ''
            let detail_data=this.activeElement.node
            let last_columns=detail_data.after_append_columns
            if(last_columns==undefined || last_columns.lenght==0)
                last_columns=detail_data.view_columns
            if(last_columns==undefined || last_columns.lenght==0)
                last_columns=detail_data.old_columns
            if (last_columns==undefined || last_columns.length === 0) 
                return tmp_sql
            tmp_sql = 'select \r\n\r\n\t[' + last_columns.join('],\r\n\t[') + ']'
            if (tmp_sql.startsWith(',\r\n')) { tmp_sql = tmp_sql.substr(1) }
            tmp_sql = tmp_sql + ' \r\n\r\nfrom ' + detail_data.name
            return tmp_sql
        },
    },
    data(){
        return {
            ds_data:[],
            cur_ds:"",
            query_result_visible:false,
            files_template_exec_result_visilbe:false,
            template_actSet_dialog_visilbe:false,
            files_template_exec_result:{},
            tplDialog_visible:false,
            sql_visible:false,
            
            varDetailDialog_visible:false,
            tmp_obj:undefined,
            plumbIns:null,
            lineList:[],
            
            urlData_ds_visible:false,
            url_visible:false,
            activeElement:{
                // 可选值 node 、line
                type: undefined,
                // 节点ID
                nodeId: undefined,
                node:undefined,
                // 连线ID
                sourceId: undefined,
                targetId: undefined
            },
            zoom: 1.0,
            loadFinish:false,

            form_input_title: '',
            form_input_obj: {},
            form_input_option: {},
            form_input_visible: false,
            form_input_submit(obj){},
        }
    },
    methods:{
        export_excel(data){
            const ws = XLSX.utils.json_to_sheet(data)
            // 新建book
            const wb = XLSX.utils.book_new()
            // 生成xlsx文件(book,sheet数据,sheet命名)
            XLSX.utils.book_append_sheet(wb, ws, '数据详情')
            // 写文件(book,xlsx文件名称)
            XLSX.writeFile(wb, this.cur_ds+'.xlsx')
        },
        template_actSet_option(){
            let dicData=[];
            this.all_ds.forEach(one => {
                dicData.push({'label':one.name,'value':one.name} )
            });
            this.config_data.vars.filter(x=>x.resultType=='none').forEach(one => {
                dicData.push({'label':one.name,'value':one.name} )
            });
            let ret=
            {                
                column: [
                    { prop: 'file', label: '名字', cell:false,readyonly:true },
                    { prop: 'canOutput', label: '作为模板', type:'select',value:false,dicData: [{label: '是',value: "true"}, {label: '否',value: "false"}] },
                    { prop: 'wx_file', label: '文件发送' },
                    { prop: 'wx_msg', label: '图片或文本发送' },
                    { prop: 'loopForDS', label: '针对数据集循环', width: 80,type:'select',
                    dicData: dicData
                    },
                ] 
            }
            return ret
        },
        template_actSet_dialog_submit(form,done){
            Object.assign(this.activeElement.node, form)
            done()
            this.template_actSet_dialog_visilbe=false
        },
        sql_dialog_submit() {
            this.activeElement.node.sql = (this.tmp_obj == this.default_sql ?  '' : this.tmp_obj )
            this.sql_visible = false
        },
        //以下是模板定义的有关函数
        handleDeleteTpl(tag){
            this.config_data.text_tpls.splice(this.config_data.text_tpls.indexOf(tag), 1);
        },
        handleEditTpl(tag){
            this.tmp_obj=tag
            this.tplDialog_visible=true
        },
        tplDialog_submit(obj){                   
            if(this.config_data.text_tpls===undefined)
                this.config_data.text_tpls=[this.deepClone(obj.newVal)]
            else{
                const text_tpls=this.config_data.text_tpls
                if(obj.old_Val.name){
                let idx=this.findArray(text_tpls,obj.old_Val.name,'name');
                if(idx>=0)
                    text_tpls.splice(idx, 1,obj.newVal);
                }else
                    text_tpls.push(obj.newVal)
            }
        },
        tplDialog_show(){
            this.tmp_obj={name:'',txt:''}
            this.tplDialog_visible=true
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
        //----------------------------
        zoomAdd() {
            if (this.zoom >= 1) {
                return
            }
            this.zoom = this.zoom + 0.1
            this.$refs.efContainer.style.transform = `scale(${this.zoom})`
            this.jsPlumb.setZoom(this.zoom)
        },
        zoomSub() {
            if (this.zoom <= 0) {
                return
            }
            this.zoom = this.zoom - 0.1
            this.$refs.efContainer.style.transform = `scale(${this.zoom})`
            this.jsPlumb.setZoom(this.zoom)
        },
        change_cron(cron) {
            this.$emit('update:cron_str',cron); //有效
            //this.cron_str = cron
        },
    },
    
  }
</script>

<style scoped>
.el-table__row{
    line-height: 30px;
}

/*顶部工具栏*/
.ef-tooltar {
    padding-left: 10px;
    box-sizing: border-box;
    height: 42px;
    line-height: 42px;
    z-index: 3;
    border-bottom: 1px solid #DADCE0;
}
/*画布容器*/
  #efContainer {
    background:
      radial-gradient(
        ellipse at top left,
        rgba(255, 255, 255, 1) 40%,
        rgba(229, 229, 229, .9) 100%
      );
    height: 100vh;
    width: 100vw;
    overflow: scroll;
    flex: 1;
    position: relative;
  }
  .ef-node {
    width: 100px;
    max-height: 25px;
    color: #606266;
    background: #f6f6f6;
    font-size: 14px;
    text-align: center;
    line-height: 20px;
    font-family: sans-serif;
    border-radius: 4px;
    margin-right: 60px;
    border: 1px solid #3a3939;
    overflow: wrap
  }
  .ef-node-canDrop:hover {
    /* 设置拖拽的样式 */
    cursor: crosshair;
  }
  .ef-node:hover {
    color: black;
    /*box-shadow: #1879FF 0px 0px 12px 0px;*/
    background-color: #F0F7FF;
    border: 1px solid black;
}
/*节点激活样式*/
.ef-node-active {
    color: black;
    
    font-weight: bolder;
    border: 1px solid black;
}
  .line-wrap {
    display: flex;
    margin-bottom: 20px;
  }

  .ef-node-error{
      background-color: red;
  }
    .ef-node-success{
      background-color:forestgreen;
    color: white;
  }
  .ef-node-form-header{
      background:#d0cbcb;color:#4f4c4c;
  }
  .ef-node-form-header{

  }
  
  svg .jtk-connector path{
      stroke:red
  }
</style>