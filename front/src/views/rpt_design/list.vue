<template>
  <div style="height:100%">
      <div><span> 当前目录：</span>
    <el-breadcrumb separator="/" style="display: inline-block;">
    <el-breadcrumb-item > <span @click="path_click(0,0)"> root </span></el-breadcrumb-item>
        <el-breadcrumb-item v-for="(one,idx) in loc_path" :key="idx" 
        ><span @click="path_click(one,idx+1)"> {{ one}} </span></el-breadcrumb-item>
    </el-breadcrumb>
    </div>
    <el-table  :data="tableData.children"
        style="width: 100%;margin-bottom: 20px;"
        row-key="FullPathFileName" :height="'90%'"
        border @row-click="row_click"
        :default-expand-all='False'>
        <el-table-column
        prop="FileName"
        label="FileName">
         <template slot-scope="scope">
            <img :src="scope.row.LastAccessTime?'img/xsl.png':'img/folder.png'"/>
            <span style="margin-left: 10px">{{ scope.row.FileName }}</span>
        </template>
        </el-table-column>
        <el-table-column  prop="LastAccessTime" label="LastAccessTime"/>
        <el-table-column  prop="LastWriteTime" label="LastWriteTime" />
        <el-table-column  prop="Length" label="Length" />
        
        </el-table>
  </div>
</template>

<script>
import {rptList} from "./api/report_api"
export default {
    created(){
        let _this=this
        rptList(this.loc_path.join("/")).then(response_data => {
            _this.tableData=response_data
        }).catch(error=>error)
    },
    data() {
        return {
        tableData:[],
        loc_path:[]
        }
    },
    methods:{
        path_click(one,idx){
            let _this=this
            this.loc_path.splice(idx)
            rptList(this.loc_path.join("/")).then(response_data => {
                _this.tableData=response_data
            }).catch(error=>error)
        },
        row_click(row, column, event){
            if (row.LastAccessTime){
                let filename=this.loc_path.join("/")+"/"+row.FileName
                this.$router.push({
                    path: "/rpt-design/index",
                    query: {label:filename,}
                });
            }else
            {
                let _this=this
                this.loc_path.push(row.FileName)
                rptList(this.loc_path.join("/")).then(response_data => {
                    _this.tableData=response_data
                }).catch(error=>error)
            }
        }
    }
}
</script>

<style>

</style>