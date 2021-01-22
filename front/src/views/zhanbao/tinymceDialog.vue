<template>
     <div id="tinymceDialog">
        <el-dialog  :visible.sync="dialogVisible" :title="'模板输出生成:'" 
        :close-on-click-modal="false"  @close="close"  :fullscreen="fullscreen"
          direction="btt" append-to-body  @submit="handleSubmit"
        >
        <div slot="title" >
          <span class="el-dialog__title">模板输出生成</span>
          <div style="right: 40px;    top: 20px;    position: absolute;">
            <i @click="fullscreen=!fullscreen"
              class="el-icon-full-screen"></i>
          </div>
        </div>
        <el-form :inline="true" class="demo-form-inline">
           <el-form-item label="名字"><el-input v-model="obj.name" placeholder="请输入名字："></el-input></el-form-item>
           <el-form-item label="发送给："><el-input v-model="obj.wx_msg" placeholder="请输入发送给谁"></el-input> </el-form-item>
            <el-form-item label="针对这个数据集中的每条数据执行模板：">
            <el-select v-model="obj.loopForDS" clearable  placeholder="数据集">
            <el-option
              v-for="item in all_ds"
              :key="item.name"
              :label="item.name"
              :value="item.name">
            </el-option>
          </el-select>
          </el-form-item>
        </el-form>
          <tinymce v-model="obj.txt" :height="300" v-if="dialogVisible"  
          :initProps="initProps" ref="tinymce"
          menubar="view" :toolbar="['undo redo emoticons | code']"
           >
            <el-dropdown trigger="click" @command="addLoopVar" style="color: #ef190e;" v-if="obj.loopForDS">
              <span class="el-dropdown-link" >
                循环数据集的字段<i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-row style="min-width:100px;max-width:400px">
                  <el-dropdown-item  command="_idx_"><el-tag type="danger">序号：_idx_</el-tag></el-dropdown-item>
                  <el-col :span="12" v-for="item in all_ds.find(x=>x.name==obj.loopForDS).last_columns" :key="item">
                    <el-dropdown-item  :command="item"><el-tag type="danger">{{item}}</el-tag></el-dropdown-item>
                  </el-col>
                </el-row>
              </el-dropdown-menu>
            </el-dropdown>

            <el-dropdown trigger="click" @command="addVar" style="color: #ef190e;">
              <span class="el-dropdown-link" style="color: #ef190e;">
                添加预定义变量<i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-row style="min-width:100px;max-width:400px">
                  <el-col :span="12" v-for="item in [
                  '_今日_|例:1月20日',
                  '_昨日_|不带0（1月19日）',
                  '_时分_|例（15时55分）',
                  '_月_|不带前面的0',
                  '_日_|不带前面的0',
                  '_时_|例（15）',
                  '_月0_|带前面的0',
                  '_日0_|带前面的0',
                  '_年_|例（2021）',
                  '_上年_|例（2020）',
                  '_今天_|带前面的0（2021-01-02）',
                  '_昨天_|带前面的0（2021-01-01）',
                  '_whatDayToDate_(1,-1)|(星期1，上周)，按自己需要改',
                  
                  ]" :key="item.name">
                    <el-dropdown-item  :command="item.split('|')[0]"><el-tag type="danger">{{item}}</el-tag></el-dropdown-item>
                  </el-col>
                </el-row>
              </el-dropdown-menu>
              
            </el-dropdown>

            <el-dropdown trigger="click" @command="addVar" style="color: #ef190e;">
              <span class="el-dropdown-link" >
                添加变量<i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-row style="min-width:100px;max-width:400px">
                  <el-col :span="12" v-for="item in all_vars" :key="item.name">
                    <el-dropdown-item  :command="item.name"><el-tag type="danger">{{item.name}}</el-tag></el-dropdown-item>
                  </el-col>
                </el-row>
              </el-dropdown-menu>
            </el-dropdown>
          </tinymce>
        <div slot="footer" class="dialog-footer" style="text-align: left">
          1、如果内容是以http开始，将会按你指定的url 连接的网页作为模板<br>
          2、如果设置“针对这个数据集中的每条数据执行模板”， 使用_loop_['字段']来引用原数据集中的数据。_idx_ 表示当前取到第几行数据
          <el-button type="primary" @click="handleSubmit">确 定</el-button>
        </div>
     </el-dialog>
   </div>
</template>

<script>
import Tinymce from '@/components/Tinymce'

export default {
    name: 'tinymceDialog',    
    components: {Tinymce},
    props:{all_ds:{type:Array,default(){return []} } ,visible:Boolean,target_obj:[Object,Array],all_vars:{type:Array,default(){return []} } },
    watch: {
        dialogVisible(val) {
        this.$nextTick(() => {
            this.$emit('update:visible', val)
            })      
        },
        visible(val) {
            if(val)            
                this.obj= this.deepClone( this.target_obj)
            this.dialogVisible=this.visible
        },
    },
   methods:{
     addLoopVar(command){
       const editor=this.$refs.tinymce.editor
       const dom=editor.dom
       let txt="_idx_"
       if(command!="_idx_")
        txt=`_loop_['${command}']`
       editor.insertContent(`<span class="mceNonEditable" style:"color: red; text-decoration: underline" >{{ ${txt} }}<span>`)
     },
     addVar(command){
       const editor=this.$refs.tinymce.editor
       const dom=editor.dom
       editor.insertContent(`<span class="mceNonEditable" style:"color: red; text-decoration: underline" >{{ ${command} }}<span>`)
     },
      handleSubmit(){
        
        if(this.obj.name.trim()==""){
          this.$message.warning("必须输入名字")
          return
        }
        this.$emit('update:visible', false)
        
        this.$emit("submit",{newVal:this.obj,old_Val:this.target_obj})        
    },
    close(){
      this.$emit('update:visible', false)      
    }
   },
   data(){
       return {
        fullscreen:false,
        dialogVisible:false,
        obj:{name:'',txt:'',wx_user:''},
        cur_var:"",
        initProps:{
          content_style: "span[contentEditable=false] {color: red; text-decoration: underline}"
        }
       }
   }
}
</script>

<style>

</style>