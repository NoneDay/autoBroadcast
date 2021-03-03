let jsplumbSetting= {
    // 动态锚点、位置自适应
    Anchors: ['Top', 'TopCenter', 'TopRight', 'TopLeft', 'Right', 'RightMiddle', 'Bottom', 'BottomCenter', 'BottomRight', 'BottomLeft', 'Left', 'LeftMiddle'],
    // 容器ID
    Container: 'efContainer',
    // 连线的样式，直线或者曲线等，可选值:  StateMachine、Flowchart，Bezier、Straight
    Connector: ['Bezier', {curviness: 100}],
    // Connector: ['Straight', {stub: 20, gap: 1}],
    // Connector: ['Flowchart', {stub: 30, gap: 1, alwaysRespectStubs: false, midpoint: 0.5, cornerRadius: 10}],
    // Connector: ['StateMachine', {margin: 5, curviness: 10, proximityLimit: 80}],
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
        stroke: 'red',
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
    HoverPaintStyle: {stroke: '#b0b2b5', strokeWidth: 1},
    // 滑过锚点效果
    // EndpointHoverStyle: {fill: 'red'}
    Scope: 'jsPlumb_DefaultScope' // 范围，具有相同scope的点才可连接
}
import * as service from '@/api/zhanbao'
export default {
    data() {
      return {
      }
    },
    
    computed:{
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
        varDetailDialog_submit(obj){            
            if(this.config_data.vars===undefined)
                this.config_data.vars=[this.deepClone(obj.newVal)]
            else{
                const vars=this.config_data.vars
                if(obj.old_Val.name){
                let idx=this.findArray(vars,obj.old_Val.name,'name');
                if(idx>=0)
                    vars.splice(idx, 1,obj.newVal);
                }else
                vars.push(obj.newVal)
            }
        },
        varDetailDialog_show(var_type){
            this.tmp_obj={var_type:var_type}
            this.varDetailDialog_visible=true
        },


        addUrlFrom(type){
            this.$prompt('请输入', type, {confirmButtonText: '确定',cancelButtonText: '取消',customClass:"inputDialog"})
                .then(async ({value}) => {
                    if(value.startsWith("view-source:")){
                        value=value.substring("view-source:".length)
                    }
                    let data_from={ 'type': 'html', 'form_input': [], 'ds': [],'type':type,'url':value }
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
                      if(data_from['type']=="sql"){
                        data_from.ds={"type":"sqlLite","name":"修改名字"}
                      }
                      else if (!data_from['url'].startsWith("结果")){
                        const res_data = await service.initDatafrom({ data_from: data_from,curr_report_id:old_this.curr_report_id })
                        data_from=res_data.data_from
                      }
                      old_this.config_data.data_from.push(data_from)
                      data_from.ds.forEach(ds=>{
                        while(old_this.config_data.ds_queue.find(x=>x==ds.name)){
                            ds.name="修改"+Math.ceil(Math.random() * 999)
                        }
                        old_this.config_data.ds_queue.push(ds.name)
                      })
                }).catch(error=>console.info(error));
        },
        url_submit(form,done){
            Object.assign(this.activeElement.node, form)
            done()
            this.url_visible=false
        },
        url_option(){
            return {
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

                ]
            }
        },
        urlData_ds_submit(form,done){
            if(this.activeElement.node.backup!=form.backup){
                this.$nextTick(function () {
                    if(form.backup){
                        this.plumbIns.makeSource("上次:"+form.name)
                        this.plumbIns.makeSource("昨日:"+form.name)
                    }else{

                    }
                    this.plumbIns.setSuspendDrawing(false, true);
                })               
            }
            Object.assign(this.activeElement.node, form)
            done()
            this.urlData_ds_visible=false
        },
        urlData_ds_option()
        {
            let columns_name=[]
            this.activeElement.node.old_columns.forEach(col=>{
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
                { prop: 'view_columns',span:24, type:'checkbox',label: '选择显示的列',dicData:columns_name},          
                { prop: 'key_column',span:24, type:'radio',label: '选择显示的列',dicData:columns_name},   
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
            if(['昨日','上次'].includes(from.split(":")[0]) && from.split(":")[1]!=to.split(":")[1]){
                return "['昨日','上次']只能合并到自身。合并到其他数据集现在不支持"
            }
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
        
        reload_line(){
            let plumbIns=this.plumbIns
            this.loadFinish=false
            this.lineList=[]
            
            let props={
                anchor: ['Left', 'Right', 'Top', 'Bottom', [0.3, 0, 0, -1], [0.7, 0, 0, -1], [0.3, 1, 0, 1], [0.7, 1, 0, 1]],
                connector: ['StateMachine'],
                endpoint: 'Blank',
                overlays: [ ['Arrow', { width: 8, length: 8, location: 1}] 
                ], // overlay
                // 添加样式
                paintStyle: { stroke: '#909399', strokeWidth: 2 }, // connector
                // endpointStyle: { fill: '#909399', outlineStroke: '#606266', outlineWidth: 1 } // endpoint
                
                }
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
                    plumbIns.makeSource("裁剪:"+ds.name)
                    if(data_from.type!='sql')
                        plumbIns.makeSource("最终:"+ds.name)
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
                    if(this.config_data.vars.filter(x=>x.ds==ds.name).length>0)
                        this.lineList.push({source: "最终:"+ds.name,target: "来自:"+ds.name,})
                
                });
                this.lineList.forEach(element => {
                    plumbIns.connect({...props,...element})
                }); 
                this.loadFinish=true  
                // 会使整个jsPlumb立即重绘。
                this.plumbIns.setSuspendDrawing(false, true);
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
                //_this.$refs.nodeForm.lineInit({
                //    from: conn.sourceId,
                //    to: conn.targetId,
                //    label: conn.getLabel()
                //})
            })
            // 连线
            _this.plumbIns.bind("connection", (evt) => {
                let from = evt.source.id
                let to = evt.target.id
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
            _this.plumbIns.bind("contextmenu", (evt) => {
                console.log('contextmenu', evt)
            })

            // 连线
            _this.plumbIns.bind("beforeDrop", (evt) => {
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
                let line=_this.lineList.find(x=>x.source==evt.sourceId && x.target==evt.targetId)
                if(line.canDelete){
                    return true
                }
                return false
            })
            _this.plumbIns.setContainer(_this.$refs.efContainer)
            
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
    }
}