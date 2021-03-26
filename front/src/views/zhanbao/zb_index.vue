<template>

    <landingPage :config_data="data.config_data" style="height:100%"
    :fileList="data.fileList"
    :report_name="data.report_name"
    :cron_start.sync="data.cron_start"
    :cron_str.sync="data.cron_str"
    :curr_report_id="data.curr_report_id" />  


</template>

<script>
import * as service from '@/api/zhanbao'
import { baseUrl } from '@/config/env';
import landingPage from "./workflow/plane"
const datas={}
export default {
  name: 'Zhanbao',
  components: {  landingPage},
  data() {
    return {
      
      datas: datas,
      data: this.getDefaultData()
    }
  }, 
  methods: { 
    getDefaultData() {
      return {
        curr_report_id: -1,
        fileList:[],
        report_name: '',
        config_data: {"data_from":[]},
        cron_start: 0,
        cron_str: '0 30 7,18 * * * *',
      }
    },
    async switchData(id) {
      const data = this.datas[id+'m']

        if (data===undefined) {
          const data_r = {
            ...this.getDefaultData(),
            ...await service.getZhanbao(id)
          }
          if (data_r.cron_str==undefined || data_r.cron_str.trim()=="")
            data_r.cron_str= '0 30 7,18 * * * *'
          data_r.curr_report_id = id
          data_r.config_data = JSON.parse(data_r.config_txt)
          if(undefined== data_r.config_data.template_output_act)
            data_r.config_data.template_output_act=[]
          this.datas[id+'m'] = data_r
          this.data = data_r          
        }
        else{
          this.data = data
        } 
    }
  },


  async beforeRouteEnter(to, from, next) {
    const id = to.params.id || to.meta.id
    if (id) {
      await next(async instance => await instance.switchData(id))
    } else {
      next(new Error('未指定ID'))
    }
  },
  // 在同一组件对应的多个路由间切换时触发
  async beforeRouteUpdate(to, from, next) {
    const id = to.params.id || to.meta.id
    if (id) {
      await this.switchData(id)
      next()
    } else {
      next(new Error('未指定ID'))
    }
  }
}
</script>
<style >
.contextmenu_zb{
      background-color: lightgray!important;
  }
</style>