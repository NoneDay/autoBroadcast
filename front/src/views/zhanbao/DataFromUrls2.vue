<template>
    <div>
        <avue-crud :data="dataFrom" :option="option" v-model="obj" 
            @row-save="rowSave" height=250 ref="xGrid_url"
            @row-update="rowUpdate"
            @row-del="rowDel" @sortable-change="sortableChange"
            @refresh-change="refresh"
            @row-click="handleRowClick"  
            @current-row-change="handleCurrentRowChange"
        >
        <template slot-scope="scope" slot="menuLeft">
        <el-button type="danger" icon="el-icon-plus" size="small" plain @click.stop="guess_form">输入参数</el-button>
        <el-button type="danger" icon="el-icon-plus" size="small" plain @click.stop="grant_form">登录URL的授权Form参数</el-button>

        </template>           
        </avue-crud>
   <formDialog title="当前选中的url需要的参数" :visible.sync="form_input_visible"  v-if="url_data!=null && url_data.form_input!=null"
        
        :oldFormInput.sync="url_data.form_input" append-to-body 
        :form-option=" {
          addBtn:false,delBtn:false,cellBtn:true,editBtn:false,cellEdit:true,rowKey:'name',
          column: [{ prop: 'name', label: '参数名字', cell:false,formslot:true  },{ prop: 'value', label: '参数值', cell:true }] 
        }"
    />

   <formDialog title="当前选中的url需要的参数" :visible.sync="grant_form_visible" v-if="url_data!=null && url_data.grant_form_input!=null"

        :oldFormInput.sync="url_data.grant_form_input" append-to-body 
        :form-option=" {
          addBtn:true,delBtn:true,cellBtn:true,editBtn:false,cellEdit:true,rowKey:'name',
          column: [{ prop: 'name', label: '参数名字', cell:true  },{ prop: 'value', label: '参数值', cell:true }] 
        }"
    />
  </div>

</template>

<script>
import formDialog from './formDialog'
export default {
  components: { formDialog },
  props: {
    dataFrom: Array, newUrlFormInput: Array
  },
  watch:{
      dataFrom(new_v,old_v){
        this.$nextTick(()=>{
          if(this.$refs.xGrid_url){
              if(this.dataFrom && this.dataFrom.length>0){
                  this.$refs.xGrid_url.setCurrentRow(this.dataFrom[0])
                  this.url_data=this.dataFrom[0]
              }
              else{
                this.url_data=null
                this.has_select= false
              }
              this.$emit('select_change', this.url_data)              
          }
        })
      }
  },

  data() {
    return {
      obj:{},
      data: [],
      url_data:null,
      has_select:false,
      form_input_visible: false,
      grant_form_visible: false,
      files_template_exec_result: {},
      files_template_exec_result_visilbe: false,
      option:{
          index: true,highlightCurrentRow:true,height:200,maxHeight:200,sortable:true,
        column: [
            {label: "网址",prop: "url" ,span:12,
              rules: [{required: true,message: "请输入网址",trigger: "blur"}]
            },
            {label: "类型",prop: "type" ,type:'select',
              dicData:[
                    {value:'html', label:'html'},
                    {value:'json', label:'json'},
                    {value:'file', label:'csv文件'},
                    {value:'sql', label:'sql加工'}
              ],
              rules: [{required: true,message: "请选择类型",trigger: "blur"}]
            },
          {label: "描述",prop: "desc"},
          {label: "登录url",prop: "grant_url"},
        ]
      }
    }
  },

  methods: {
    guess_form() {
      if (this.url_data=== null) {
        this.$message.error('请先选择数据来源！')
        return
      }
      if (this.url_data.form_input === undefined)
      { 
        this.url_data.form_input = [] 
      }
      this.form_input_visible = true
    },
    grant_form() {
      if (this.url_data === null) {
        this.$message.error('请先选择数据来源！')
        return
      }
      if (this.url_data.grant_form_input === undefined)
      { 
        this.url_data.grant_form_input = [] 
      }
      this.grant_form_visible = true
    }, 

    handleRowClick (row, event, column) {
        this.$emit('select_change', row)
    },
    handleCurrentRowChange(row){        
        this.url_data=row//?row:{ form_input: [], grant_form_input: [] }
        this.has_select= row!=null
        this.$emit('select_change', row)
    },    
    rowSave(form,done,loading){
        this.dataFrom.push(Object.assign({ 'type': 'html', 'form_input': [], 'ds': [] },form))
        done(); 
      },
    refresh(val){
        this.$emit('reload_define')
        this.$message.success('从服务器重取了数据');
    },
    rowDel(form,index){
        this.dataFrom.splice(index,1)
    },
    rowUpdate(form,index,done,loading){
        Object.assign(this.dataFrom[index],form)
        done();    
    },
    sortableChange(oldindex, newindex, row, list) {
      list=this.deepClone(list)
      this.dataFrom.splice(0,this.dataFrom.length)
      this.$nextTick(()=>{
        list.forEach(element => {
          this.dataFrom.push(element);  
        });        
      })
    },
    typeForUrl(url){
    let type_dict=
    [
      {'type': "帆软",
      'pattern':"http://demo.finereport.com/decision/",
      'login_data_template':'{"username":"{{username}}","password":"{{password}}","validity":-1,"sliderToken":"","origin":"","encrypted":false}',
      'login_data_type':"json",//form
      'login_url':"http://demo.finereport.com/decision/login",
      "login_headers":`{
            'Accept': 'application/json, text/javascript, */*; q=0.01'
            ,'Accept-Encoding': 'gzip, deflate'
            ,'Accept-Language': 'zh-CN,zh;q=0.9'
            ,'Cache-Control': 'no-cache'
            ,'Content-Type': 'application/json'
            ,'Cookie': 'fine_remember_login=-1'
            ,'Proxy-Connection': 'keep-alive'
            ,'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
            ,'X-Requested-With': 'XMLHttpRequest'
        }`,
      "login_success":"",
      'next_headers':'{"Authorization": "Bearer {{login_data["data"]["accessToken"]}}"}',
      "next_cookies":'{"fine_remember_login":-1,"fine_auth_token":"{{login_data["data"]["accessToken"]}}" }',
      },
    ]
    let result=[]
    type_dict.forEach(ele => {
        if(ele.pattern.test(url))
            result.push(ele)
    });
    return result
}

  }

}
</script>

<style scope>
.el-table__body tr.current-row>td {
    background-color: #cad2da;
}
.avue-crud__pagination {
  display: none;
}
</style>
