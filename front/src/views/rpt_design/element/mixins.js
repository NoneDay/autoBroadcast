import {request} from 'axios'
import x2js from 'x2js' 

export default {
    props: {
        select:{
          type: Object,
          default: () => {
            return {}
          }
        },parent:{
          type: Object,
          default: () => {
            return {}
          }
        },index:Number,
        self: {
          type: Object,
          default: () => {
            return {}
          }
        },
        params: {
          type: Object,
          default: () => {
            return {}
          }
        }
    },
    inject: ["fresh_ele","context"],
    data () {
      return {
        selectWidget: this.select ,
        
      }
    },
    watch: {
        select (val) {
          this.selectWidget = val
        },
        selectWidget: {
          handler (val) {
              this.$emit('update:select', val)
          },
          deep: true
        },
        'self.gridName'(newVal,oldVal){
          delete this.context.clickedEle[oldVal]
          if(this.self.gridName && this.self.gridName!="_random_")
            this.$set(this.context.clickedEle,this.self.gridName,{data:{},cell:null,column:{}})
        },
        'fresh_ele':{//这里有个问题，会照成重复刷新
          handler:function(newVal,oldVal){
            
            if(!this.self.datasource || !this.buildDisplayData)
              return 
            if(this.buildDisplayData && this.fresh_ele.find(x=>x==this.self.datasource))
            {
              console.info("重构"+this.self.gridName)
              if(this.refresh)
                this.refresh()
              else{
                this.buildDisplayData()
              }
            }
          },deep:true,
        }
    },
    computed: {
      
    },
    methods:{
      click_fresh(p_data){
        
        this.fresh_ele.splice(0)
        this.fresh_ele.push("元素选中行:"+this.self.gridName)//: Date.now() + '_' + Math.ceil(Math.random() * 99999});
        console.info(this.self.fresh_ds)
        console.info(this.self.fresh_params)
        if(this.self.fresh_ds.length==0)
          return;
        if(this.context.in_exec_url.stat){
          this.$notify({title: '提示',message: "已经在执行一个查询！",type: 'error',duration:3000});
          return
        }
        let x2jsone=new x2js(); //实例
        let _this=this
        let data=new FormData();
        console.info(_this.context.report)
        data.append("content", x2jsone.js2xml({report:_this.context.report}) )
        data.append("fresh_ds", JSON.stringify(this.self.fresh_ds))
        let t_params=[];
        this.self.fresh_params.forEach(ele=>{
          if(ele.value.startsWith("原始参数:"))
            return;
          t_params.push({"name":ele.name,"value":p_data.data[ele.value]})
        })
        data.append("fresh_params", JSON.stringify(t_params))
        _this.context.in_exec_url.stat=true;
        let url= '/report5/design/preview'
        //if(this.context.design)
        //  url= '/report5/design/preview'
        //else
        //  url="todo"
        request({
          method: 'post',
          //url: '/report5/default?reportName=2019/2jidu/kb_dangri2.cr',
          url,
          headers:{"needType": "json","worker_no":"14100298","Authorization":"Bearer d2762dbd"},
          data
          ,withCredentials: true
        }).then(response => {
          _this.context.in_exec_url.stat=false;
          if(response.data.errcode && response.data.errcode ==1){
            _this.$notify({title: '提示',message: response.data.message,duration: 0});
            return;
          }
          console.info(response.data)
          _this.fresh_ele.splice(0)
          Object.keys(response.data.dataSet).forEach(name => {
            _this.context.report_result.dataSet[name] =response.data.dataSet[name]  
            _this.fresh_ele.push("数据集:"+name);
          });
          _this.$notify({title: '提示',type: 'success',message: _this.fresh_ele,position: 'bottom-right',duration: 3000});
        }).catch(error=> { 
          _this.context.in_exec_url=false;
          _this.$notify({title: '提示',message: error.response.data,type: 'error',duration:0});
        })
      }
    },
    created(){
      if(this?.self?.gridName){
        if(this?.self?.gridName=="_random_")
          return
        console.info(this.self.gridName+":created")
        this.$set(this.context.clickedEle,this.self.gridName,{data:{},cell:null,column:{}})
      }
    },
    beforeDestroy(){
      if(this?.self?.gridName){
        console.info(this.self.gridName+":beforeDestroy")
        delete this.context.clickedEle[this.self.gridName]
      }
    },
    
}