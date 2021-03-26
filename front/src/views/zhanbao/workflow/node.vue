<template>
    <div :id="type+':'+node_name"  :style="{'margin-right': ['文件','变量'].includes( type)?'2px':'60px'}"
        @click.prevent="clickNode(node,type)"   
        @contextmenu.prevent="p_this.showMenu(type,node,$event,node_this)"
        @dblclick="editNode(node,type)"   
        :class="nodeClass(node,type)" 
    >
        <i v-if="type=='文件' && node.canOutput=='true'" class="el-icon-s-opportunity"></i>
        {{txt}} 
    </div>

  
</template>

<script>
import * as service from '@/api/zhanbao'
export default {
    name:'zbnode',
    inject: ["p_this"],
    props:['type','node','node_name'],
    data(){
        return {
            
        }
    },
    methods:{
        
        nodeClass(ds,type) {
            let exec_success=false
            let exec_satge='0'
            let end_stage='9'
            let start_stage='0'
            if(ds.exec_stat){
                exec_satge=ds.exec_stat.split(":")[0]
                if(['裁剪','昨日','上次',].includes(type) ){
                    start_stage='0'
                    end_stage='2'
                }
                else if(['合并',].includes(type) ){
                    start_stage='2'
                    end_stage='4'
                }
                else if(['最终',].includes(type) ){
                    start_stage='4'
                    end_stage='9'
                }
            }
            return {
                'ef-node': true,
                'ef-node-canDrop': ['裁剪','昨日','上次','最终',].includes(type),
                'ef-node-success':exec_satge>=end_stage,
                'ef-node-error':exec_satge!='0' && (exec_satge>start_stage && exec_satge<end_stage) ,
                'ef-node-active': this.activeElement.node ==ds && this.activeElement.type ==type,
            }
        },
        
        copyNode(node,type){
            
            if(type=='变量'){
                let new_name=node.name+"_复制"
                while(true){
                    let {obj,obj_type,parent}=this.p_this.getByName(new_name)
                    if (!obj)
                        break
                    new_name=new_name+Math.ceil(Math.random() * 99)
                }
                let new_obj=JSON.parse(JSON.stringify(node))
                new_obj.name=new_name
                this.config_data.vars.push(new_obj)
            } else if(['最终'].includes(type)){
                let new_name=node.name+"_复制"
                while(true){
                    let {obj}=this.p_this.getByName(new_name)
                    if (!obj)
                        break
                    new_name=new_name+Math.ceil(Math.random() * 99)
                }
                let new_obj=JSON.parse(JSON.stringify(node))
                new_obj.name=new_name
                new_obj.append=[]
                new_obj.backup=''
                this.config_data.ds_queue.push(new_name)
                if(new_obj.view_columns)
                    new_obj.last_columns=new_obj.view_columns
                else 
                    new_obj.last_columns=new_obj.old_columns
                new_obj.after_append_columns=[]
                new_obj.sql=""
                new_obj.exec_stat='0:'
                this.p_this.getByName(node.name).parent.push(new_obj)
            }else{
                this.$message({message: '没有实现',type: 'warning'});
            }
            this.p_this.fresh_plumb()
        },
        csvAsDatasource(node){
            
            if(this.config_data.data_from.find(x=>x.url==node.file)){
                 this.$message('已经有数据集了，不用再创建');
                 return
            }
            let ds_name="修改1"
            let _this=this
            while(this.config_data.ds_queue.find(x=>x==ds_name)){
                ds_name="修改"+Math.ceil(Math.random() * 999)
            }
            this.config_data.ds_queue.push(ds_name)
            this.config_data.data_from.push({ 'type': 'file', 'form_input': [], 'ds': [{'name':ds_name}],'url':node.file })
            this.p_this.fresh_plumb()
        },
        async resultAsDatasource(node){
            
            if(this.config_data.data_from.find(x=>x.url=='结果://'+node.file)){
                 this.$message('已经有数据集了，不用再创建');
                 return
            }
            let _this=this
            let new_data_from={ 'type': 'html', 'form_input': [], 'ds': [],'url':'结果://'+node.file }
            const res_data = await service.initDatafrom({ data_from: new_data_from,curr_report_id:this.p_this.curr_report_id })
            
            this.p_this.show_result(res_data,true)
            this.p_this.fresh_plumb()
        },
        editNode(node,type){
            this.p_this.removeConnectionsActive()
            
            this.activeElement.node=node
            this.activeElement.type=type
            this.p_this.tmp_obj=node
            switch (type) {
                case "URL":
                    if(this.node.type=='file' ||this.node.type=='sql' || this.node.url.startsWith("结果://"))
                         this.$message('这种类型的数据源不能修改基本内容');
                    else
                        this.p_this.url_visible=true
                    break;
                case "文件":
                    this.p_this.template_actSet_dialog_visilbe=true
                    
                    break;
                case "最终":
                    if(this.activeElement.node.sql)
                        this.p_this.tmp_obj=this.activeElement.node.sql
                    else
                        this.p_this.tmp_obj=this.p_this.default_sql
                    this.p_this.sql_visible=true
                    break
                 case "变量":
                     this.p_this.handleEditVar(this.activeElement.node)
                     break
                 case "文本模板":
                     this.p_this.handleEditTpl(this.activeElement.node)
                     break                     
                default:
                    this.p_this.urlData_ds_visible=true
                    break;
            }
        },
        clickNode(node,type){
            this.p_this.removeConnectionsActive()
            
            this.activeElement.node=node
            this.activeElement.type=type
        },
        deleteSelected(node,type){
            
            if(!type){
                this.$message({message: '请先选中要删除的项',type: 'warning'});
                return
            }
            let type_name=type
            if(['裁剪','昨日','上次','最终','合并'].includes(type))
                type_name='数据集'
            else if(type=='URL')
                type_name='取数地址'
            else if(type=='file')
                type_name='文件'
            let _this=this
            let idx=-1
            this.$confirm(`此操作将永久删除【${type_name}】=>【${node.name||node.file||node.desc||node.type}】, 是否继续?`, '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                if(['变量'].includes(type)) {
                    let idx=_this.config_data.vars.indexOf(node);
                    if(idx>=0){
                        _this.config_data.vars.splice(idx,1)
                    }
                }else if(['裁剪','昨日','上次','最终','合并'].includes(type)) {
                    _this.deleteDs(node)
                }else if(['URL'].includes(type)) {
                    node.ds.forEach(x=>{
                        _this.deleteDs(x)
                    })
                    let idx=_this.config_data.data_from.indexOf(node)
                    if(idx>=0)
                        _this.config_data.data_from.splice(idx,1)
                }else if(['文本模板'].includes(type)) {
                    _this.p_this.handleDeleteTpl(node)
                }else if(['文件'].includes(type)) {
                    _this.p_this.file_handleRemove(node)
                }else{
                    _this.$message({message: '没实现',type: 'warning'});
                }
                _this.p_this.fresh_plumb()
            }).catch(() => {
                this.$message({
                    type: 'info',
                    message: '已取消删除'
                });          
            });

        },
        deleteDs(ds){
            let ds_depend
            do {
                ds_depend=this.config_data.ds_depend.find(x=>[x.depend.split( ":")[1],x.master.split( ":")[1]].includes(ds.name))    
                if(ds_depend){
                    let idx= this.config_data.ds_depend.indexOf(ds_depend)
                    this.config_data.ds_depend.splice(idx,1)
                }
            } while (ds_depend);
            let idx=this.config_data.ds_queue.indexOf(ds.name)
            if(idx>=0){
                this.config_data.ds_queue.splice(idx,1)
            }
            this.config_data.data_from.forEach(data_from=>{
                data_from.ds.forEach(one_ds=>{
                    let append=one_ds.append?.find(x=>x.from==ds.name)
                    if(append){
                        one_ds.append.splice(one_ds.append.indexOf(append),1)
                    }
                })
            })

            for(let d_idx in this.config_data.data_from){
                let data_from=this.config_data.data_from[d_idx]
                let idx=data_from.ds.indexOf(ds)
                if(idx>=0){
                    data_from.ds.splice(idx,1)
                    break
                }
            }
            this.p_this.fresh_plumb()                  
        },
    },
    computed:{
        activeElement(){
            return this.p_this.activeElement
        },
        config_data(){
            return this.p_this.config_data
        },
        node_this(){
            return this
        },
        txt(){
            if (this.type=='URL'){
                if(this.node.desc)
                    return this.node.desc
                if('file'==this.node.type)
                    return this.node.url
                if(this.node.url.startsWith('结果'))
                    return this.node.url
                if('sql'==this.node.type)
                    return "专业合并数据"
 
                return this.node.type                
            }
            if (['裁剪','昨日','上次','昨日'].includes(this.type)){
                return this.type
            }
            if (['变量','文件','最终'].includes(this.type)){
                return this.node_name
            }
            if (['最终'].includes(this.type)){
                return this.type+':'+this.node.name
            }
            if('文本模板'==this.type)
                return this.node.name
            return this.type

        }
    }
}
</script>

<style  scoped>

</style>