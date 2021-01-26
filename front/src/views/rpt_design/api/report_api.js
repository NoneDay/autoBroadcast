import x2js from 'x2js' 
const x2jsone=new x2js(); //实例
import {request} from 'axios'
import {luckySheet2ReportGrid,loadFile,deepClone,build_layout,get_signalR_connection,getObjType} from '../utils/util.js'
export function open_one(_this,reportFilePath) {
    return request({
        method: 'post',
        //url: '/report5/default?reportName=2019/2jidu/kb_dangri2.cr',
        url: '/report5/design/open?reportName='+ reportFilePath,
        headers:{"needType": "json","worker_no":"14100298","Authorization":"Bearer d2762dbd"},
        withCredentials: true
  })
}

export function save_one(reportFilePath) {
    return request({
        method: 'post',
        //url: '/report5/default?reportName=2019/2jidu/kb_dangri2.cr',
        url: '/report5/design/open?reportName='+ reportFilePath,
        headers:{"needType": "json","worker_no":"14100298","Authorization":"Bearer d2762dbd"},
        withCredentials: true
    })
}

export function preview_one(_this) {
    _this.context.report.params?.param.forEach(ele=>{
        if(ele.tagValue && ele.tagValue.length==0)
        delete ele.tagValue
    })
    _this.context.report.dataSets?.dataSet.forEach(ele=>{
        _this.$set(_this.ds_log,ele._name,{color:'info',content:[]})
    })
    let signalR_connection=get_signalR_connection(function(message) {
        //_this.$nextTick(function(){
        let ds_name=message.split("\n")[0].split("=>")[0].split(":")[0]
        if(_this.ds_log[ds_name]){
            if(message.indexOf("取数结束")>0){
            console.info(message)
            _this.ds_log[ds_name].color="success"  
            }
            else
            if(message.indexOf("开始")>0){
            _this.ds_log[ds_name].color="danger"  
            }
            _this.ds_log[ds_name].content.push(message)
        }
        //})
        _this.exec_log=_this.exec_log+message+"\n"
        _this.$refs.textarea.scrollTop=_this.$refs.textarea.scrollHeight
        //_this.$message.error(message);
    })
    signalR_connection.invoke('GetConnectionId').then(function(connectionId){
        let data=new FormData();
        console.info(_this.context.report)
        data.append("content", x2jsone.js2xml({report:_this.context.report}) )
        data.append("connectionId", connectionId)
        request({
        method: 'post',
        //url: '/report5/default?reportName=2019/2jidu/kb_dangri2.cr',
        url: '/report5/design/preview',
        headers:{"needType": "json","worker_no":"14100298","Authorization":"Bearer d2762dbd"},
        data
        ,withCredentials: true
        }).then(response_data => {
            _this.executed =true
            if(response_data.errcode && response_data.errcode ==1){
            _this.$notify({title: '提示',message: response_data.message,duration: 0});
            return;
            }

            Object.assign(_this.result,response_data)
            console.info( _this.result)
            _this.queryForm=response_data.form
            Object.assign(_this.context.report_result,_this.result)
            _this.context.report.dataSets.dataSet.forEach(element => {
                let define_ds= _this.context.report_result.dataSet[element._name]               
                if(define_ds)
                {
                element._fields=JSON.stringify(define_ds[0][0])
                }
            });
            if(_this.context.report_result.layout)
            {
            _this.layout=_this.context.report_result.layout
            }
            else
            {
            _this.layout=build_layout(
                { HtmlText:Object.values(_this.result.data).filter(ele=>ele.type=="htmlText"),
                grid:Object.values(_this.result.data).filter(ele=>ele.type=="common")
                } )
            }
        }).catch(error=> { 
        _this.$notify({title: '提示',message: error.response_data,type: 'error',duration:0});
        })
    }).catch(error=> { 
        _this.$notify({title: '提示',message: error,type: 'error',duration:0});
    })
}

export function run_one(_this,reportFilePath) {
    let data=new FormData();
    console.info(_this.context.report)
    data.append("reportFilePath", reportFilePath)
    request({
      method: 'post',
      url: '/report5/design/run_one',
      headers:{"needType": "json","worker_no":"14100298","Authorization":"Bearer d2762dbd"},
      data
      ,withCredentials: true
    }).then(response_data => {
        _this.executed =true
        if(response_data.errcode && response_data.errcode ==1){
        _this.$notify({title: '提示',message: response_data.message,duration: 0});
        return;
        }
        Object.assign(_this.result,response_data)
        console.info( _this.result)
        _this.queryForm=response_data.form
        Object.assign(_this.context.report_result,_this.result)
        if(_this.context.report_result.layout)
        {
        _this.layout=_this.context.report_result.layout
        }
        else
        {
        _this.layout=build_layout(
            { HtmlText:Object.values(_this.result.data).filter(ele=>ele.type=="htmlText"),
            grid:Object.values(_this.result.data).filter(ele=>ele.type=="common")
            } )
        }
    }).catch(error=> { 
        _this.$notify({title: '提示',message: error.response_data,type: 'error',duration:0});
    })
    
}

export function rptList(loc_path) {

    return request({
        method: 'get',
        url: '/report5/design/list'+( loc_path==""?"":`?loc_path=${loc_path}` ),
        headers:{"needType": "json","worker_no":"14100298","Authorization":"Bearer d2762dbd"},
        withCredentials: true
    })
}