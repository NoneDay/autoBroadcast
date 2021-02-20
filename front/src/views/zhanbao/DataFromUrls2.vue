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
        </template>           
        </avue-crud>
   <formDialog title="当前选中的url需要的参数" :visible.sync="form_input_visible"  v-if="url_data!=null && url_data.form_input!=null"
        
        :oldFormInput.sync="url_data.form_input" append-to-body 
        :form-option=" {
          addBtn:false,delBtn:false,cellBtn:true,editBtn:false,cellEdit:true,rowKey:'name',
          column: [{ prop: 'name', label: '参数名字', cell:false,formslot:true  },{ prop: 'value', label: '参数值', cell:true }] 
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
      
      files_template_exec_result: {},
      files_template_exec_result_visilbe: false,
      option:{
          index: true,highlightCurrentRow:true,height:200,maxHeight:200,sortable:true,
        column: [
            {label: "网址",prop: "url" ,span:24,
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
          {label: "描述",prop: "desc"}
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

    handleRowClick (row, event, column) {
        this.$emit('select_change', row)
    },
    handleCurrentRowChange(row){        
        this.url_data=row//?row:{ form_input: [] }
        this.has_select= row!=null
        this.$emit('select_change', row)
    },    
    rowSave(form,done,loading){
        if(['html','json'].includes(form.type)){
          let match_arr=[]
          this.$store.getters.canReadSys.forEach(one_sys=>{
            one_sys.patterns.forEach(one_pat=>{
              if (form.url.startsWith(one_pat))
                match_arr.push([one_sys.name,one_pat])
            })
          })
          if (match_arr.length==0){
            this.$message.error('这个网址没有可匹配的系统，如果确实没输入错误，请联系管理员添加对该系统的支持')
            loading()
            return 
          }
          match_arr.sort(function(a,b){return b[1].length-a[1].length})
          form.type=match_arr[0][0]
        }        
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
