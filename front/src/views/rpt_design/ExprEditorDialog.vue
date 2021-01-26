<template>
    <el-dialog   style="text-align: left;"
    :visible.sync="dialogVisible" :title="'设置表达式:'+prop.display" 
        :close-on-click-modal="false"  @close="close" 
          direction="btt" append-to-body  
    > 
<el-container >
  <el-header style="height: 150px;">
   
    <form>
      <codemirror v-if='dialogVisible' ref="editor"    v-model="obj[prop.val]" 
          :options="{tabSize: 4, mode: 'text/javascript', styleActiveLine: true,lineWrapping: true,
            theme: 'cobalt',showCursorWhenSelecting: true, cursorBlinkRate:0 }" 
            @ready="editor_ready"
         />
      </form>
  </el-header>
  <el-main style="padding:10px 20px">

<el-row>
  <el-col :span="8">
    <el-scrollbar style="height:250px">
<el-collapse accordion v-if="dialogVisible" >
   <el-collapse-item v-for="(ds,ds_idx) in report.dataSets.dataSet" :key="ds+ds_idx">
    <template slot="title"> <!-- https://www.iconfont.cn -->
        <svg v-if="ds._type=='excel'" class="icon" style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1709"><path d="M903.2 315.4V950c0 15.7-12.7 28.4-28.4 28.4H217.3c-12 0-21.6-9.7-21.6-21.6V98.7c0-8.8 7.1-15.9 15.9-15.9h443.1c0.9 0 1.4 1.1 0.8 1.8-0.4 0.4-0.4 1.1 0.1 1.5l247.5 228.6c0 0.1 0.1 0.4 0.1 0.7z" fill="#F4F4F4" p-id="1710"></path><path d="M654.8 300.1V82.8L903.3 315H669.7c-8.2 0-14.9-6.7-14.9-14.9zM431.4 374.1H213.2c-58.4 0-105.7-47.3-105.7-105.7 0-58.4 47.3-105.7 105.7-105.7h218.2c58.4 0 105.7 47.3 105.7 105.7 0.1 58.3-47.3 105.7-105.7 105.7z" fill="#4BC929" p-id="1711"></path><path d="M386.1 275.1c-1.1-1.7-2.3-3.1-3.4-4.3-4.1-4.2-9.6-7.1-16.5-8.5-4.5-1.1-8.5-1.4-11-1.5h-64.3c-8.6 0.1-15-1.7-18.5-5.3-0.7-0.7-1.2-1.4-1.6-2.1v-0.3c-1.2-2-1.9-4.5-1.9-7.5v-1-1.1c0.1-4.2 1.3-7.5 3.9-9.9 5.4-5.1 15.5-5.8 18.6-5.7H383.3c4 0 7.3-3.3 7.3-7.3s-3.3-7.3-7.3-7.3h-91.4c-2.5-0.1-17.2-0.2-27.6 8.3h-0.4c-0.6 0.5-1.2 1.1-1.8 1.7-2 2.1-4.3 5.1-5.8 9.1v0.3c-1.3 3.4-1.9 7-1.9 11v0.5c-0.2 7.6 1.8 13.2 4.3 17.1 0.5 0.8 1 1.5 1.6 2.2v0.1l0.3 0.3c0.1 0.1 0.1 0.2 0.2 0.2l0.3 0.3 0.2 0.2 0.3 0.3c0 0.1 0.1 0.1 0.1 0.2 0.1 0.2 0.3 0.3 0.4 0.5 4.1 4.2 9.6 7.1 16.5 8.5 4.5 1.1 8.5 1.4 11 1.5H354c3.2 0 6.1 0.2 8.7 0.7 3.4 0.8 7 2.3 9.5 4.7 0.8 0.7 1.4 1.5 1.9 2.4 0.2 0.3 0.3 0.5 0.4 0.8 0 0.1 0.1 0.2 0.1 0.3 0.1 0.2 0.2 0.4 0.3 0.5 0 0.1 0.1 0.2 0.1 0.3 0.1 0.2 0.1 0.3 0.2 0.5 0 0.1 0.1 0.3 0.1 0.4 0.1 0.2 0.1 0.3 0.2 0.5 0 0.1 0.1 0.3 0.1 0.4 0 0.2 0.1 0.3 0.1 0.5 0 0.1 0 0.3 0.1 0.5 0 0.2 0.1 0.4 0.1 0.5v0.5c0 0.2 0 0.4 0.1 0.6V293c-0.1 4.2-1.3 7.5-3.9 9.9-2.5 2.4-6.1 3.8-9.5 4.7-2.6 0.5-5.5 0.7-8.7 0.7h-78.3c-0.7 0-1.5 0.1-2.1 0.3h-12c-4 0-7.3 3.3-7.3 7.3s3.3 7.3 7.3 7.3h91.4c1.4 0.1 7 0.1 13.5-1.5 5.8-1.3 10.7-3.5 14.5-6.8 0.6-0.5 1.2-1.1 1.8-1.7 2-2.1 4.3-5.1 5.8-9.1 1.2-3.1 1.9-6.9 1.9-11.3v-0.7-0.5-0.2-0.1c0-7.1-1.9-12.4-4.3-16.2z" fill="#FFFFFF" p-id="1712"></path><path d="M716 509.4H369.6c-5.4 0-9.8 4.4-9.8 9.8v312.5c0 6.2 5.1 11.3 11.3 11.3h341.6c7.9 0 14.4-6.4 14.4-14.4v-308c0-6.2-5-11.2-11.1-11.2z m-11.2 22.3v83h-89.6v-83h89.6zM592.9 819.2h-99v-81.6h99v81.6zM494 715.3V637h99v78.4h-99z m-22.3 0h-88.9V637h88.9v78.3zM494 533.1h99v81.6h-99v-81.6zM615.2 637h88.9v78.4h-88.9V637zM382.1 531.7h89.6v83h-89.6v-83z m0 288.9v-83h89.6v83h-89.6z m322.7 0h-89.6v-83h89.6v83z" fill="#4BC929" p-id="1713"></path></svg>
        <svg v-if="ds._type!='excel'" class="icon" style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4244"><path d="M793.6 682.8288V460.8H243.2v221.7088C108.3008 675.904 0 565.5424 0 431.5904c0-129.856 98.1248-234.56 230.4-251.2512C281.6 79.8336 388.224 12.8 512 12.8c157.8496 0 285.8496 108.8768 315.7248 251.2384C934.4 272.4096 1024 364.544 1024 473.3824c0 117.2864-93.8752 209.4464-213.376 209.4464H793.6z" fill="#1989FA" opacity=".3" p-id="4245"></path><path d="M518.4 833.4336c-151.9872 0-275.2-42.9824-275.2-96V864c0 53.0176 123.2128 96 275.2 96S793.6 917.0176 793.6 864v-126.5664c0 53.0176-123.2128 96-275.2 96z m0-197.184c-151.9872 0-275.2-42.9696-275.2-96V672c0 53.0176 123.2128 96 275.2 96S793.6 725.0176 793.6 672V540.2496c0 53.0304-123.2128 96-275.2 96zM243.2 467.2c0 53.0176 123.2128 96 275.2 96S793.6 520.2176 793.6 467.2c0-53.0176-123.2128-96-275.2-96S243.2 414.1824 243.2 467.2z" fill="#1989FA" p-id="4246"></path></svg>
        <svg v-if="ds._type=='cr'" class="icon" style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7477"><path d="M912.027826 661.993739l-352.300522 211.389218a70.077217 70.077217 0 0 1-35.216695 8.770782c-12.733217 0-25.510957-2.938435-35.261218-8.770782l-352.300521-211.389218c-19.456-11.664696-19.456-30.630957 0-42.25113l59.748173-35.84 271.84974 163.127652c15.62713 9.305043 35.439304 14.425043 55.963826 14.425043 20.48 0 40.292174-5.12 55.919304-14.425043l271.849739-163.127652 59.748174 35.84c19.456 11.664696 19.456 30.586435 0 42.25113z" fill="#2B3B94" p-id="7478"></path><path d="M912.027826 501.092174l-352.300522 211.433739a70.077217 70.077217 0 0 1-35.216695 8.770783c-12.733217 0-25.510957-2.938435-35.261218-8.770783l-352.300521-211.433739c-19.456-11.664696-19.456-30.630957 0-42.251131L196.697043 422.956522l271.84974 163.127652c15.62713 9.394087 35.439304 14.514087 55.963826 14.514087 20.48 0 40.292174-5.12 55.919304-14.514087L852.324174 422.956522l59.748174 35.884521c19.411478 11.664696 19.411478 30.630957-0.044522 42.251131z" fill="#2B3B94" p-id="7479"></path><path d="M912.027826 340.23513l-352.300522 211.43374a70.077217 70.077217 0 0 1-35.216695 8.770782c-12.733217 0-25.510957-2.938435-35.261218-8.770782L136.94887 340.23513c-19.456-11.620174-19.456-30.630957 0-42.25113l352.300521-211.433739c9.750261-5.832348 22.528-8.726261 35.261218-8.726261 12.688696 0 25.466435 2.893913 35.216695 8.726261l352.300522 211.433739c19.456 11.664696 19.456 30.630957 0 42.25113z" fill="#2B3B94" p-id="7480"></path></svg>
        <el-tag style="color:black;width:80%">{{ds._name}} </el-tag>
        
    </template>
    <div v-for="(one,idx) in JSON.parse(ds._fields)" 
        :key="one+idx" 
        :style="{'background-color':(cur_ds==ds && cur_field==one)?'#c5f3e0':'#fff','cursor': 'pointer'}"        
        @click="choose_field(ds,one)"
        @dblclick="insert_field(ds,one)">       
        {{ one }}
    </div>
  </el-collapse-item>
  </el-collapse>
    </el-scrollbar>
  </el-col>
  <el-col :span="8">
    <el-scrollbar style="height:250px">
     <el-tree :data="func_xml" :props="{children:'catalogy',label:'_name'}" node-key="_name" accordion >
             <span class="custom-tree-node" slot-scope="{ node, data }" >
                    <span v-if="!node.isLeaf" type="text" size="mini" class="el-icon-folder custom-tree-node-label" 
                    style="font-weight:700;" >
                        {{ data.name }}
                    </span>
                    <span  v-else type="text" size="mini" class="el-icon-bell custom-tree-node-label" 
                    @click="change_func_xml('catalogy',data,node)" >
                        {{ data._name }}
                    </span>
                </span>
    </el-tree>
    </el-scrollbar>
  </el-col>
  <el-col :span="8">
    <el-scrollbar style="height:250px">
    <el-table :show-header='false' max-height="250"
     :data="catalogy.function" highlight-current-row style="width: 100%">
        <el-table-column label="姓名" width="180">
          <template slot-scope="scope">
              <div @click="change_func_xml('cur_func',scope.row.__text)"  @dblclick="insert_func(scope.row._name)">
                  {{ scope.row._name }}
              </div>
            </template>
        </el-table-column>
    </el-table>
    </el-scrollbar>

  </el-col>
  </el-row> 
  <el-row> 
  <el-col :span="24">
    <el-input type="textarea" :rows="6" v-model="cur_func"></el-input>    
  </el-col>  
</el-row>    

  </el-main>

</el-container>
 
          <span slot="footer" class="dialog-footer">
            <el-button @click="dialogVisible = false">取 消</el-button>
            <el-button type="primary" @click="handleSubmit">确 定</el-button>
        </span>
    </el-dialog>      

</template>

<script>
import {loadFile} from './utils/util.js'

import  codemirror  from './element/vue-codemirror.vue'

//import MonacoEditor from 'vue-monaco'
import x2js from 'x2js' 
const x2jsone=new x2js(); //实例
export default {
    components: {codemirror},
    
    mounted() {
      this.func_xml=x2jsone.xml2js(loadFile('func.xml'))["functions"]["catalogy"]
      //console.info(this.func_xml)
      
    },
    name: "ExprEditorDialog",
    props: { visible: Boolean, target_obj: Object,prop:Object,report:Object},
    data() {
        return {
        dialogVisible:false,
        obj:{sql:''},
        func_xml:"",
        catalogy:[],
        cur_func:"",
        cur_ds:{},
        cur_field:"",
        }
    }, 
  watch: {
    dialogVisible(val) {
      this.$emit('update:visible', val)
    },
    oldFormInput(val){
      this.obj=this.deepClone(val)
    },
    visible(val) {
      this.obj=this.deepClone(this.target_obj)
      if(val && this.obj[this.prop.val]==undefined)
        this.$set(this.obj,this.prop.val,'')
      this.dialogVisible=val
      this.$emit('update:visible', val)
    }
  },
  methods: {
   handleSubmit(){

        this.$emit('update:visible', false)
        this.$set(this.target_obj,this.prop.val,this.obj[this.prop.val])
        //this.target_obj[this.prop]=this.obj[this.prop]
        this.$emit("submit",{newVal:this.obj,old_Val:this.target_obj})        
    },
    close(){
      this.$emit('update:visible', false)      
    },
    onCmReady(cm) {
      console.log('the editor is readied!', cm)
    },
    onCmFocus(cm) {
      console.log('the editor is focused!', cm)
    },
    onCmCodeChange(newCode) {
      console.log('this is new code', newCode)
      this.obj = newCode
    },    
    change_func_xml(prop,data){
      this[prop]=data
    },
    choose_func(name){
      alert(name)
    },
    insert_func(name){
      let prefix=''
      if(!this.$refs.editor.value)
        prefix="="
      if(this.$refs.editor.value && this.$refs.editor.value.trim()=="")
        prefix="="
      if(this.catalogy._name=="数据集"){
        let arg=name.replace("()",`(${this.cur_ds._name}.${this.cur_field})`)
        this.$refs.editor.codemirror.replaceSelection(`${prefix}${this.cur_ds._name}.${arg}`)
      }
      else
        this.$refs.editor.codemirror.replaceSelection(`${prefix}${name}`)
    },
    choose_field(ds,field){
      this.cur_ds=ds
      this.cur_field=field      
    },
    insert_field(ds,field){
      this.cur_ds=ds
      this.cur_field=field
      if(this.$refs.editor.value && this.$refs.editor.value.trim()!="")
        this.$refs.editor.codemirror.replaceSelection(ds._name+"."+field)
      else
        this.$refs.editor.codemirror.replaceSelection("="+ds._name+"."+field)
    },
    editor_ready(){
      this.$refs.editor.codemirror.setSize('auto','150px')
    }
  },
  computed:{

  }
}
</script>
<style lang="less" scoped>
.my_active{ color: red;}
</style>