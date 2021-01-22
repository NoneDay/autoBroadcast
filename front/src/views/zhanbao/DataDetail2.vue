<template>
  <div>
    
        <avue-crud :data="urlData_ds" :option="urlData_ds_option" v-model="obj"  ref="xGrid_detail"
            @row-save="rowSave"
            @row-update="rowUpdate"
            @row-del="rowDel"
            @refresh-change="refresh"  
            @current-row-change="handleCurrentRowChange"
        >
          <template slot-scope="scope" slot="menuLeft">
            <el-button type="danger" icon="el-icon-plus" size="small" plain @click.stop="detail_toolbarButtonClickEvent('query_data')">查看数据</el-button>
            <el-button type="danger" icon="el-icon-plus" size="small" plain @click.stop="detail_toolbarButtonClickEvent('query_col_name')">查看列名</el-button>
            <el-button type="danger" icon="el-icon-plus" size="small" plain @click.stop="detail_toolbarButtonClickEvent('append_data')">合并其他数据</el-button>
            <el-button type="danger" icon="el-icon-plus" size="small" plain @click.stop="detail_toolbarButtonClickEvent('sql')">最终数据整理</el-button>
          </template>        
        </avue-crud>


     <el-dialog :visible.sync="columns_name_visible" label="选择显示列" :close-on-click-modal="false" append-to-body>
      <el-checkbox-group v-model="checkedColumns">
        <el-checkbox v-for="col in columns_name" :key="col" :label="col">{{ col }}</el-checkbox>
      </el-checkbox-group>
      选择关键字：<br>
      <el-radio-group v-model="key_column">
        <el-radio-button v-for="col in columns_name" :key="col" :label="col">{{ col }}</el-radio-button>
      </el-radio-group>

      <div slot="footer" class="dialog-footer">
        <el-button @click="columns_name_visible = false">取 消</el-button>
        <el-button type="primary" @click="columns_name_dialog_submit">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="append_data_visible" label="合并其他数据" :close-on-click-modal="false" append-to-body>
        <basic-container>
              <avue-crud :data="tmp_append_data" :option="tmp_append_data_option2" v-model="obj"  
                  @row-save="rowSave2"
                  @row-update="rowUpdate2"
                  @row-del="rowDel2" 
              >
              </avue-crud>
          </basic-container> 
      <b>备份22时05分</b>  取历史备份数据，严格按照这个格式写，只需要替换对应的时和分就可以。程序在指定时间执行的时候，会备份当时该数据。任何时候取数
      都会去取前一天的这个数据，然后按第一列为关键字合并到一起<br>
      <b>group.csv</b> 从csv文件中取数<br>
      <b>b</b>  其他文字，按数据源取数<br>
      合并数据时，以当前表为主表，将附加表附加到当前主表上，如果没有数据，将设置为0
      <div slot="footer" class="dialog-footer">
        <el-button @click="append_data_visible = false">取 消</el-button>
        <el-button type="primary" @click="append_data_dialog_submit">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="sql_visible" title="设置sql" :close-on-click-modal="false" append-to-body>
      <avue-form v-model="option_sql_obj" :option="option_sql" v-if="sql_visible"  @submit="sql_dialog_submit">
      </avue-form>
    </el-dialog>
  </div>
</template>

<script>
export default { 
  props: {
    urlData: Object
  },
  watch:{ 
        urlData(new_v){
            this.$nextTick(()=>{
              if(this.urlData && this.urlData.ds.length>0)
                    this.cur_row=this.urlData.ds[0]
              else
                this.cur_row=null
              this.$refs.xGrid_detail.setCurrentRow(this.cur_row)
          })          
        } 
  },
  data() {
    return {
      obj:{},
      option_sql_obj:{},
      columns_name: [],
      sql_visible: false,
      tmp_sql: '',
      columns_name_visible: false,
      key_column:'',
      checkedColumns: [],
      append_data_visible: false,
      tmp_append_data: [],
      cur_row:{},
      tmp_append_data_option2:{ 
        column: [
          { prop: 'from', label: '数据来源', width: 250 },
          { prop: 'suffixes', label: '后缀', width: 250 }
        ]
      },
      urlData_ds_option:{
          index: true,highlightCurrentRow:true,height:200,maxHeight:200,sortable:true,
        column: [
          { prop: 't', label: '类型', rules: [{required: true,message: "请输入类型",trigger: "blur"}], type:'select',
              dicData: [
                { value: 'html', label: 'html' },
                { value: 'json', label: 'json' },
                { value: 'sqlite', label: 'sqlite' }
              ]
          },
          { prop: 'name', label: 'name', width: 100,
            rules: [
                {required: true,message: "请输入名字",trigger: "blur"},
                { validator:function(rule, value, callback){
                    if (!/^[a-zA-Z\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5]*$/.test(value)) {
                      return callback(new Error('请输入首字符为非数字中间无空格等特殊字符的字符串！！'))
                    } else {
                      callback()
                    }
                  }
                }
                ]
          },
          { prop: 'pattern', label: '模式', width: 150, editRender: { name: 'textarea' }},
          { prop: 'start', label: 'start'},
          { prop: 'end', label: 'end'},
          { prop: 'sort', label: '排序列'},
          { prop: 'columns', label: '列名',hide:true,editDisplay:false,addDisplay:false},
          { prop: 'view_columns', label: '选择显示的列',hide:true,editDisplay:false,addDisplay:false},
          { prop: 'backup', label: '备份'}
        ]
      }
    }
  },
  computed:{
      option_sql(){
        let field_dicData=[]
        if(this.cur_row.last_columns){
          this.cur_row.last_columns.forEach(x=>{
            field_dicData.push({label: x,value: x})
          })
        }
        return {
            tabs:true,enter:false,
              group:[
               {icon:'el-icon-info',label: 'sql',prop: 'group1',column: [{label: 'sql',span:20,prop: 'sql',type:"textarea",minRows:20}]},
               {icon:'el-icon-info',label: '可视化设置',prop: 'group2',
                  column: [
                      {label: '条件',prop: 'where',maxHeight:100,size:'mini',type: 'dynamic',span:24,
                        children: {
                          align: 'center',headerAlign: 'center',
                          column: [
                            {width: 200,label: '字段',prop: "field",type: 'select',dicData: field_dicData},
                            {width: 200,label: '关系',prop: "op",type: 'select',
                              dicData: [{label: '等于',value: "=="}, {label: '不等于',value: "!="},
                              {label: '大于',value: ">"}, {label: '大于等于',value: ">="},
                              {label: '小于',value: "<"}, {label: '小于等于',value: "<="},
                              ]
                            },
                            {width: 200,label: '值',prop: "value",},
                          ]
                        }
                      },
                      {label: '分组',prop: "group",type: 'select',multiple:true,span:17,dicData: field_dicData,row:true },
                      {label: '排序字段',prop: "sort_field",type: 'select',span:8,dicData: field_dicData},
                      {label: '',prop: "sort",type: 'radio',span:6,value:'False',row:true,
                          dicData: [{label: '降序',value: 'False'},{label: '升序',value: 'True'}]
                      }
                    ]
                }
              ]
          }
    },
    urlData_ds(){
      if(this.urlData)
        return this.urlData.ds
      else return []
    }
  },
  methods: {
      handleCurrentRowChange(row){
        this.cur_row=row
      },    
    
      refresh(val){
          
      },
    rowSave(form,done,loading){
          this.urlData.ds.push(Object.assign({},form))
          done(); 
        },    
      rowDel(form,index){
          this.urlData.ds.splice(index,1)     
          if(this.urlData.ds.length>0){
            this.cur_row=this.urlData.ds[0]
            this.$refs.xGrid_detail.setCurrentRow(this.cur_row)
          }
          else{
            this.cur_row=null
            this.$refs.xGrid_detail.setCurrentRow()
          }               
      },
      rowUpdate(form,index,done,loading){
          Object.assign(this.urlData.ds[index],form)
          done();    
      },

      rowSave2(form,done,loading){
          this.cur_row.append.push(Object.assign({},form))
          done(); 
        },    
      rowDel2(form,index){
          this.cur_row.append.splice(index,1)
      },
      rowUpdate2(form,index,done,loading){
          Object.assign(this.cur_row.append[index],form)
          done();    
      },
    default_sql(){
          let tmp_sql = ''
          let detail_data=this.cur_row
          if (!detail_data.last_columns || detail_data.last_columns.length === 0) 
             return tmp_sql
          tmp_sql = 'select \r\n\r\n[' + detail_data.last_columns.join('],\r\n[') + ']'
          if (tmp_sql.startsWith(',\r\n')) { tmp_sql = tmp_sql.substr(1) }
          tmp_sql = tmp_sql + ' \r\n\r\nfrom \r\n\r\n' + detail_data.name
          return tmp_sql
    },

    detail_toolbarButtonClickEvent( button) {
      let urlData = this.urlData
      let detail_data = this.cur_row
      
      if (urlData === null) {
        this.$message.error('请先选择数据来源！')
        return
      }
      switch (button) { 
        case 'insert_actived':
          urlData.ds.push({ t: 'html', pattern: '#reportDivmainthetable', start: '1', end: '10000', columns: 'auto', view_columns: '', sort: '' })
          break
        case 'query_col_name':
          if (detail_data === null) {
            this.$message.error('请先选择数据来源！')
            return
          }
          this.columns_name_visible = true
          this.columns_name = detail_data.old_columns
          this.key_column = detail_data.key_column
          this.checkedColumns = detail_data.view_columns.split(',')
          break
        case 'sql':
          if (detail_data === null) {
            this.$message.error('请先选择数据来源！')
            return
          }
          if(detail_data.last_columns===undefined){
            this.$message.error('请先运行一次查看数据！')
            return
          }
          if (detail_data.vis_sql_conf === undefined) 
            detail_data.vis_sql_conf={}
          let tmp_sql = this.default_sql()
          if (detail_data.sql === undefined) { detail_data.sql = '' }
          if (detail_data.sql === '') { detail_data.sql = tmp_sql }
          this.tmp_sql = detail_data.sql
          this.option_sql_obj= detail_data.vis_sql_conf
          this.option_sql_obj.sql=this.tmp_sql
          this.sql_visible = true
          break
        case 'append_data':
          if (detail_data === null && urlData.ds.length > 0) {
            this.$message.error('请先选择数据来源！')
            return
          }
          if (detail_data.append === undefined) { detail_data.append = [] }
          this.$emit("append_data",detail_data)          
          break
        case 'query_data':
          if ( this.urlData.ds===undefined) {
            this.urlData.ds=[]
            detail_data=null
          }
          if(this.urlData.ds.length>0 && detail_data==null)
          {
             this.$message.error('请先选择数据来源！')
            return
          }
          this.$emit('query_data', urlData, detail_data)
          break
      }
    },
    columns_name_dialog_submit() {
      let detail_data = this.cur_row
      detail_data.view_columns = this.checkedColumns.join()
      detail_data.key_column=this.key_column
      if (detail_data.view_columns.startsWith(',')) { detail_data.view_columns = detail_data.view_columns.substr(1) }
      this.columns_name_visible = false
    },
    sql_dialog_submit() {
      let detail_data = this.cur_row
      
      if (this.option_sql_obj.sql !== this.default_sql()) 
        detail_data.sql = this.option_sql_obj.sql
      else  
        detail_data.sql = '' 
      delete this.option_sql_obj.sql

      let ret_s=""
      if(this.option_sql_obj.where && this.option_sql_obj.where.length>0){
          let where_arr =[]
          this.option_sql_obj.where.forEach(x=>
            where_arr.push( "`"+x.field +"`"+ x.op + x.value )
          )
          ret_s=ret_s+'.query("""'+ where_arr.join(" & ")  + '""")'
      }
      if(this.option_sql_obj.group && this.option_sql_obj.group.length>0){
        ret_s=ret_s+'.groupby(["'+this.option_sql_obj.group.join('","')+'"]).sum().reset_index()'
      }
      if(this.option_sql_obj.sort_field)
      {
        ret_s=ret_s+'.sort_values("' +this.option_sql_obj.sort_field+'",ascending='+this.option_sql_obj.sort+')'
      }
      this.option_sql_obj.expr=ret_s
      detail_data.vis_sql_conf= this.option_sql_obj

      this.sql_visible = false
    },
    append_data_dialog_submit() {
      let detail_data = this.cur_row
      detail_data.append = this.tmp_append_data
      this.append_data_visible = false
    }
  }
}
</script>

<style type="text/css" scope>
    .dataframe  {width:100%;border-collapse:collapse;empty-cells:show;margin-bottom:16px;display:block;overflow:auto;border-spacing:0}
    .dataframe  tr{background-color:#fff;border-top:1px solid #c6cbd1}
    .dataframe  td,.vditor-reset table th{padding:6px 13px;border:1px solid #dfe2e5;word-break:keep-all}
    .dataframe  th{font-weight:600;word-break:keep-all}.dataframe tbody tr:nth-child(2n){background-color:#f6f8fa}
.el-table .cell {
    box-sizing: border-box;
    text-overflow: ellipsis;
    white-space: normal;
    word-break: break-all;
    line-height: 13px;
    padding-right: 1px;
    overflow: hidden;
}
.avue-crud__pagination {
  display: none;
}
</style>
