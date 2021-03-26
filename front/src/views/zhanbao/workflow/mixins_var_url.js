let props={
    anchor: ['Left', 'Right', 'Top', 'Bottom', [0.3, 0, 0, -1], [0.7, 0, 0, -1], [0.3, 1, 0, 1], [0.7, 1, 0, 1]],
    connector: ['StateMachine', {margin: 0, curviness: 10, proximityLimit: 80}],
    endpoint: ['Blank', {Overlays: ''}],
    overlays: [ ['Arrow', { width: 8, length: 8, location: 1}] 
    ], // overlay
    // 添加样式
    //paintStyle: { stroke: '#909399', strokeWidth: 2 ,outlineWidth: 10}, // connector
    //hoverPaintStyle: {stroke:"black", strokeWidth: 3},
    // endpointStyle: { fill: '#909399',  outlineWidth: 1 } // endpoint
    //scope: 'jsPlumb_DefaultScope' 
    }
let jsplumbSetting= {
    Anchor: ['Left', 'Right', 'Top', 'Bottom', [0.3, 0, 0, -1], [0.7, 0, 0, -1], [0.3, 1, 0, 1], [0.7, 1, 0, 1]],
    // 动态锚点、位置自适应
    Anchors: ['Left', 'Right', 'Top', 'Bottom', [0.3, 0, 0, -1], [0.7, 0, 0, -1], [0.3, 1, 0, 1], [0.7, 1, 0, 1]],
    // 容器ID
    Container: 'efContainer',
    // 连线的样式，直线或者曲线等，可选值:  StateMachine、Flowchart，Bezier、Straight
    //Connector: ['Bezier', {curviness: 100}],
    // Connector: ['Straight', {stub: 20, gap: 1}],
    // Connector: ['Flowchart', {stub: 30, gap: 1, alwaysRespectStubs: false, midpoint: 0.5, cornerRadius: 10}],
    Connector: ['StateMachine', {margin: 0, curviness: 10, proximityLimit: 80}],
    // 鼠标不能拖动删除线
    ConnectionsDetachable: false,
    // 删除线的时候节点不删除
    DeleteEndpointsOnDetach: false,
    /**
     * 连线的两端端点类型：圆形
     * radius: 圆的半径，越大圆越大
     */
    // Endpoint: ['Dot', {radius: 5, cssClass: 'ef-dot', hoverClass: 'ef-dot-hover'}],
    /**
     * 连线的两端端点类型：矩形
     * height: 矩形的高
     * width: 矩形的宽
     */
    // Endpoint: ['Rectangle', {height: 20, width: 20, cssClass: 'ef-rectangle', hoverClass: 'ef-rectangle-hover'}],
    /**
     * 图像端点
     */
    // Endpoint: ['Image', {src: 'https://www.easyicon.net/api/resizeApi.php?id=1181776&size=32', cssClass: 'ef-img', hoverClass: 'ef-img-hover'}],
    /**
     * 空白端点
     */
    Endpoint: ['Blank', {Overlays: ''}],
    // Endpoints: [['Dot', {radius: 5, cssClass: 'ef-dot', hoverClass: 'ef-dot-hover'}], ['Rectangle', {height: 20, width: 20, cssClass: 'ef-rectangle', hoverClass: 'ef-rectangle-hover'}]],
    /**
     * 连线的两端端点样式
     * fill: 颜色值，如：#12aabb，为空不显示
     * outlineWidth: 外边线宽度
     */
    EndpointStyle: {fill: '#1879ffa1', outlineWidth: 1},
    // 是否打开jsPlumb的内部日志记录
    LogEnabled: true,
    /**
     * 连线的样式
     */
    PaintStyle: {
        // 线的颜色
        stroke: '#909399',
        // 线的粗细，值越大线越粗
        strokeWidth: 1,
        // 设置外边线的颜色，默认设置透明，这样别人就看不见了，点击线的时候可以不用精确点击，参考 https://blog.csdn.net/roymno2/article/details/72717101
        outlineStroke: 'transparent',
        // 线外边的宽，值越大，线的点击范围越大
        outlineWidth: 10
    },
    DragOptions: {cursor: 'pointer', zIndex: 2000},
    /**
     *  叠加 参考： https://www.jianshu.com/p/d9e9918fd928
     */
    Overlays: [
        // 箭头叠加
        ['Arrow', {
            width: 10, // 箭头尾部的宽度
            length: 8, // 从箭头的尾部到头部的距离
            location: 1, // 位置，建议使用0～1之间
            direction: 1, // 方向，默认值为1（表示向前），可选-1（表示向后）
            foldback: 0.623 // 折回，也就是尾翼的角度，默认0.623，当为1时，为正三角
        }],
        // ['Diamond', {
        //     events: {
        //         dblclick: function (diamondOverlay, originalEvent) {
        //             console.log('double click on diamond overlay for : ' + diamondOverlay.component)
        //         }
        //     }
        // }],
        ['Label', {
            label: '',
            location: 0.1,
            cssClass: 'aLabel'
        }]
    ],
    // 绘制图的模式 svg、canvas
    RenderMode: 'svg',
    // 鼠标滑过线的样式
    HoverPaintStyle: {stroke: '#909399', strokeWidth: 4},
    // 滑过锚点效果
    // EndpointHoverStyle: {fill: 'red'}
    Scope: 'jsPlumb_DefaultScope' // 范围，具有相同scope的点才可连接
}
import * as service from '@/api/zhanbao'
import { baseUrl } from '@/config/env';
import {convert_array_to_json} from "@/views/rpt_design/utils/util"
export default {
    data() {
        return {
              in_menu:false,
              page: {
                pageSize: 20,
                pagerCount:5,
                currentPage:1,
                total:0,
              },
        }
    },
    watch:{
        
    },
    computed:{
        all_image(){
            let rets=[]
            this.files_template_exec_result?.all_files?.filter(x=> x.endsWith('.png')|| x.endsWith('.JPG') ).forEach(one_png=>
            {
                rets.push(baseUrl+'/mg/image_file/'+ this.curr_report_id+'/'+one_png )
            })
            return rets
        },
        tableData_option(){      
            let ret_columns=[]
            if(this.ds_data.ds_dict && this.ds_data.ds_dict[this.cur_ds]){
                this.ds_data.ds_dict[this.cur_ds].columns.forEach(x=>{
                    ret_columns.push({label:x,prop:x})
                })
                ret_columns[0].fixed=true
                return {
                    title:this.cur_ds,
                    refreshBtn:false,saveBtn:false,updateBtn:false,menu:false,
                    cancelBtn:false,addBtn:false,delBtn:false,editBtn:false,
                    column:ret_columns
                }
            }
            return []
            },
        tableData(){      
            if(this.ds_data.ds_dict && this.ds_data.ds_dict[this.cur_ds]){
                let ret=this.ds_data.ds_dict[this.cur_ds].data
                this.page.total=ret.length
                this.page.currentPage=1
                return ret
            }
            return []
            },
        all_ds(){
            let ret_arr=[]
            if(this.config_data.data_from)
                this.config_data.data_from.forEach(element => {
                if(element.ds)
                    element.ds.forEach(one=>ret_arr.push(one))
            });
            if(this.config_data.vars===undefined)
                this.config_data.vars=[]
            if(this.config_data.text_tpls===undefined)
                this.config_data.text_tpls=[]
            return ret_arr
        },        

    },
    methods:{

        //变量定义的有关函数
        handleDeleteVar(tag){
            this.config_data.vars.splice(this.config_data.vars.indexOf(tag), 1);
        },
        handleEditVar(tag){
            this.tmp_obj=tag
            this.varDetailDialog_visible=true
        },
        varDetailDialog_submit(form){            
            if(this.config_data.vars===undefined)
                this.config_data.vars=[this.deepClone(form.newVal)]
            else{
                let {obj,obj_type,parent}=this.getByName(form.name)
                
                const vars=this.config_data.vars
                if(form.old_Val.name){
                let idx=this.findArray(vars,form.old_Val.name,'name');
                if(idx>=0){
                    if( obj && this.activeElement.node!=obj){
                        this.$message({message: '名字重复',type: 'warning'});
                        return
                    }
                    vars.splice(idx, 1,form.newVal);
                }
                }else{
                    vars.push(form.newVal)
                }
            }
        },
        varDetailDialog_show(var_type){
            this.tmp_obj={var_type:var_type}
            this.varDetailDialog_visible=true
        },


        addUrlFrom(type){
            if(type=="sql"){
                let data_from={'form_input': [], 'ds':[{"type":"json","name":"修改名字"}],'type':'sql','url':"" }
                while(this.getByName(data_from.ds[0].name).obj){
                    data_from.ds[0].name="修改"+Math.ceil(Math.random() * 999)
                }
                this.config_data.data_from.push(data_from)
                this.config_data.ds_queue.push(data_from.ds[0].name) 
                this.fresh_plumb()
                return
            }
            this.$prompt('请输入', type, {confirmButtonText: '确定',cancelButtonText: '取消',customClass:"inputDialog"})
                .then(async ({value}) => {
                    if(value.startsWith("view-source:")){
                        value=value.substring("view-source:".length)
                    }
                    let data_from={'form_input': [], 'ds': [],'type':type,'url':value }
                    if(['html','json'].includes(type) && !data_from['url'].startsWith("结果")){
                        let match_arr=[]
                        this.$store.getters.canReadSys.forEach(one_sys=>{
                          one_sys.patterns.forEach(one_pat=>{
                            if (data_from.url.startsWith(one_pat))
                              match_arr.push([one_sys.name,one_pat])
                          })
                        })
                        if (match_arr.length==0){
                          
                          if(data_from.url.endsWith(".csv") || data_from.url.endsWith(".xlsx"))
                          {
                            data_from.type="file"
                          }
                          else{
                            this.$message.error('这个网址没有可匹配的系统，如果确实没输入错误，请联系管理员添加对该系统的支持')
                            return 
                          }
                        }else{
                          match_arr.sort(function(a,b){return b[1].length-a[1].length})
                          data_from.type=match_arr[0][0]
                        }
                    }                              
                    let old_this = this
                    if (!data_from['url'].startsWith("结果")){
                        const res_data = await service.initDatafrom({ data_from: data_from,curr_report_id:old_this.curr_report_id })
                        data_from=res_data.data_from
                        this.show_result(res_data)
                    }
                    old_this.fresh_plumb()
                }).catch(error=>this.$message(error,type="error"));                
        },
        url_submit(form,done){
            Object.assign(this.activeElement.node, form)
            done()
            this.url_visible=false
        },
        url_option(){
            let ret= {
                column: [
                    {label: "网址",prop: "url" ,span:24,rules: [{required: true,message: "请输入网址",trigger: "blur"}]
                    },
                    {label: "类型",prop: "type" ,type:'select',      value: 'html',
                    dicData:[
                            {value:'html', label:'html'},
                            {value:'file', label:'数据文件'},
                            {value:'sql', label:'sql加工'}
                    ],
                    rules: [{required: true,message: "请选择类型",trigger: "blur"}]
                    },
                {label: "描述",prop: "desc"},
                ]}
            if(!['sql','file'].includes(this.activeElement.node.type))
            ret.column.push(
                {
                    type: 'dynamic',
                    label: '参数设置',
                    span: 24,
                    display: true,
                    prop: 'form_input',
                    children: {
                        align: 'center',
                        headerAlign: 'center',
                        index: false,
                        addBtn: true,
                        delBtn: true,
                        column: [
                        { prop: 'label',     label: '标签', cell:false,readonly:true  },
                        { prop: 'name',      label: '参数名字', cell:false,readonly:true  },
                        { prop: 'value',     label: '参数值', cell:true },
                        { prop: 'type',     label: '类型', cell:true ,readonly:true},
                        { prop: 'valueList',type:'title',styles:{'font-weight':100,fontSize:'11px'}, label: '可用值提示', cell:true,readonly:true },
                        ] 
                    }
                }
            )
            return ret
        },
        getByName(name){
            let ret=this.config_data.vars.find(x=>x.name==name)
            if(ret)
                return {obj:ret,obj_type:'变量',parent:this.config_data.vars}
            let ret_df
            let ret_ds
            ret=this.config_data.data_from.every(data_from=>{
                ret_df=data_from.ds
                return ret_df.every(ds=>{
                    ret_ds=ds
                    return ds.name!=name
                })
            })
            if(!ret)
                return {obj:ret_ds,obj_type:'数据集',parent:ret_df}
            return {}
        },
        urlData_ds_submit(form,done){
            let {obj,obj_type,parent}=this.getByName(form.name)
            if(obj && this.activeElement.node!=obj){
                this.$message({message: '名字重复',type: 'warning'});
                return
            }
            if(this.activeElement.node.backup!=form.backup){

            }
            if(this.activeElement.node.name!=form.name){//替换ds_queue和ds_depend中的名字
                let old_name=this.activeElement.node.name
                let idx=this.config_data.ds_queue.indexOf(old_name)
                this.config_data.ds_queue[idx]=form.name
                this.config_data.ds_depend.forEach(one=>{
                    one.master=one.master.replace(":"+old_name,":"+form.name )
                    one.depend=one.depend.replace(":"+old_name,":"+form.name )
                })
                this.config_data.vars.forEach(one=>{
                    if(one.ds==old_name){
                        one.ds=form.name
                        one.last_statement.replaceAll(old_name+ "[", form.name+"[")
                    }
                })
                this.config_data.data_from.forEach(data_from=>{
                    data_from.ds.forEach(ds=>{
                        ds.append?.forEach(one=>{
                            let arr=one.from.split(":")
                            if(arr.length==1 && arr[0]==old_name)
                                one.from=form.name
                            else if(arr.length==2 && arr[1]==old_name)
                                one.from=arr[0]+":"+form.name
                        })
                    })
                })
                let _this=this
                this.fresh_plumb()
            }
            Object.assign(this.activeElement.node, form)
            done()
            this.urlData_ds_visible=false
        },
        urlData_ds_option()
        {
            let columns_name=[]
            this.activeElement.node?.old_columns?.forEach(col=>{
                columns_name.push({label:col,value:col})
            })
            return {
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
                { prop: 'backup', label: '备份'},
                { prop: 'view_columns',span:24, type:'checkbox',label: '选择显示列',dicData:columns_name},          
                { prop: 'key_column',span:24, type:'radio',label: '选择关键字',dicData:columns_name},   
                ]
            }
        },
        test_ds_queue(from,to){ // 新队列里的顺序应该是，先有 before 后有 after ，所以如果原先顺序就是这样，就不用改
            let new_arr=[]
            let tmp_ds_names=[]
            let tmp_ds_depend= JSON.parse(JSON.stringify(this.config_data.ds_depend))
            if(from.split(":")[0]=='裁剪')
                tmp_ds_depend.push({master: from, depend : to })
            if(from.split(":")[0]=='最终')
                tmp_ds_depend.push({master: to, depend : from })
            this.all_ds.forEach(ds=>{tmp_ds_names.push(ds.name)})
            tmp_ds_depend=tmp_ds_depend.filter(x=>x.master.split(":")[0]!='来自' && x.master.split(":")[1] !=x.depend.split(":")[0] )
            let hasAdd=false
            while(tmp_ds_names.length>0){
                hasAdd=false
                for(let i_ds_names in tmp_ds_names){
                    let ds_name=tmp_ds_names[i_ds_names]
                    let canCalc=true
                    for(let i in tmp_ds_depend){
                        if (ds_name==tmp_ds_depend[i].master.split(":")[1] && !new_arr.find(x=>x==tmp_ds_depend[i].depend.split(":")[1]))
                        {
                            canCalc=false
                            break
                        }
                    }
                    if(canCalc){
                        new_arr.push(ds_name)
                        tmp_ds_names.splice(i_ds_names,1)
                        hasAdd=true
                        break
                    }                    
                }
                if(hasAdd==false){
                    return [tmp_ds_names,new_arr]
                }
            }
            return [tmp_ds_names,new_arr]            
        },
        // 是否具有该线
        hasLine(from, to) {
            if(from.split(":")[1]==to.split(":")[1] ){ //同一个数据集之间的连接
                if(from.split(":")[0]=='最终' && to.split(":")[0]=='合并'){
                    return "不能反向"
                }
                for (let i = 0; i < this.lineList.length; i++) {
                    let line = this.lineList[i]
                    if(line.source==from && line.target==to){
                        return "已有合并"
                    }
                }
                return ""
            }
            //if(['昨日','上次'].includes(from.split(":")[0]) && from.split(":")[1]!=to.split(":")[1]){
            //    return "['昨日','上次']只能合并到自身。合并到其他数据集现在不支持"
            //}
             //不同数据集之间的连接
            for (let i = 0; i < this.lineList.length; i++) {
                let line = this.lineList[i]
                if(line.source==from && line.target==to){
                    return "已有合并"
                }
                if (line.source.split(":")[1] == from.split(":")[1]  && line.target.split(":")[1] == to.split(":")[1] ) {
                    return "已有其他种类合并"
                }
                if (line.source.split(":")[1] == to.split(":")[1]  && line.target.split(":")[1] == from.split(":")[1] ) {
                    return "已有反向合并，不能继续"
                }
            }
            return ""
        },        
        fresh_plumb(){
            this.plumbIns.deleteEveryConnection()
            this.plumbIns.deleteEveryEndpoint()
            this.plumbIns.unmakeEveryTarget()
            this.plumbIns.unmakeEverySource()
            let _this=this
            this.$nextTick(() => {
                if(_this.curr_report_id!=-1)
                    _this.reload_line()
            });
        },
        reload_line(){

            
            let plumbIns=this.plumbIns
            this.loadFinish=false
            this.lineList=[]
            
 
            let init_ds_depend=false
            if(this.config_data.ds_depend==undefined){
                this.$set(this.config_data,"ds_depend",[])
                init_ds_depend=true
            }
            if(this.config_data.ds_queue==undefined){
                this.$set(this.config_data,"ds_queue",[])
            }
            this.config_data.data_from.forEach((data_from,idx) => {
                data_from.ds.forEach(ds => {
                    if(!this.config_data.ds_queue.find(x=>x==ds.name))
                        this.config_data.ds_queue.push(ds.name)
                })
            })
            this.config_data.template_output_act.filter(x=>x.canOutput=='false' && ['csv','xlsx'].includes( x.file.split('.')[1]))
            .forEach(one=>{
                plumbIns.makeSource('文件:'+one.file)
            })
            this.config_data.ds_queue.forEach(one => {
                let data_from,idx,ds
                this.config_data.data_from.forEach( (x,i)=>{
                    if(data_from)
                        return
                    ds=x.ds.find(c=>c.name==one)
                    if(ds){
                            data_from=x
                            idx=i
                    }
                })
                if(data_from.url.startsWith('结果://')){
                    this.lineList.push({source: "URL:"+idx,target: "合并:"+ds.name,})
                    this.lineList.push({source: "合并:"+ds.name,target: "最终:"+ds.name,})
                }else{
                    
                    if(data_from.type!='sql'){
                        plumbIns.makeSource("裁剪:"+ds.name)
                        plumbIns.makeSource("最终:"+ds.name)
                    }
                    if(ds.backup){
                        plumbIns.makeSource("上次:"+ds.name)
                        plumbIns.makeSource("昨日:"+ds.name)
                    }
                    
                    plumbIns.makeTarget("合并:"+ds.name)
                
                    if( ! ['sql','file'].includes( data_from.type)){
                        this.lineList.push({source: "URL:"+idx,target: "裁剪:"+ds.name,})
                        this.lineList.push({source: "裁剪:"+ds.name,target: "合并:"+ds.name,})
                    }else{
                        this.lineList.push({source: "URL:"+idx,target: "合并:"+ds.name,})
                    }
                    this.lineList.push({source: "合并:"+ds.name,target: "最终:"+ds.name,})
                    ds.append?.forEach((other,o_idx)=>{
                        if(other.from.substring(0,2)=="上次"){
                            let add_name=other.from.substring(3)
                            if(!add_name)
                                add_name=ds.name
                            this.lineList.push({labelLocation:0.9,label:""+o_idx,source: "上次:"+add_name,target: "合并:"+ds.name,canDelete:true})
                        }
                        else if(other.from.substring(0,2)=="备份"){
                            let add_name=other.from.substring(3)
                            if(!add_name)
                                add_name=ds.name
                            this.lineList.push({labelLocation:0.9,label:""+o_idx,source: "昨日:"+add_name,target: "合并:"+ds.name,canDelete:true})
                        }else{
                            //查找from是否在to之前 先计算
                            let from_other_pos=this.config_data.ds_queue.findIndex(x=>x==other.from)
                            let ds_pos=this.config_data.ds_queue.findIndex(x=>x==ds.name)
                            if(from_other_pos<0){
                                this.lineList.push({labelLocation:0.9,label:""+o_idx,source: "文件:"+other.from,target: "合并:"+ds.name,canDelete:true})
                            }
                            else if(  from_other_pos < ds_pos ){
                                this.lineList.push({labelLocation:0.9,label:""+o_idx,source: "最终:"+other.from,target: "合并:"+ds.name,canDelete:true})
                                if(init_ds_depend)
                                    this.config_data.ds_depend.push({master: "合并:"+ds.name, depend : "最终:"+other.from })
                            }
                            else{
                                this.lineList.push({labelLocation:0.9,label:""+o_idx,source: "裁剪:"+other.from,target: "合并:"+ds.name,canDelete:true})
                                if(init_ds_depend)
                                    this.config_data.ds_depend.push({master: "裁剪:"+other.from, depend : "合并:"+ds.name })
                            }
                        }
                    })
                }
                if(this.config_data.vars.filter(x=>x.ds==ds.name).length>0)
                    this.lineList.push({source: "最终:"+ds.name,target: "来自:"+ds.name,})
            
            });
            
                this.lineList.forEach(element => {
                    //anchor: ['Left', 'Right', 'Top', 'Bottom', [0.3, 0, 0, -1], [0.7, 0, 0, -1], [0.3, 1, 0, 1], [0.7, 1, 0, 1]],
                    if(["上次",'昨日','裁剪'].includes( element.source.split(":")[0]))
                        plumbIns.connect({...props,...element,...{anchor: ['Left', 'Right',]}})
                    else
                        plumbIns.connect({...props,...element})
                }); 
          
            
            this.loadFinish=true  
            
            // 会使整个jsPlumb立即重绘。
            //this.plumbIns.setSuspendDrawing(false, true);
        },
        makeConnectionsActive(item) { // 选择某节点其连线高亮显示
            this.removeConnectionsActive()  // 先删除之前的连线动态效果，再添加
           
            let connections = this.plumbIns.getConnections(item)
            if (connections.length) {
                connections.forEach((connection, index) => {
                let sourceId = connection.sourceId,
                    targetId = connection.targetId,
                    sourceKey = connection.endpoints[0].anchor.x * 10 + '' + connection.endpoints[0].anchor.y * 10,
                    targetKey = connection.endpoints[1].anchor.x * 10 + '' + connection.endpoints[1].anchor.y * 10
                this.plumbIns.connect({ // 添加动态效果即在两节点之间再加一条高亮的线段，故需要获取两个节点id和连线位置
                    source: sourceId,
                    target: targetId,
                    anchors: [connection.endpoints[0].anchor, connection.endpoints[1].anchor],
                    detachable: false,
                    scope: 'activeScope',
                    cssClass: 'point-active-line', // 可设置高亮的效果
                    connector: ['StateMachine'],
                    endpoint: 'Blank',
                    overlays: [ ['Arrow', { width: 8, length: 8, location: 1}] 
                    ], // overlay
                    // 添加样式
                    paintStyle: { stroke: 'black', strokeWidth: 3 ,outlineWidth: 10}, // connector
                    hoverPaintStyle: {stroke:"black", strokeWidth: 3},
                })
            })
            }
        },
        removeConnectionsActive(){
            let connections = this.plumbIns.getConnections({scope: 'activeScope'})
            if (connections.length) {
                connections.forEach((connection) => {
                    this.plumbIns.deleteConnection(connection,{force:true})
                })
            }            
        },
        jsPlumbInit() {
            let _this=this
            // 导入默认配置
            _this.plumbIns.importDefaults(jsplumbSetting)
            // 会使整个jsPlumb立即重绘。
            _this.plumbIns.setSuspendDrawing(false, true);
            // 单点击了连接线, https://www.cnblogs.com/ysx215/p/7615677.html
            _this.plumbIns.bind('click', (conn, originalEvent) => {
                _this.activeElement.type = 'line'
                _this.activeElement.sourceId = conn.sourceId
                _this.activeElement.targetId = conn.targetId
                _this.makeConnectionsActive({source:conn.sourceId,target:conn.targetId})
                //_this.$refs.nodeForm.lineInit({
                //    from: conn.sourceId,
                //    to: conn.targetId,
                //    label: conn.getLabel()
                //})
            })
            // 连线
            _this.plumbIns.bind("connection", (connect_info,evt) => {
                if(connect_info.connection.scope=="activeScope")
                    return
                let from = connect_info.source.id
                let to = connect_info.target.id
                if (_this.loadFinish) 
                {
                    let ds=_this.all_ds.find(x=>x.name==to.split(":")[1])
                    let names=from.split(":")
                    let add_name=""
                    let pos=0
                    if (['昨日','上次'].includes(names[0])){
                        if(names[1]==ds.name){
                            add_name=(names[0]=='昨日'?'备份':"上次")
                        }
                        else{
                            add_name=(names[0]=='昨日'?'备份:':"上次:")+names[1]
                        }
                    }
                    else if (names.length>1){
                        add_name=names[1]
                    }else{ //来自文件
                        add_name=from
                    }
                    if(ds.append==undefined)
                        ds.append=[]
                    if(ds.append.find(x=>x.from==add_name)){
                        return
                    }
                    ds.append.push({"from":add_name})
                    if(from.split(":")[0]=='裁剪')
                        _this.config_data.ds_depend.push({master: from, depend : to })
                    if(from.split(":")[0]=='最终')
                        _this.config_data.ds_depend.push({master: to, depend : from })
                    _this.lineList.push({source: from, target: to,canDelete:true})
                    _this.fresh_plumb()
                }
            }),
            // 删除连线回调
            _this.plumbIns.bind("connectionDetached", (evt) => {
                _this.deleteLine(evt.sourceId, evt.targetId)
            })

            // 改变线的连接节点
            _this.plumbIns.bind("connectionMoved", (evt) => {
                _this.changeLine(evt.originalSourceId, evt.originalTargetId)
            })

            // 连线右击
            _this.plumbIns.bind("contextmenu", (connect_info,evt) => {
                console.log('contextmenu', evt)
                _this.showMenu("line",connect_info,evt)
            })

            // 连线
            _this.plumbIns.bind("beforeDrop", (evt) => {
                if(evt.scope=="activeScope")
                    return 
                let from = evt.sourceId
                let to = evt.targetId
                
                if (from === to) {
                    _this.$message.error('节点不支持连接自己')
                    return false
                }
                let msg=_this.hasLine(from, to) 
                if (msg) {
                    _this.$message.error(msg)
                    return false
                }
                let [tmp_ds_names,new_arr]=[..._this.test_ds_queue(from,to)]
                if(tmp_ds_names.length>0){
                    _this.$message.error("循环引用："+tmp_ds_names.toString())
                    return false
                }
                _this.config_data.ds_queue=new_arr
                _this.$message.success('连接成功')
                return true
            })

            // beforeDetach
            _this.plumbIns.bind("beforeDetach", (evt) => {
                if(evt.scope=="activeScope")
                    return 
                let line=_this.lineList.find(x=>x.source==evt.sourceId && x.target==evt.targetId)
                if(line.canDelete){
                    return true
                }
                return false
            })
            _this.plumbIns.setContainer(_this.$refs.efContainer)
            
        },
        showMenu (type,for_obj,event,node_this) {
            let _this=this
            if(_this.in_menu)
                return
            try{
                _this.in_menu=true
                if(type=="画布"){
                    event.preventDefault()
                    let menu_items=[ {label: "添加来至于报表的数据",icon: "el-icon-attract",onClick:function(){
                        _this.addUrlFrom('html')
                    }},
                    
                    {label: "添加专业合并",icon: "el-icon-attract",onClick:function(){
                        _this.addUrlFrom('sql')
                    }},
                    {divided:true},
                    {label: "查询数据集数据",icon: "el-icon-view",onClick:function(){
                        _this.query_data() 
                    }},
                    
                    {label: "执行生成",icon: "el-icon-video-play",onClick:function(){
                        _this.files_template_exec() 
                    }},
                    {label: "保存",icon: "el-icon-save",onClick:function(){
                        _this.save_config() 
                    }},
                    {label: "添加自定义变量",onClick:function(){
                        _this.varDetailDialog_show('detail')
                    }},
                    {divided:true},
                    
                    {label: "重新载入定义",icon: "el-icon-refresh",onClick:function(){
                        _this.reload_define() 
                    }},
                    
                    {label: "总控参数设置",onClick:function(){
                        _this.form_input_title = '需要的参数'
                        _this.form_input_option = {
                          addBtn:false,delBtn:true,cellBtn:true,editBtn:false,cellEdit:true,rowKey:'name',
                          column: [{ prop: 'name', label: '参数名字', cell:false,formslot:true  },{ prop: 'value', label: '参数值', cell:true }] 
                        }
                        _this.form_input_obj = _this.config_data.form_input
                        _this.form_input_submit=function(){
                          _this.config_data.form_input=_this.form_input_obj 
                          _this.form_input_obj={}
                          }
                        _this.form_input_visible = true

                    }},
                    ]
                    this.$contextmenu({items:menu_items,event,customClass: "contextmenu_zb",zIndex: 3000,minWidth: 230})
                }else
                if(type=="line"){
                    event.preventDefault()
                    let from = for_obj.source.id, to = for_obj.target.id
                    let from_type=from.split(":")[0], to_type=to.split(":")[0]
                    let from_name=from.split(":")[1], to_name=to.split(":")[1]
                    
                    if(to_type!='合并')
                        return

                    let menu_label="删除"
                    if (to_type=='来自' || from_type=='URL' || from_type=='sql' || ((from_name==to_name) && false==['上次','昨日'].includes( from_type) ))
                        return
                    
                    this.$contextmenu({
                        items: [
                        {label: from+"=>"+to},{divided:true},
                        {label: from_name+"【"+(from_type=="文件"?"第一列" :  _this.getByName(from_name).obj?.key_column)+"】=="+
                             to_name+"【"+_this.getByName(to_name).obj?.key_column+"】"},{divided:true},
                        {
                            label: menu_label,icon: "el-icon-delete",
                                onClick: () => {
                                    if(menu_label=='删除'){
                                        this.$confirm(`确实要删除针对【${to_name}】的来至于【${from_name==to_name?from_type:from_name}】的数据合并吗？`,'提示', 
                                        {
                                            confirmButtonText: '确定',
                                            cancelButtonText: '取消',
                                            type: 'warning'
                                        })
                                        .then( function () {
                                            let target=_this.getByName(to_name)
                                            if(from_name==to_name){
                                                if(from_type=='昨日')
                                                    from_name='备份'
                                                if(from_type=='上次')
                                                    from_name='上次'
                                            }else{
                                                if(['昨日','上次'].includes( from_type))
                                                    if(from_type=='昨日')
                                                        from_name='备份'+":"+from_name
                                                    if(from_type=='上次')
                                                        from_name=from_type+":"+from_name
                                            }
                                            let find_from_item=target.obj.append?.find(x=>x.from==from_name)
                                            if (find_from_item){
                                                target.obj.append.splice(target.obj.append.indexOf(find_from_item),1)
                                                let ds_depend_idx=_this.config_data.ds_depend.findIndex(x=>x.master==from && x.depend==to)
                                                _this.config_data.ds_depend.splice(ds_depend_idx,1)
                                                _this.removeConnectionsActive()
                                                let connections=_this.plumbIns.getConnections({source:from,target:to})
                                                if (connections.length) {
                                                    connections.forEach((connection, index) => {
                                                        _this.plumbIns.deleteConnection(connection)
                                                    })
                                                }
                                            }
                                        })
                                        .catch(function () {})
                                        
                                    }
                                }
                        },
                        ],event,customClass: "contextmenu_zb",zIndex: 3000,minWidth: 230
                    });
                }else{
                    event.preventDefault()
                    let node=for_obj
                    let menu_items=[ {label: "编辑", icon: "el-icon-edit",onClick:function(){
                        node_this.editNode(node,type) 
                    }},{divided:true},]
                    if (['裁剪'].includes(type)) {
                    if(node['backup']==undefined || node['backup']=='')
                        menu_items.push({label: "启动备份功能",onClick:function(){node['backup']='1';_this.fresh_plumb(); }})
                    else
                        menu_items.push({label: "关闭备份功能",onClick:function(){node['backup']='';_this.fresh_plumb(); }})

                    }

                    if(type=='文件' && node.file.endsWith('.csv')) 
                        menu_items.push({label: "数据作为数据源",onClick:function(){node_this.csvAsDatasource(node,type) }})
                    if(type=='文件' && node.canOutput=='true' && node.file.endsWith('.xlsx')) 
                        menu_items.push({label: "数据作为数据源",onClick:function(){node_this.resultAsDatasource(node,type) }})
                    if (['最终','变量'].includes(type))
                        menu_items.push({label: "克隆",icon: "el-icon-document-copy",onClick:function(){node_this.copyNode(node,type) }})
                    
                    menu_items.push({label: "删除",icon: "el-icon-delete",onClick:function(){node_this.deleteSelected(node,type)} })
                    this.$contextmenu({items:menu_items,event,customClass: "contextmenu_zb",zIndex: 3000,minWidth: 230})
                }
            }finally{
                setTimeout(() => {
                    _this.in_menu=false
                }, 1)
            }
            return false;
        },
        // 删除线
        deleteLine(source, target) {
            this.lineList = this.lineList.filter(function (line) {
                if (line.canDelete && line.source == source && line.target == target) {
                    return false
                }
                return true
            })
        },
        files_template_exec(){
            let old_this=this
            service.files_template_exec(this.curr_report_id, { config_data: this.config_data })
            .then(data=>{
                this.files_template_exec_result = data
                this.files_template_exec_result_visilbe = true
                Object.assign(old_this.config_data,data.config_data)
                this.fresh_plumb()
            }).catch(error=>{
                Object.assign(old_this.config_data,error.config_data)
                this.fresh_plumb()
            })
        },
        show_result(res_data){
            this.query_result_visible = true
            if(res_data.ds_dict){
              res_data.df_arr.forEach(one_df=>{
                let one=JSON.parse( res_data.ds_dict[one_df] )
                res_data.ds_dict[one_df]={data: convert_array_to_json(one.data,0,-1,one.columns),columns:one.columns}
              })
            }
            this.ds_data=res_data
            if(res_data.data_from){
                res_data.data_from.ds.forEach(ds=>{
                    let old_name=ds.name
                    let name_idx=res_data.df_arr.indexOf(ds.name)
                    while(this.getByName(ds.name).obj){
                        ds.name="修改"+Math.ceil(Math.random() * 999)
                    }
                    res_data.df_arr[name_idx]=ds.name
                    if(old_name!=ds.name){
                        res_data.ds_dict[ds.name]=res_data.ds_dict[old_name]
                        delete res_data.ds_dict[old_name]
                    }
                    this.config_data.ds_queue.push(ds.name)
                })
                this.config_data.data_from.push(res_data.data_from)
            }
            this.cur_ds=res_data.df_arr[0]
        },
        query_data( ) {
            let old_this = this
             service.query_data({ config_data: this.config_data,curr_report_id: this.curr_report_id }
            ).then(res_data=>{
                old_this.show_result(res_data)
                Object.assign(old_this.config_data,res_data.config_data)
            }).catch(error=>{
              if( typeof(error.config_data)=="object")
                  Object.assign(old_this.config_data,error.config_data)
            })
            this.fresh_plumb()
        },
        reload_define(){
            //this.$emit("reload_define")    
            let _this=this
            service.getZhanbao(this.curr_report_id).then(data_r=>{
                data_r.config_data = JSON.parse(data_r.config_txt)
                if(undefined== data_r.config_data.template_output_act)
                    data_r.config_data.template_output_act=[]
                Object.assign( this.config_data , data_r.config_data)
                if(data_r.config_data.ds_depend==undefined)
                    delete this.config_data.ds_depend
                if(data_r.config_data.ds_queue==undefined)
                    delete this.config_data.ds_queue

                if(!Array.isArray(this.config_data.template_output_act))
                    this.config_data.template_output_act=[]
                let template_output=this.config_data.template_output_act
                data_r.fileList.forEach(one=>{
                    if(template_output.filter(x=>x.file===one.name).length===0){
                    template_output.push({'file':one.name,'canOutput':"false",'wx_file':'','wx_msg':''})
                    }
                })                
                this.fresh_plumb()
            }).catch(error=>{this.$message({message: error,type: 'error'});})
            
        },
        async save_config() {
            const data = await service.save_config(this.curr_report_id, 
                JSON.parse(JSON.stringify( { config_data: this.config_data,
                    report_name: this.report_name,
                    cron_str: this.cron_str,
                    cron_start: this.cron_start
                }))
              )
            if(data.errcode && data.errcode!=0){
              this.$message.error(data.message)
            }
            else
            this.$message.success("保存成功！")
        },
        
    }
}