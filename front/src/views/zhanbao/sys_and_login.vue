<template>
<el-tabs  value="first" v-if="ready">
    <el-tab-pane label="用户管理" name="first" v-model="user_obj">
        <avue-crud :data="login_tbl" :option="option_user()"  
        @row-save="user_rowSave"
        @row-update="user_rowUpdate"
        @row-del="user_rowDelete"
        >
        <template  slot-scope="scope" slot="sys_nameForm">
            <el-input :disabled="true" v-model="scope.row.sys_name"></el-input>
        </template>
        
        </avue-crud>
        
    </el-tab-pane>
    <el-tab-pane label="配置管理" name="second" v-if="$store.getters.permission.sys_register">
        <avue-crud :data="data.sys_register" :option="option_sys()" v-model="obj"
        @row-save="sys_rowSave"
        @row-update="sys_rowUpdate"
        @row-del="sys_rowDelete"
        >
        <template  slot-scope="scope" slot="nameForm">
            <el-input :disabled="scope.row.id!=undefined" v-model="scope.row.name"></el-input>
        </template>
        <template slot-scope="scope" slot="menu">
            <el-button type="primary" icon="el-icon-check" size="small" plain @click.stop="handleClone(scope.row,scope.index)">克隆</el-button>
        </template>
        </avue-crud>
    </el-tab-pane>
  </el-tabs>
</template>

<script>
import * as service from '@/api/zhanbao'
function convert_db2web(save_obj,one){
    let tmp=[]
    Object.keys(save_obj[one]).forEach(p_v => {
        tmp.push({'prop':p_v,'value':save_obj[one][p_v]})
    });
    save_obj[one]=tmp
}
function convert_web2db(save_obj,one){
    let tmp={}
    save_obj[one].forEach(p_v => {
        tmp[p_v.prop]=p_v.value
    });
    save_obj[one]=tmp
}

export default {
    async created(){

        let _this=this
        _this.data=await service.getLoginGetDataTemplate()
        _this.login_tbl=[]
        
        _this.$store.getters.canReadSys.forEach(ele=>{
            if(ele.login_url){
                let one=_this.data.login_tbl.find(x=>x.sys_name==ele.name)
                _this.login_tbl.push({'sys_name':ele.name,'username':one?.username,'password':one?.password})
            }
        })
        _this.parsers=this.convert_parsers()
        _this.data.sys_register.forEach(one=>{
            one.json_txt=JSON.parse(one.json_txt)
            one.json_txt['id']=one['id']
            convert_db2web(one.json_txt,'login_data_template')
            convert_db2web(one.json_txt,'headers')
            convert_db2web(one.json_txt,'next_headers')
            convert_db2web(one.json_txt,'next_cookies')
            for (let key in one.json_txt) {
                one[key] = one.json_txt[key];
            }
        })
        _this.ready=true
    },
    computed:{
        
    },
    methods:{
        convert_parsers(){
            let ret=[]
            this.data.parsers.forEach(x=>{
                ret.push({'label':x,"value":x})
            })
            return ret
        },
        handleClone(row,index){
            let _this=this
            this.$prompt('请输入新的系统名字', '新增系统', {
                    confirmButtonText: '确定',
                    inputPattern:/^[a-zA-Z\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5]*$/,
                    cancelButtonText: '取消',
                    inputValue:""
                  }).then(async({ value }) => {
                    if (_this.data.sys_register.find(x=>x.name==value)){
                        this.$alert("名字不能重复");
                        return
                    }
                    let saveObj={...JSON.parse( JSON.stringify(row)),...{id:0,name:value}}
                    saveObj.json_txt.name=value
                    let result=await this.sys_rowSave(saveObj)
                    
                }).catch(error=>error)
        },
        async user_rowUpdate(form,index,done,loading){
            loading()
             let _this=this
            let result=await service.login_tbl(form)
            Object.assign(this.login_tbl[index],form)
            done()
        },
        async sys_rowSave(form,done,loading){
            let save_obj=JSON.parse(JSON.stringify(form))
            convert_web2db(save_obj,'login_data_template')
            convert_web2db(save_obj,'headers')
            convert_web2db(save_obj,'next_headers')
            convert_web2db(save_obj,'next_cookies')
            let _this=this
            let result=await service.sys_register(save_obj)
            if(result['errcode']==0 && result['id']){
                form.id=result['id']
                _this.data.sys_register.push(Object.assign({},form))
            }
            if(done)
                done(); 
        },
        async sys_rowUpdate(form,index,done,loading){
            await this.sys_rowSave(form,done,loading)
            Object.assign(this.data.sys_register[index],form)
        },
         sys_rowDelete(form,index){
            
            let _this=this
            
            this.$confirm(`此操作将永久删除该配置<${form.name}>, 是否继续?`, '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
                }).then(async() => {
                let result=await service.sys_register(form,"delete")
                _this.data.sys_register.splice(index,1)
                _this.$message({
                    type: 'success',
                    message: '删除成功!'
                });
                }).catch(() => {
                _this.$message({
                    type: 'info',
                    message: '已取消删除'
                });          
                });
            
      },
                  option_user(){return {
                      "addBtn": false,"delBtn": false,  "index": "true","headerAlign": "left","align": "left","editBtn": "true",
  "column": [
    {      "label": "系统","prop": "sys_name",formslot:true,      "type": "text",'readonly': true,"span": 24,"display": true,    },
    {      "label": "用户名",      "prop": "username",      "type": "input",      "span": 12,      "display": true    },
    {      "label": "密码",      "prop": "password",      "type": "password",      "span": 12,      "display": true    }
  ]
}
},
            option_sys(){ return {
                "addBtn": "true",
                "editBtn": "true",
                
                "delBtn": "true",
                "saveBtn": "true",
                "column": [
                    {
      type: 'input',
      label: '系统', rules: [{required: true}],
      span: 12,formslot:true,
      display: true,
      prop: 'name'
    },
    {
      type: 'select',
      label: '解析器',
      span: 12, rules: [{required: true}],
      display: true,'dicData':this.parsers,
      prop: 'type'
    },
    {
      type: 'array',
      label: '匹配网址', rules: [{required: true}],
      span: 24,
      display: true,
      prop: 'patterns'
    },
    {
      type: 'input',
      label: '允许用户',
      span: 12, rules: [{required: true}],
      display: true,
      prop: 'allow_userid'
    },
    {
      type: 'select',label: '提交类型',span: 12,display: true,prop: 'login_data_type',
      dicData: [
        {label: 'json',value: 'json'},
        {label: 'form',value: 'form'}
      ],
      props: {label: 'label',value: 'value'},
      cascaderItem: [],      value: 'form'
    },
    {
      type: 'input',label: '登陆网址',span: 24,display: true,prop: 'login_url'
    },
    {
      type: 'dynamic',
      label: '登陆提交内容',
      span: 24,
      display: true,
      children: {
        align: 'center',headerAlign: 'center',index: false,addBtn: true,delBtn: true,
        column: [
          {type: 'input',label: '属性',span: 24,display: true,prop: 'prop'},
          {type: 'input',label: '值',span: 24,display: true,prop: 'value'}
        ]
      },prop: 'login_data_template'
    },
    {type: 'input',label: '登陆成功会有',span: 12,display: true,prop: 'login_success'},
    {type: 'input',label: '登陆错误会有',span: 12,display: true,prop: 'login_error'},
    {
      type: 'dynamic',
      label: '登陆提交:header',
      span: 24,
      display: true,
      children: {
        align: 'center',
        headerAlign: 'center',
        index: false,
        addBtn: true,
        delBtn: true,
        column: [
          {
            type: 'input',
            label: '属性',
            span: 24,
            display: true,
            prop: 'prop'
          },
          {
            type: 'input',
            label: '值',
            span: 24,
            display: true,
            prop: 'value'
          }
        ]
      },
      prop: 'headers'
    },

    {
      type: 'dynamic',
      label: '查询报表:header',
      span: 24,
      display: true,
      children: {
        align: 'center',
        headerAlign: 'center',
        index: false,
        addBtn: true,
        delBtn: true,
        column: [
          {
            type: 'input',
            label: '属性',
            span: 24,
            display: true,
            prop: 'prop'
          },
          {
            type: 'input',
            label: '值',
            span: 24,
            display: true,
            prop: 'value'
          }
        ]
      },
      prop: 'next_headers'
    },
    
    {
      type: 'dynamic',
      label: '查询报表:cookies',
      span: 24,
      display: true,
      children: {
        align: 'center',
        headerAlign: 'center',
        index: false,
        addBtn: true,
        delBtn: true,
        column: [
          {
            type: 'input',
            label: '属性',
            span: 24,
            display: true,
            prop: 'prop'
          },
          {
            type: 'input',
            label: '值',
            span: 24,
            display: true,
            prop: 'value'
          }
        ]
      },
      prop: 'next_cookies'
    }
                ]
                }
    }
    },
    data(){
        return {
            obj:{},
            login_tbl:[],
            user_obj:{},
            parsers:[],
            data:{},
            ready:false,

        }
    }
}
</script>

<style>

</style>