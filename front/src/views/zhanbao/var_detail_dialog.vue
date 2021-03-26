<template>  
<el-dialog :visible.sync="dialogVisible" 
  title="变量定义"  :fullscreen="fullscreen"
  :close-on-click-modal="false"  @close="close"
  direction="btt" append-to-body> 
  <div slot="title" >
          <span class="el-dialog__title">变量定义</span>
          <div style="right: 40px;    top: 20px;    position: absolute;">
            <i @click="fullscreen=!fullscreen"
              class="el-icon-full-screen"></i>
          </div>
        </div>
    {{last_statement}}
    <avue-form :option="option" v-model="obj" v-if="dialogVisible"  @submit="handleSubmit" ref="form">
    </avue-form>
</el-dialog>
</template>
<script>

export default {
  name:"varDetailDialog",
  methods:{
    
    getOption(){
      if(this.target_obj.var_type=="detail")
        return {formHeight:9,size:'mini',
          column: [
              {span: 8,label: '名字',prop: "name",
                rules: [
                    {required: true,message: '必填项',trigger: 'blur'},
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
              {label: '类型',prop:"var_type",display:false},
              {span: 8,label: '数据集',prop: "ds",type: 'select',dicData: this.ds_dicData,
                rules: [
                  {required: true,message: '必填项',trigger: 'blur'}
                ]} , 
              {
                label: '条件',prop: 'where',maxHeight:100,size:'mini',type: 'dynamic',span:24,
                children: {
                  align: 'center',headerAlign: 'center',
                  column: [
                    {width: 200,label: '字段',prop: "field",type: 'select',dicData: this.field_dicData},
                    {width: 200,label: '关系',prop: "op",type: 'select',
                      dicData: [{label: '等于',value: "=="}, {label: '不等于',value: "!="},
                      {label: '大于',value: ">"}, {label: '大于等于',value: ">="},
                      {label: '小于',value: "<"}, {label: '小于等于',value: "<="},
                      ]
                    },
                    {width: 200,label: '值',prop: "value",},
                    {width: 200,label: '条件间的关系',prop: "op_op",type: 'select',value: "&",
                      dicData: [{label: '并且',value: "&"}, {label: '或者',value: "|"},
                      ]
                    },
                  ]
                }
              },
              {label: '分组',prop: "group",type: 'select',multiple:true,span:17,dicData: this.field_dicData,row:true },
              {label: '排序字段',prop: "sort_field",type: 'select',span:8,dicData: this.field_dicData},
              {label: '',prop: "sort",type: 'radio',span:6,value:'False',row:true,
                  dicData: [{label: '降序',value: 'False'},{label: '升序',value: 'True'}]
              }, 
              
              {label: '范围类型',prop: "topType",type: 'radio',value:"top",span:8,row:true,
                  dicData: [{label: '前几',value: 'top'},{label: '后几',value: 'bottom'}
                  //,{label: '中间',value: 'between'}
                  ]
              },
              {label: '开始',prop: "start",type: 'number',span:7,display:false},
              {label: '结束',prop: "end",type: 'number',span:7,display:false,row:true},
              {label: '后几',prop: "bottom",type: 'number',span:7,display:false,row:true},
              {label: '前几',prop: "top",type: 'number',span:7,display:false,row:true},
              
              {label: '结果类型',prop: "resultType",type: 'radio',value:"none",span:8,
                  dicData: [{label: '明细',value: 'detail'},{label: '汇总',value: 'sum'},{label: '无',value: 'none'}]
              },{label: '行间填充',prop: "line_join",value:"\\n",display:false},
              {
                label: '明细',prop: 'select',type: 'dynamic',span:24,maxHeight:100,size:'mini',display:false,
                children: {
                  align: 'center',headerAlign: 'center',
                  column: [
                    {width: 200,label: '前缀',prop: "before",}, 
                    {width: 200,label: '字段',prop: "field",type: 'select',
                      dicData: this.field_dicData,rules: [{required: true,message: '必填项',trigger: 'blur'}]
                    },
                    {width: 200,label: '后缀',prop: "after"},
                  ]
                }
              },
              
              {width: 200,label: '字段',prop: "sum_field",type: 'select',display:false,dicData: this.field_dicData},
              {width: 200,label: '类型',prop: "sum_op",type: 'select',value:'sum',display:false,dicData: [{label: '合计',value: "sum"}]},
          ]
        }
      else if(this.target_obj.var_type=="expr"){
        return {formHeight:9,size:'mini',span:12,
          column: [
              {label: '名字',prop: "name",rules: [{required: true,message: '必填项',trigger: 'blur'}],span:12},
              {label: '类型',prop:"var_type",display:false},
              {label: '类型',prop:"resultType",display:false},
              {label: '类型',prop:"topType",display:false},              
              {label: '表达式',prop:"expr",type:"textarea",span:24},

          ]
        }
      }
      return {formHeight:9,size:'mini',
        column: [
            {width: 200,label: '名字',prop: "name",rules: [{required: true,message: '必填项',trigger: 'blur'}]},
            {width: 200,label: '类型',prop:"var_type",display:false},
            {label: '类型',prop:"resultType",display:false},
            {label: '类型',prop:"topType",display:false},
        ]
      }
    },
    handleSubmit(form,done){
       this.$emit('update:visible', false)
       form.last_statement=this.last_statement
       this.$emit("submit",{newVal:form,old_Val:this.target_obj})
       done()       
    },
    close(){
      this.$emit('update:visible', false)      
    },
    obj_resultType(){      
      let col_detail =this.findObject(this.option.column,'select');
      let line_join =this.findObject(this.option.column,'line_join');
      
      let col_sum =this.findObject(this.option.column,'sum_field');
      let col_op =this.findObject(this.option.column,'sum_op');
      col_detail.display=false
      line_join.display=false
      col_sum.display=false
      col_op.display=false
      if(this.obj.resultType==='detail'){
        col_detail.display=true
        line_join.display=true
      }
      else if(this.obj.resultType==='sum')
        col_sum.display=true
    },
    obj_topType(){
      let col_top =this.findObject(this.option.column,'top');
      let col_bottom =this.findObject(this.option.column,'bottom');
      let col_start =this.findObject(this.option.column,'start');
      let col_end =this.findObject(this.option.column,'end');
      
      if(this.obj.topType==='top'){
        col_top.display=true
        col_bottom.display=false
        col_start.display=false
        col_end.display=false
      }else if(this.obj.topType==='bottom'){
        col_top.display=false
        col_bottom.display=true
        col_start.display=false
        col_end.display=false
      }
      else{
        col_top.display=false
        col_bottom.display=false
        col_start.display=true
        col_end.display=true
      }
    },
  }, 
  created(){
    this.target_obj.where?.forEach(x=>{
      if(x.op_op==undefined)
        x.op_op="&"
    })
    this.obj= this.deepClone( this.target_obj)
    this.all_ds.forEach(element => {
        this.ds_dicData.push({label: element.name,value: element.name})
    });
    this.option=this.getOption()
    this.$nextTick(function(){
      if(this.obj.var_type=="detail"){
        this.obj_resultType()
        this.obj_topType()
      }
    })

  },
  watch: {
    dialogVisible(val) {
      this.$nextTick(() => {
          this.$emit('update:visible', val)
        })      
    },
    visible(val) {
        this.dialogVisible=this.visible
    },
    'obj.resultType'(){
      this.obj_resultType()
    },
    'obj.topType'(){
      this.obj_topType()
    },
    'obj.ds'(){
      this.field_dicData=[]
      if(this.obj.ds){
        this.field_dicData.push({label: '__序号__',value: '__序号__'})
        this.all_ds.filter(x=>x.name==this.obj.ds)[0].last_columns.forEach(x=>{
          this.field_dicData.push({label: x,value: x})
        })
      }
      this.option=this.getOption()
      if(this.obj.var_type=="detail"){
        this.obj_resultType()
        this.obj_topType()
      }    
    }
  },
  props:{all_ds:Array,visible:Boolean,target_obj:Object},
  computed:{
    last_statement(){
      if(this.obj.var_type=="expr"){
        let ret_s=""+this.obj.expr        
        return ret_s        
      }
      let ret_s=""+this.obj.ds
      if(this.obj.var_type=="detail")
      {        
        if(this.obj.where && this.obj.where.length>0){
            let where_arr =[]
            this.obj.where.forEach(x=>{
                if(x.op_op==undefined || (x.op_op!='&' && x.op_op!='|'))
                  x.op_op="&"
              //if (x.field=='__序号__')
              //  where_arr.push( "(index+1)"+ x.op + x.value.replaceAll(/[‘|’|“|”]/g,'\'') )
              //else
              //  where_arr.push( "`"+x.field +"`"+ x.op + x.value.replaceAll(/[‘|’|“|”]/g,'\'') )
              if (x.field=='__序号__')
                where_arr.push(`( (${this.obj.ds}.index+1) ${x.op}`+ x.value.replaceAll(/[‘|’|“|”]/g,'\'') +")" )
              else
                where_arr.push(`(${this.obj.ds}['${x.field}']${x.op}`+ x.value.replaceAll(/[‘|’|“|”]/g,'\'') +")")
              where_arr.push(x.op_op)
            }
            )
            ret_s=ret_s+'['+ where_arr.slice(0,where_arr.length-1).join(" ")  + ']'
        }
        if(this.obj.group && this.obj.group.filter(x=>x!="__序号__").length>0){
          console.info(this.obj.group)
          ret_s=ret_s+'.groupby(["'+this.obj.group.filter(x=>x!="__序号__").join('","')+'"]).sum().reset_index()'
        }
        if(this.obj.sort_field  && this.obj.sort_field!="__序号__")
        {
          ret_s=ret_s+'.sort_values("' +this.obj.sort_field+'",ascending='+this.obj.sort+').reset_index()'
        }
        if(this.obj.topType==='top' && this.obj.top )
           ret_s=ret_s+`[:${this.obj.top||''}]`
        else if(this.obj.topType==='bottom' && this.obj.bottom )
           ret_s=ret_s+`[-${this.obj.bottom||''}:]`
        else if(this.obj.topType==='between' && (this.obj.start || this.obj.end))
          ret_s=ret_s+`[${this.obj.start||''}:${this.obj.end||''}]`
        
        let cur_df=ret_s
        if(this.obj.resultType==='detail'){
          let arr=[]
          ret_s="__tmp_ds__="+ret_s+"\n"
          if(this.obj.select && this.obj.select.length>0){
            this.obj.select.forEach(x=>{
                  if (x.field=='__序号__')
                    arr.push('"'+ ( (x.before||'') + `" + (__tmp_ds__.index+1)` + '.astype(str) +"'+ (x.after||'') +'"'))
                  else
                    arr.push('"'+ ( (x.before||'') + `" + __tmp_ds__["` +x.field + '"].astype(str) +"'+ (x.after||'') +'"'))
                }
                )
            if (this.obj.line_join===undefined)
              this.obj.line_join="\\n"
            ret_s=ret_s+ this.obj.name+"= ('"+ this.obj.line_join.replace("'","\\'") +"'.join([str(x) for x in (  "+  arr.join("+")  + "   ).values]))"
            return ret_s
          }
        }
        else if(this.obj.resultType==='sum'){
          if(this.obj.sum_field!=""&& this.obj.sum_field!="__序号__")
            ret_s=ret_s+'.sum()["' +this.obj.sum_field+'"]'
          else
            ret_s=ret_s+'.sum().reset_index()'
        }
        else
          ret_s=ret_s+".reset_index(drop=True)"
        return ret_s
      }
      return "==="
    }
  },
  data() {
      return {
        fullscreen:true,
        dialogVisible:this.visible,        
        ds_dicData:[],
        field_dicData:[],
        obj: {var_type:"sum" },
        option: this.getOption()
      }
  }
}
</script>
<style scoped>
  .el-tag {
    color: red;
    white-space: initial;
}
.el-tag.el-tag--info {
    background-color: #f4f4f5;
    border-color: #e9e9eb;
    color: #e01f78;
}
</style>>

</style>