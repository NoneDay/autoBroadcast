<template>
    <div style="height: calc(100vh);">
        <el-row>
            <!--顶部工具菜单-->
            <el-col :span="24">
                <div class="ef-tooltar">
                    <el-button type="text" icon="el-icon-platform-eleme" size="large" @click="addUrlFrom('html')"></el-button>
                    <el-divider direction="vertical"></el-divider>
                    <i class="el-icon-notebook-2" @click="addUrlFrom('file')"></i>
                    <el-divider direction="vertical"></el-divider>
                    <img style="width:20px;height:20px;margin-top: 5px;" src="svg/sql.png" @click="addUrlFrom('sql')"></img>
                    
                    <el-divider direction="vertical"></el-divider>
                    <el-button type="text" icon="el-icon-plus" size="large" @click="zoomAdd"></el-button>
                    <el-divider direction="vertical"></el-divider>
                    <el-button type="text" icon="el-icon-minus" size="large" @click="zoomSub"></el-button>
                    
                    <el-divider direction="vertical"></el-divider>
                     {{config_data.ds_queue}}
                </div>
            </el-col>
        </el-row>
        <div style="display: flex;height: calc(100% - 47px);">
            <div   id="efContainer" ref="efContainer">
                <div  class="line-wrap" :key="idx" v-for="(data_from,idx) in config_data.data_from"  >
                    <div  :id="'URL:'+idx" @click="clickNode(data_from,'URL')"  @dblclick="dblclickNode(data_from,'URL')" :class="nodeClass(data_from,'URL')">
                        {{data_from.desc ? data_from.desc:(data_from.type=='file'?data_from.url: data_from.type) }} 
                    </div>
                    <div>
                        <div :key="idx1" class="line-wrap"  v-for="(ds,idx1) in data_from.ds" >
                            <div  >
                                <template v-if="!['sql','file'].includes( data_from.type)">
                                <div :id="'裁剪:'+ds.name" @click="clickNode(ds,'裁剪')" @dblclick="dblclickNode(ds,'裁剪')" :class="nodeClass(ds,'裁剪')">裁剪:{{ds.name}} </div>
                                <div :id="'昨日:'+ds.name" @click="clickNode(ds,'昨日')" @dblclick="dblclickNode(ds,'昨日')"  :class="nodeClass(ds,'昨日')" v-if="ds.backup">昨日 </div>
                                <div :id="'上次:'+ds.name" @click="clickNode(ds,'上次')" @dblclick="dblclickNode(ds,'上次')"  :class="nodeClass(ds,'上次')" v-if="ds.backup">上次 </div>
                                </template>
                                <div v-else style="width:164px">
                                    
                                </div>
                            </div>
                                <div :id="'合并:'+ds.name" @click="clickNode(ds,'合并')" @dblclick="dblclickNode(ds,'合并')"  :class="nodeClass(ds,'合并')" >合并 

                                </div>
                                <div :id="'最终:'+ds.name" @click="clickNode(ds,'最终')" @dblclick="dblclickNode(ds,'最终')"  :class="nodeClass(ds,'最终')" >最终:{{ds.name}} 
                                    
                                </div>
                            <div style="width:200px;border:1px black dotted" :id="'来自:'+ds.name" v-if="config_data.vars.filter(x=>x.ds==ds.name).length>0">
                                <el-tag  type="danger"  v-for="one_var in config_data.vars.filter(x=>x.ds==ds.name)" 
                                    :key="one_var" style="margin: 2px;"
                                    closable :disable-transitions="false"  @close="handleDeleteVar(one_var)" @click="handleEditVar(one_var)"
                                    >
                                    {{ one_var.name }}
                                </el-tag>
                            </div>
                        </div>
                    </div>
                
                </div>
                <div style="width:150px; min-height:10px;border:1px black dotted;margin-bottom: 10px;">
                    <div style="background:#d0cbcb;color:#4f4c4c">数据文件</div>
                    <template v-if="config_data.template_output_act">
                        <div class="line-wrap" :key="idx" v-for="(data_from,idx) in config_data.template_output_act.filter(x=>x.canOutput=='false')"  >
                            <div  :id="'文件:'+data_from.file" @click="clickNode(data_from,'文件')"  @dblclick="dblclickNode(data_from,'文件')" :class="nodeClass(data_from,'文件')">{{data_from.file}} </div>
                        </div>
                    </template>
                </div>
                <div class="line-wrap" >
                <div style="width:150px;min-height:10px;border:1px black dotted;margin-bottom: 10px;">
                    <div style="background:#d0cbcb;color:#4f4c4c">模板文件</div>
                    <template v-if="config_data.template_output_act">
                        <div class="line-wrap" :key="idx" v-for="(data_from,idx) in config_data.template_output_act.filter(x=>x.canOutput=='true')"  >
                            <div  :id="'模板:'+data_from.file" @click="clickNode(data_from,'模板')"  @dblclick="dblclickNode(data_from,'模板')" :class="nodeClass(data_from,'模板')">{{data_from.file}} </div>
                        </div>
                    </template>
                </div>
                </div>
                <div class="line-wrap" >
                <div style="width:250px;border: 1px gray dotted">
                    <el-upload
                    ref="upload"
                    class="upload-demo"
                    :data="{'curr_report_id':curr_report_id}"
                    action="./aps/mg/file/posts"
                    :limit="10"
                    :http-request="myUpload"
                    :on-preview="file_handlePreview"
                    :on-remove="file_handleRemove"
                    :on-error="file_error"
                    :on-success="file_success"
                    :on-change="file_change"
                    :file-list.sync="fileList"
                    >
                    <el-button slot="trigger" size="small" type="primary">选取文件</el-button>
                    <div slot="tip" class="el-upload__tip">只能上传txt/xlxs/html/csv/md文件，且不超过500kb</div>
                    </el-upload>                        
                </div>
                <el-card class="box-card" style="width:250px;border: 1px gray dotted" >
                    <div slot="header" class="clearfix">
                    <span>文本模板</span>
                    <el-button style="float: right; padding: 3px 0"  @click="tplDialog_show" type="text">新建</el-button>
                    </div>
                    <el-tag type="danger"  v-for="tag in config_data.text_tpls" :key="tag.name" style="margin: 10px;"
                    closable :disable-transitions="false"  @close="handleDeleteTpl(tag)" @click="handleEditTpl(tag)"
                    >{{tag.name}}</el-tag>         
                    
                </el-card>
                </div>
            </div>
            
            <!-- 右侧表单 -->
            <div style="width: 300px;border-left: 1px solid #dce3e8;background-color: #FBFBFB">
                <div class="ef-node-form">
                    <div class="ef-node-form-header">
                        编辑
                    </div>
                    <div class="ef-node-form-body">
                        <div v-if="activeElement.type=='URL'">
                            网页地址：
                            <el-input type="textarea" autosize v-model="activeElement.node.url" placeholder="请输入内容"></el-input>
                            类型：{{activeElement.node.type}}
                        </div>
                        <div v-if="['裁剪','昨日','上次','合并','最终',].includes(activeElement.type)">
                            数据集名称
                            <el-input v-model="activeElement.node.name" placeholder="请输入内容"></el-input>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <el-dialog :visible.sync="urlData_ds_visible" v-if="urlData_ds_visible"  label="。。" :close-on-click-modal="false" append-to-body>
            <avue-form :option="urlData_ds_option()" v-model="tmp_obj" @submit="urlData_ds_submit"> </avue-form>
        </el-dialog>
        <el-dialog :visible.sync="url_visible" v-if="url_visible"  label="。。" :close-on-click-modal="false" append-to-body>
            <avue-form :option="url_option()" v-model="tmp_obj" @submit="url_submit"> 
            </avue-form>
        </el-dialog>
        <var-detail-dialog 
            :visible.sync="varDetailDialog_visible" 
            v-if="varDetailDialog_visible" :all_ds="all_ds" 
            :target_obj="tmp_obj"
            @submit="varDetailDialog_submit" 
        ></var-detail-dialog>
    </div>
</template>

<script>
import {jsPlumb} from 'jsplumb'
import varDetailDialog from '../var_detail_dialog.vue'
import lodash from 'lodash'
import mixins_var_url from './mixins_var_url'
import mixins_upload from "./mixins_upload"
  export default {
    name: 'landing-page',
    components:{varDetailDialog},
    mixins:[mixins_var_url,mixins_upload],
    mounted () {
      let plumbIns = jsPlumb.getInstance(this)
      this.plumbIns=plumbIns
      
        
      let _this=this

      plumbIns.ready(()=> {
        _this.jsPlumbInit()
       _this.reload_line()
      })
        
    },
    props:['config_data','fileList'],
    data(){
        return {
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
        }
    },
    methods:{


        nodeClass(ds,type) {
            return {
                'ef-node': true,
                'ef-node-canDrop': ['裁剪','昨日','上次','最终',].includes(type),
                'ef-node-active': this.activeElement.node ==ds && this.activeElement.type ==type
            }
        },
        dblclickNode(node,type){
            this.activeElement.node=node
            this.activeElement.type=type
            this.tmp_obj=node
            if(this.activeElement.type=="URL"){
                this.url_visible=true
            }
            else
                this.urlData_ds_visible=true
        },
        clickNode(node,type){
            this.activeElement.node=node
            this.activeElement.type=type
        },

    
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
    },
    
  }
</script>

<style scoped>


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
    height: 25px;
    color: #606266;
    background: #f6f6f6;
    border: 2px solid rgba(0, 0, 0, 0.05);
    text-align: center;
    line-height: 25px;
    font-family: sans-serif;
    border-radius: 4px;
    margin-right: 60px;
    overflow: hidden
  }
  .ef-node-canDrop:hover {
    /* 设置拖拽的样式 */
    cursor: crosshair;
  }
  .ef-node:hover {
    background-color: #F0F7FF;
    /*box-shadow: #1879FF 0px 0px 12px 0px;*/
    background-color: #F0F7FF;
    border: 1px dashed #1879FF;
}
/*节点激活样式*/
.ef-node-active {
    background-color: #F0F7FF;
    /*box-shadow: #1879FF 0px 0px 12px 0px;*/
    background-color: #F0F7FF;
    border: 1px solid #1879FF;
}
  .line-wrap {
    display: flex;
    margin-bottom: 10px;
  }
  
</style>