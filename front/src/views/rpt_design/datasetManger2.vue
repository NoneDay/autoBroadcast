<template>
<el-dialog  style="text-align: left;" :inline="true"
    :visible.sync="dialogVisible" :title="'数据管理'" 
        :close-on-click-modal="false"  @close="dialogVisible=false" 
          direction="btt" append-to-body  :fullscreen="true"
    >
    <ExprEditorDialog  :visible.sync="ExprEditorDialog_visible" 
        :target_obj="url_param" 
        :prop="{display:'引用报表的参数',val:'_default_value'}" 
        :report="context.report">
    </ExprEditorDialog>
    <el-container style="height: 100%; border: 1px solid #eee">
    <el-aside width="200px" style="background-color: rgb(238, 241, 246)">
    
    <el-row>
        <div>
            <span>数据集</span>
            
            <el-dropdown @command="new_dataset($event)" style="float: right; padding: 3px 0">
                <span class="el-dropdown-link">
                    新增<i class="el-icon-more"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                    <el-dropdown-item command="sql">来自数据库</el-dropdown-item>
                    <el-dropdown-item command="from">来自其他数据集</el-dropdown-item>
                    <el-dropdown-item command="memory">内存数据（sqlite）</el-dropdown-item>
                    <el-dropdown-item command="cr" style="color: gray">来自组件报表</el-dropdown-item>
                    <el-dropdown-item  command="csv" style="color: gray">来自excel文件</el-dropdown-item>
                    <el-dropdown-item  command="api" style="color: gray">来自API调用</el-dropdown-item>
                    <el-dropdown-item  command="html" style="color: gray">来自有Table的html网页</el-dropdown-item>
                </el-dropdown-menu>
            </el-dropdown>
        </div>
    </el-row>
    <el-row v-for="(ds,ds_idx) in all_dataSet" :key="ds+ds_idx" :style="{'background-color':action_target==ds?'#c5f3e0':'#fff'}"> <!-- https://www.iconfont.cn -->
        <svg v-if="ds._type=='csv'" class="icon" style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1709"><path d="M903.2 315.4V950c0 15.7-12.7 28.4-28.4 28.4H217.3c-12 0-21.6-9.7-21.6-21.6V98.7c0-8.8 7.1-15.9 15.9-15.9h443.1c0.9 0 1.4 1.1 0.8 1.8-0.4 0.4-0.4 1.1 0.1 1.5l247.5 228.6c0 0.1 0.1 0.4 0.1 0.7z" fill="#F4F4F4" p-id="1710"></path><path d="M654.8 300.1V82.8L903.3 315H669.7c-8.2 0-14.9-6.7-14.9-14.9zM431.4 374.1H213.2c-58.4 0-105.7-47.3-105.7-105.7 0-58.4 47.3-105.7 105.7-105.7h218.2c58.4 0 105.7 47.3 105.7 105.7 0.1 58.3-47.3 105.7-105.7 105.7z" fill="#4BC929" p-id="1711"></path><path d="M386.1 275.1c-1.1-1.7-2.3-3.1-3.4-4.3-4.1-4.2-9.6-7.1-16.5-8.5-4.5-1.1-8.5-1.4-11-1.5h-64.3c-8.6 0.1-15-1.7-18.5-5.3-0.7-0.7-1.2-1.4-1.6-2.1v-0.3c-1.2-2-1.9-4.5-1.9-7.5v-1-1.1c0.1-4.2 1.3-7.5 3.9-9.9 5.4-5.1 15.5-5.8 18.6-5.7H383.3c4 0 7.3-3.3 7.3-7.3s-3.3-7.3-7.3-7.3h-91.4c-2.5-0.1-17.2-0.2-27.6 8.3h-0.4c-0.6 0.5-1.2 1.1-1.8 1.7-2 2.1-4.3 5.1-5.8 9.1v0.3c-1.3 3.4-1.9 7-1.9 11v0.5c-0.2 7.6 1.8 13.2 4.3 17.1 0.5 0.8 1 1.5 1.6 2.2v0.1l0.3 0.3c0.1 0.1 0.1 0.2 0.2 0.2l0.3 0.3 0.2 0.2 0.3 0.3c0 0.1 0.1 0.1 0.1 0.2 0.1 0.2 0.3 0.3 0.4 0.5 4.1 4.2 9.6 7.1 16.5 8.5 4.5 1.1 8.5 1.4 11 1.5H354c3.2 0 6.1 0.2 8.7 0.7 3.4 0.8 7 2.3 9.5 4.7 0.8 0.7 1.4 1.5 1.9 2.4 0.2 0.3 0.3 0.5 0.4 0.8 0 0.1 0.1 0.2 0.1 0.3 0.1 0.2 0.2 0.4 0.3 0.5 0 0.1 0.1 0.2 0.1 0.3 0.1 0.2 0.1 0.3 0.2 0.5 0 0.1 0.1 0.3 0.1 0.4 0.1 0.2 0.1 0.3 0.2 0.5 0 0.1 0.1 0.3 0.1 0.4 0 0.2 0.1 0.3 0.1 0.5 0 0.1 0 0.3 0.1 0.5 0 0.2 0.1 0.4 0.1 0.5v0.5c0 0.2 0 0.4 0.1 0.6V293c-0.1 4.2-1.3 7.5-3.9 9.9-2.5 2.4-6.1 3.8-9.5 4.7-2.6 0.5-5.5 0.7-8.7 0.7h-78.3c-0.7 0-1.5 0.1-2.1 0.3h-12c-4 0-7.3 3.3-7.3 7.3s3.3 7.3 7.3 7.3h91.4c1.4 0.1 7 0.1 13.5-1.5 5.8-1.3 10.7-3.5 14.5-6.8 0.6-0.5 1.2-1.1 1.8-1.7 2-2.1 4.3-5.1 5.8-9.1 1.2-3.1 1.9-6.9 1.9-11.3v-0.7-0.5-0.2-0.1c0-7.1-1.9-12.4-4.3-16.2z" fill="#FFFFFF" p-id="1712"></path><path d="M716 509.4H369.6c-5.4 0-9.8 4.4-9.8 9.8v312.5c0 6.2 5.1 11.3 11.3 11.3h341.6c7.9 0 14.4-6.4 14.4-14.4v-308c0-6.2-5-11.2-11.1-11.2z m-11.2 22.3v83h-89.6v-83h89.6zM592.9 819.2h-99v-81.6h99v81.6zM494 715.3V637h99v78.4h-99z m-22.3 0h-88.9V637h88.9v78.3zM494 533.1h99v81.6h-99v-81.6zM615.2 637h88.9v78.4h-88.9V637zM382.1 531.7h89.6v83h-89.6v-83z m0 288.9v-83h89.6v83h-89.6z m322.7 0h-89.6v-83h89.6v83z" fill="#4BC929" p-id="1713"></path></svg>
        <svg v-if="ds._type!='csv' && ds._type!='cr'" class="icon" style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4244"><path d="M793.6 682.8288V460.8H243.2v221.7088C108.3008 675.904 0 565.5424 0 431.5904c0-129.856 98.1248-234.56 230.4-251.2512C281.6 79.8336 388.224 12.8 512 12.8c157.8496 0 285.8496 108.8768 315.7248 251.2384C934.4 272.4096 1024 364.544 1024 473.3824c0 117.2864-93.8752 209.4464-213.376 209.4464H793.6z" fill="#1989FA" opacity=".3" p-id="4245"></path><path d="M518.4 833.4336c-151.9872 0-275.2-42.9824-275.2-96V864c0 53.0176 123.2128 96 275.2 96S793.6 917.0176 793.6 864v-126.5664c0 53.0176-123.2128 96-275.2 96z m0-197.184c-151.9872 0-275.2-42.9696-275.2-96V672c0 53.0176 123.2128 96 275.2 96S793.6 725.0176 793.6 672V540.2496c0 53.0304-123.2128 96-275.2 96zM243.2 467.2c0 53.0176 123.2128 96 275.2 96S793.6 520.2176 793.6 467.2c0-53.0176-123.2128-96-275.2-96S243.2 414.1824 243.2 467.2z" fill="#1989FA" p-id="4246"></path></svg>
        <svg v-if="ds._type=='cr'" class="icon" style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7477"><path d="M912.027826 661.993739l-352.300522 211.389218a70.077217 70.077217 0 0 1-35.216695 8.770782c-12.733217 0-25.510957-2.938435-35.261218-8.770782l-352.300521-211.389218c-19.456-11.664696-19.456-30.630957 0-42.25113l59.748173-35.84 271.84974 163.127652c15.62713 9.305043 35.439304 14.425043 55.963826 14.425043 20.48 0 40.292174-5.12 55.919304-14.425043l271.849739-163.127652 59.748174 35.84c19.456 11.664696 19.456 30.586435 0 42.25113z" fill="#2B3B94" p-id="7478"></path><path d="M912.027826 501.092174l-352.300522 211.433739a70.077217 70.077217 0 0 1-35.216695 8.770783c-12.733217 0-25.510957-2.938435-35.261218-8.770783l-352.300521-211.433739c-19.456-11.664696-19.456-30.630957 0-42.251131L196.697043 422.956522l271.84974 163.127652c15.62713 9.394087 35.439304 14.514087 55.963826 14.514087 20.48 0 40.292174-5.12 55.919304-14.514087L852.324174 422.956522l59.748174 35.884521c19.411478 11.664696 19.411478 30.630957-0.044522 42.251131z" fill="#2B3B94" p-id="7479"></path><path d="M912.027826 340.23513l-352.300522 211.43374a70.077217 70.077217 0 0 1-35.216695 8.770782c-12.733217 0-25.510957-2.938435-35.261218-8.770782L136.94887 340.23513c-19.456-11.620174-19.456-30.630957 0-42.25113l352.300521-211.433739c9.750261-5.832348 22.528-8.726261 35.261218-8.726261 12.688696 0 25.466435 2.893913 35.216695 8.726261l352.300522 211.433739c19.456 11.664696 19.456 30.630957 0 42.25113z" fill="#2B3B94" p-id="7480"></path></svg>
        <div @click="action_target=ds"  style="display: inline-block;width:calc(100% - 50px)">{{ds._name}} </div>
        <el-button @click="delete_dataset(ds,ds_idx)" circle plain type="danger" size="mini" icon="el-icon-minus"
            style="padding: 4px;margin-left: 5px;float:right">
        </el-button>
         
    </el-row> 
   </el-aside>
   <el-main>

        <el-form :inline="true" class="demo-form-inline" v-if="action_target!=null">
            <el-row><el-col :span="6">
                <el-form-item label="名字"><el-button type="primary" @click="update_name" >{{action_target._name}}</el-button ></el-form-item>
            </el-col>
            
            <el-col v-if="action_target._type=='sql'|| action_target._type=='db'" :span="8">
                <el-form-item label="数据源">
                    <el-select v-model="action_target._dataSource" placeholder="数据源">
                        <el-option  v-for="(one,index) in context.report.datasources" :key="one+index" :label="one.name" :value="one.name"></el-option>
                    </el-select>
                </el-form-item>
                </el-col>  <el-col :span="4">
                <el-form-item label="类型">{{action_target._type}} </el-form-item> </el-col>
                <el-button  v-if="['memory','sql','userDefine'].includes(action_target._type)" 
                 @click="preview">取数</el-button>
            </el-row>
            <el-row  v-if="['memory','sql','userDefine'].includes(action_target._type)">
                <el-col :span="24">
             <codemirror  
                        ref="editor" 
                        v-model="action_target.__text" 
                        style="height:100%"
                        :options="{tabSize: 4, mode: 'text/x-sql', lineNumbers: true,line: true,}"  
            /></el-col>
            </el-row>
            <el-row v-if="['sql','db'].includes(action_target._type) " :span="6">
                <div v-if="dataLengthList(action_target._name).length>1">
                    <el-tag v-for="(one,index) in dataLengthList(action_target._name)" :key="one+index" 
                        @click="url_choose_get(index)"
                        :style="{'font-weight':(action_target.get==index?'bold':'')}">
                        {{index }}
                     </el-tag>
                </div>     
            </el-row>

            <el-row v-if="action_target._type=='cr'">
                <el-col :span="10">
                    <el-input v-model="action_target._dataSource" placeholder="请输入报表地址"></el-input> 
                </el-col>
                 <el-col :span="2"><el-button @click="cr_run">取数</el-button> </el-col>
                 <el-col :span="6" style="font-weight:800" > 
                     当前选择的是 ： 
                     <span v-if="action_target.get">
                     {{action_target.get.substring(0,2)=='tb'?'表格':'数据集' }}{{action_target.get.substring(3)}} 
                     </span >
                     </el-col>
            </el-row>
            
            <el-table stripe border  :height="250" v-if="action_target.url_param" 
                    :data="action_target.url_param"  
                >
                <el-table-column prop="_prompt" label="参数说明"> </el-table-column>
                <el-table-column prop="_name" label="参数名"> </el-table-column>
                <el-table-column prop="_default_value" label="值">
                    <template slot-scope="scope">
                        <el-input v-model="scope.row._default_value" 
                        style="width:80%"
                        placeholder=""></el-input> 
                        <el-button @click="paramDialog_open(scope.row)"
                         circle
                         type="success"
                         size="mini"
                         icon="el-icon-edit"
                         style="padding: 4px;margin-left: 5px"></el-button>
                    </template>
                </el-table-column>
            </el-table>
 
            <el-row v-if="action_target._type=='cr'"><el-col :span="10">
                <div v-if="action_target.report_result">
                    <el-tag v-for="(one,index) in Object.keys(action_target.report_result.data)" :key="one+index" type="success" @click="url_choose_get('tb:'+one)"  :style="{'font-weight':(action_target.get=='tb:'+one?'bold':'')}">{{one }}</el-tag>
                    <el-tag v-for="(one,index) in Object.keys(action_target.report_result.dataSet)" :key="one+index" @click="url_choose_get('ds:'+one)" :style="{'font-weight':(action_target.get=='ds:'+one?'bold':'')}">{{one }}</el-tag>
                </div>            
            </el-col>
            </el-row>
             <el-row v-if="action_target._type=='from'"><el-col :span="4">
                 挑选数据集
                <el-select v-model="action_target._dataSource" >
                    <el-option  v-for="(ds,index) in all_dataSet.filter(x=> ['db','sql','cr'].includes(x._type) 
                                                                            && ((x._type!='cr' && dataLengthList(x._name).length>1) )|| x._type=='cr')" 
                        :key="ds._name+index" :label="ds._name" :value="ds._name"></el-option>
                </el-select> 
                </el-col>
                 <el-col :span="4">
                     挑选内部数据集
                    <el-select v-model="action_target.__text" 
                            v-if="this.action_target._dataSource!=''  && ['db','sql'].includes(all_dataSet.find(a=>a._name==action_target._dataSource)._type)  " 
                    >
                        <el-option v-for="(one,index) in dataLengthList(action_target._dataSource).slice(1)" 
                            :key="index" type="success" @click="url_choose_get(one)"  :label="one" :value="one" >{{one }}</el-option>
                    </el-select>  
                    <el-select v-model="action_target.__text" v-if="this.action_target._dataSource!='' && all_dataSet.find(a=>a._name==this.action_target._dataSource)._type=='cr'" >
                        <el-option v-for="(one,index) in Object.keys(all_dataSet.find(a=>a._name==this.action_target._dataSource).report_result.data)" 
                            :key="one+index" type="success" @click="url_choose_get('ds:'+one)"  :label="one.name" :value="'tb:'+one" >{{one }}</el-option>
                        <el-option v-for="(one,index) in Object.keys(all_dataSet.find(a=>a._name==this.action_target._dataSource).report_result.dataSet)" 
                            :key="one+index" type="success" @click="url_choose_get('tb:'+one)"  :label="one.name" :value="'ds:'+one" >{{one }}</el-option>
                    </el-select> 
                     
                </el-col>
            </el-row>
           


            <div >
            <el-upload v-if="action_target._type=='csv'" class="upload-demo" action :auto-upload="false" :show-file-list="false" :on-change="choose_file"
            >
            <el-button size="small" type="primary">请选择导入excel</el-button>
            </el-upload>
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
            </div>
       </el-form>
   </el-main>
  </el-container>
          <span slot="footer" class="dialog-footer">
            <el-button @click="dialogVisible = false">取 消</el-button>
            <el-button @click="print_json">print_json</el-button>
            <el-button type="primary" @click="handleSubmit">确 定</el-button>
        </span>
</el-dialog>
</template>

<script>

import  codemirror  from './element/vue-codemirror.vue'
import ExprEditorDialog from './ExprEditorDialog.vue'
import {request} from 'axios'
import {convert_csv_to_json,convert_array_to_json } from "./utils/util"
export default {
    name: "datasetManger2",
    components: {codemirror,ExprEditorDialog},
    props: { visible: Boolean},
    inject: ["context"],
    data(){
        return {
            all_dataSet:[],
            datasetDialog_visible:false,
            action_target:null,
            action_name:"",
            dialogVisible:false,
            url_param:{},
            ExprEditorDialog_visible:false,
            currentPage: 1,
            pageSize: 10
            
        }
    },watch:{
        dialogVisible(val) {
            this.$emit('update:visible', val)
        },
        visible(val) {
            if(val){
                this.all_dataSet=JSON.parse(JSON.stringify(this.context.report.dataSets.dataSet))
            }
            this.dialogVisible=val
            this.$emit('update:visible', val)
        },
        from(){

        }
    
    },
    mounted(){
        this.all_dataSet=JSON.parse(JSON.stringify(this.context.report.dataSets.dataSet))
        this.dialogVisible=true
        
    },
    computed:{
        tableData(){
            if(this.action_target._type=="csv" && this.action_target.__text.length>0)
            {
              return convert_csv_to_json(this.action_target.__text)
            }
            if(this.action_target._type=="from" && this.action_target._dataSource!="" && this.action_target.__text!="")
            {
                let cur_ds=this.all_dataSet.find(a=>a._name==this.action_target._dataSource)
                if(cur_ds.report_result){
                    let ret=this.choose_cr_ds(cur_ds.report_result,this.action_target.__text)
                    if (ret && ret.length>1){
                        this.action_target._fields=JSON.stringify(Object.keys(ret[0]))
                        return ret
                    }
                }
                else
                {
                    let data=this.context.report_result.dataSet[cur_ds._name][this.action_target.__text||0]
                    if (data && data.length>1){
                        this.action_target._fields=JSON.stringify(data[0])
                        return convert_array_to_json(data)
                    }
                }
                    
            }
            if( ['memory','sql','userDefine'].includes(this.action_target._type) )
            {
                if(this.context.report_result?.dataSet && this.action_target._name)
                {
                    let data=this.context.report_result.dataSet[this.action_target._name][this.action_target.get||0]
                    if (data){
                        return convert_array_to_json(data)
                    }
                }
            }
            if(this.action_target._type=="cr"  && this.action_target.get){
                return this.choose_cr_ds(this.action_target.report_result,this.action_target.get)
            }
            return []
        }
    },
    
    methods:{
        preview(){

        },
        paramDialog_open(row){
            this.url_param=row
            this.ExprEditorDialog_visible=true;
        },
        
        dataLengthList(ds_name){
            let ret=[]
            let i=0
            if (ds_name!='' && Object.keys(this.context.report_result).length>1){
                this.context.report_result.dataSet[ds_name].forEach(one=>
                    {
                        ret.push(i);
                        i++;
                    }
                ) ;
            }
            return ret
        },
        choose_cr_ds(ds,name){
            if(name.toString().startsWith("ds:")){
                let data=ds.dataSet[name.slice(3)]
                if (data){
                    return convert_array_to_json(data[0])
                }
            }else if(ds && name.toString().startsWith("tb:")){
                let data=ds.data[name.slice(3)]
                if (data && data.type=="common"){
                    return convert_array_to_json(data.tableData.slice (data.extend_lines[0],data.extend_lines[1]+1),0,100,data.columns)
                }
                if (data && data.type=="large"){
                    return convert_array_to_json(data.data[0],0,100,data.columns)
                }
            } 
            return []
        },
        url_choose_get(name){
            this.$set(this.action_target,"get",name)
            this.currentPage=1
        },
        cr_run(){
            let _this=this
            const loading = this.$loading({
                    lock: true,
                    text: 'Loading',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                    });
            request({
                method: 'get',
                url: this.action_target._dataSource,
                headers:{"needType": "json","worker_no":"14100298"},
            }).then(response => {
                loading.close();
                console.log(response.data);
                this.$set(this.action_target,"report_result",response.data)
                let param=[]
                this.action_target.report_result.form.forEach(ele=>{
                    param.push({_name:ele.name,_prompt:ele.prompt,_default_value:ele.default_value})
                })
                if(this.action_target.url_param){                    
                    Object.assign(param,this.action_target.url_param)
                }
                this.$set(this.action_target,"url_param",param)                
            }).catch(error=> { 
                loading.close();
                this.$message.error(JSON.stringify(error.response.data));
            })


        },
        print_json(){
            this.all_dataSet.forEach(one=>{
                 if(one._type=='cr'){
                     delete one.report_result
                 }
             })
            console.info(JSON.stringify(this.all_dataSet,null,4))
        },
        handleSubmit(){
            this.all_dataSet.forEach(one=>{
                if(one._type=='cr'){
                    delete one.report_result
                }
            })
            this.context.report.dataSets.dataSet.splice(0)
            JSON.parse(JSON.stringify(this.all_dataSet)).forEach(ele=>{
                this.context.report.dataSets.dataSet.push(ele)
            })
            this.dialogVisible=false
        }, 
        has_name(name){
          if(this.context.allElementSet.has(name)){
            this.$alert("名字不能已有元素名称重复");
            return true;  
          }
          if(this.all_dataSet.filter(x=>x._name==name).length>0){
            this.$alert("名字不能重复");
            return true;
          }
          return false
        },
        
        update_name(){
            let _this=this
            this.$prompt('请输入数据集名字', '名字', 
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                inputPattern:/^[a-zA-Z\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5]*$/,
                inputValue:this.action_target._name
            })
            .then( ({ value }) => {
                if(_this.action_target._name==value)
                    return
                if(_this.has_name(value))
                    return
                _this.action_target._name=value
            }).catch(error=>error) 
        },
        new_dataset(command, node,data){
            let _this=this
            this.$prompt('请输入名字', '名字', 
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                inputPattern:/^[a-zA-Z\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5]*$/,
                inputValue:"ds"
            }).catch(error=>error)
            .then( ({ value }) => {
                 if(_this.has_name(value))
                    return
                _this.action_target={__text:'',_dataSource:'',_name:value,_type:command,_fields:"[]"}
                if(command=="from"){
                    _this.action_target._dataSource=""
                    _this.action_target.__text=""
                }
                _this.all_dataSet.push(_this.action_target )
            })           
        },
        delete_dataset(item,idx){
            let len=this.all_dataSet.length
            this.all_dataSet.splice(idx, 1)
            if(len==1){
                this.action_target=null
            }
            else if(idx==len-1){
                this.action_target=this.all_dataSet[len-2]
            }else{
                this.action_target=this.all_dataSet[idx]
            }
        },
    choose_file(file) {
      this.file = file.raw;//这是element的导入数据选择，必须要添加.raw才能获取，其他表单不需要
      // console.log(file);//上传文件信息
      this.importExcel(this.file)
    },
    importExcel(file) {//来自euiadmin ，在https://github.com/chenboyan1/Euiadmin
      
      let _this=this
      //声明一个文件读取器
      const fileReader = new FileReader();
      //文件读取成功时触发事件
      fileReader.onload = (ev) => {
        try {
          //读取的文件;
          const data = ev.target.result;
          //以二进制流方式读取得到整份excel表格
          const workbook = XLSX.read(data, { type: "binary" });
          // 循环遍历excel的sheet对象
          let isfirst=true
          Object.keys(workbook.Sheets).forEach((sheet) => {
            if(!isfirst)
                return false
            _this.$set(_this.action_target,"__text",XLSX.utils.sheet_to_csv(workbook.Sheets[sheet]))
            _this.action_target._fields=JSON.stringify(_this.action_target.__text.split("\n")[0].split(","))
            isfirst=false
            return false
          });
          // 自定义事件，比如校验excel数据。转换数据格式…
          //console.log(_this.excelTableData)//未转换key值的数据
          // this.changeKey(excelData)//调用转换key值
        } catch (e) {
          this.$message.danger('文件类型不正确');
        }
      };
      //读取文件
      fileReader.readAsBinaryString(file);
    },
    }
}
</script>

<style>
.el-dialog__body {height: calc(100% - 120px);}
</style>