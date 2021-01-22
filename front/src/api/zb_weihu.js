import request from '@/router/axios';

export function zb_list(data) {
  return request({
    url: `/zb/list`,method: 'get',
    loading: {type: 'loading',options:{fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}
export function update_title(data) {
  return request({
    url: `/zb/update_title`,      method: 'post',      data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}
export function create_one(data) {
  
  return request({
    url: `/zb/create_one`,      method: 'post',      data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}
export function move_one(data) {  
  return request({
    url: `/zb/move_one`,      method: 'post',      data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}

export function delete_one(data) {  
  return request({
    url: `/zb/delete_one`,      method: 'post',      data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}


export function zb_save(data) {
  return request({
    url: `/zb/save`,method: 'post',data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
} 