import * as service from '@/api/zhanbao'
export default {
    data() {
      return {
        fileList:[],
      }
    },
    computed:{
        curr_report_id(){
            return this.config_data.curr_report_id
        }
    },
    methods:{
        // ----------------------------------------
        file_submitUpload(content) {
            
            if (this.curr_report_id === 0) {
            this.$message.error('必须先保存新建文件后才能保存上传文件')
            return
            }
            this.$refs.upload.submit()
        },
        async myUpload(content){
            
            let form = new FormData();
            form.append("file", content.file);
            let ret=await service.file_upload(this.curr_report_id,form)
            
            if(ret.errcode==0)
            this.$message.success(ret.message)
            else
            this.$message.error(ret.message)
        },
        async file_handleRemove(file) {
            let ret=await service.file_remove(this.curr_report_id,file.name)
            let idx=this.fileList.indexOf(file)
            if(idx>=0)
            this.fileList.splice(idx,1);
            
            let tmp=this.config_data.template_output_act
            let one=tmp.find(x=>x.file==file.name)
            if(one && tmp.indexOf(one)>=0)
            tmp.splice(tmp.indexOf(one),1);

            if(ret.errcode==0)
            this.$message.success(ret.message)
            else
            this.$message.error(ret.message)
        },
        file_success(response, file, fileList) {
            let tmp=this.config_data.template_output_act
            let one=tmp.find(x=>x.file==file.name)
            if(!one)
            tmp.push({file:file.name,'canOutput':"false",'wx_file':'','wx_msg':''})
        },
        file_error(error, file, fileList) {
            console.log(file, fileList)
            this.$message.error(error)
        },
        file_change(file, fileList) {
            console.log(file, fileList)
        },
        download(fileName, res) { // 处理返回的文件流
            const blob = res
            if ('download' in document.createElement('a')) { // 非IE下载
                const elink = document.createElement('a')
                elink.download = fileName
                elink.style.display = 'none'
                elink.href = URL.createObjectURL(res)
                document.body.appendChild(elink)
                elink.click()
                URL.revokeObjectURL(elink.href) // 释放URL 对象
                document.body.removeChild(elink)
            } else { // IE10+下载
                navigator.msSaveBlob(blob, fileName)
            }
        },
        async file_handlePreview(file) {
            const res=await service.file_preview(this.curr_report_id,file.name)
            this.download(file.name, res)
        },
        async file_handlePreview_t(file) {
            const res=await service.file_preview_t(this.curr_report_id,file.name)
            this.download(file.name, res)
        }, 
    }
}