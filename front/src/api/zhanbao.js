import request from '@/router/axios';

export function getZhanbao(data) {
  return request({
    url: `/mg/ReportDefine/get/${data}`,
    method: 'get',
    loading: {
      type: 'loading',
      options: {
        fullscreen: true,
        lock: true,
        text: '正在载入...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.8)'
      }
    }
  })
}
export function query_data(data) {
  return request({
    url: `/mg/getOneDsDataHtmlTable/`,
    method: 'post',
    data,
    loading: {
      type: 'loading',
      options: {
        fullscreen: true,
        lock: true,
        text: '正在查询...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.8)'
      }
    }
  })
}
export function files_template_exec(id, data) {
  return request({
    url: `/mg/files_template_exec/${id}`,
    method: 'post',
    data,
    loading: {
      type: 'loading',
      options: {
        fullscreen: true,
        lock: true,
        text: '正在执行...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.8)'
      }
    }
  })
}
export function save_config(id, data) {
  return request({
    url: `/mg/ReportDefine/save/${id}`,
    method: 'post',
    data,
    loading: {
      type: 'loading',
      options: {
        fullscreen: true,
        lock: true,
        text: '正在保存...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.8)'
      }
    }
  })
}

export function file_remove(id, file_name) {
  return request({
    url: `/mg/file/remove/${id}/${file_name}`,
    method: 'post',
    loading: {
      type: 'loading',
      options: {
        fullscreen: true,
        lock: true,
        text: '正在删除...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.8)'
      }
    }
  })
}
export function file_upload(id,data) {
  return request({
    url: `/mg/file/posts/${id}`,
    method: 'post',
    data:data,
    loading: {
      type: 'loading',
      options: {
        fullscreen: true,
        lock: true,
        text: '正在上载...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.8)'
      }
    }
  })
}
export function file_preview(id, file_name) {
  return request({
    url: `/mg/file/download/${id}/${file_name}?time=${new Date().getTime()}`,
    method: 'get',
    responseType: 'blob',
    loading: {
      type: 'loading',
      options: {
        fullscreen: true,
        lock: true,
        text: '正在下载...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.8)'
      }
    }
  })
}
export function file_preview_t(id, file_name) {
  return request({
    url: `/mg/file/download_t/${id}/${file_name}?time=${new Date().getTime()}`,
    method: 'get',
    responseType: 'blob',
    loading: {
      type: 'loading',
      options: {
        fullscreen: true,
        lock: true,
        text: '正在下载...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.8)'
      }
    }
  })
}