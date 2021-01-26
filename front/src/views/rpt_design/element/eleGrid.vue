<template>
	<div style="width:100%;height:100%"  v-if="old_content==self.content" >
		<RuntimeTemplateCompiler :template="self.content" :parent="parentCompent"/>
	</div>
</template>
<script>
import {convert_csv_to_json,convert_array_to_json,build_chart_data, deepClone } from "../utils/util"


import { RuntimeTemplateCompiler } from 'vue-runtime-template-compiler'
import mixins from "./mixins"
import dyncTemplateMinxins from "./dyncTemplateMinxins"

export default {
    name:"ele-grid",
    components: { RuntimeTemplateCompiler }, 
    mixins:[mixins,dyncTemplateMinxins],
    mounted(){
    },
    data: () => ({
        currentPage: 1,
        tableData:[],
        real_data:[]
    }),
    watch:{
        "self":{
            handler(val,oldVal){
                this.refresh();
            },deep:true
        }, 
    },
    created(){
        this.buildDisplayData()
    } ,
    methods: { 
        buildDisplayData(){
            if(Object.keys(this.context.report_result).length<2 && this.self.datasource!='示例')
            {
                this.$message.warning("先点击预览，才能配置与报表结果有关的元素");
                return;
            }
            let {valid_data,valid_fileds,real_data}=build_chart_data(this.self.datasource,this.context,this.self.fields)
            this.tableData = convert_array_to_json(valid_data)
            this.real_data=convert_array_to_json(real_data)
            if(this.real_data.length && this.self.gridName!="_random_"){ 
                this.$set(this.context.clickedEle,this.self.gridName,{data:this.real_data[0],cell:null,column:null})
            }
        },
        cell_click(row, column,cell, event){
            
            let cur_data=this.real_data.filter(x=>{
                for(let key in row){
                    if(row[key]!=x[key])
                    {
                        return false
                    }
                }
                return true
            } )
            if(cur_data.length){
                if(this.context.clickedEle[this.self.gridName])
                    this.context.clickedEle[this.self.gridName]={data:deepClone(cur_data[0]),cell:cell.innerText,column}
                else
                    this.$set(this.context.clickedEle,this.self.gridName,{data:deepClone(cur_data[0]),cell:cell.innerText,column})
                this.click_fresh(this.context.clickedEle[this.self.gridName])
            }
            
        }
  },
}
</script>

<style>

</style>