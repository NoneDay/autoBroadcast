import request from '@/router/axios';

export function update_title(data) {
  return request({
    url: `/${data.prefix}/update_title`,      method: 'post',      data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}
export function create_one(data) {
  
  return request({
    url: `/${data.prefix}/create_one`,      method: 'post',      data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}
export function move_one(data) {  
  return request({
    url: `/${data.prefix}/move_one`,      method: 'post',      data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}

export function delete_one(data) {  
  return request({
    url: `/${data.prefix}/delete_one`,      method: 'post',      data,
    loading: {type: 'loading',options: {fullscreen: true,lock: true,text: '正在载入...',spinner: 'el-icon-loading',background: 'rgba(0, 0, 0, 0.8)'}}
  })
}
