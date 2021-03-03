import sys, os, zipfile,re, requests,shutil,json,glob
sys.path.append(os.path.realpath(os.curdir))
sys.path.append(os.path.realpath(os.curdir+"/hnclic/"))
sys.path.append(os.path.realpath(os.curdir+"/data_adapter/"))

import yaml
import lxml
import lxml.html
import pandas as pd

from hnclic.utils import htmltableToArray,guess_col_names
def parse_columns(column_json,last_result=[],prefix=""):
    for one in column_json:
        if one.get('columns'):
            parse_columns(one['columns'],last_result,prefix+one['display'])
        else:
            last_result.append({'display':prefix+one['display'],"name":one['name']})

def parse_html(html_text):
    soup= lxml.html.fromstring(html_text) 
    #分析处理的参数表
    form_inputs=[]
    for one in soup.cssselect(".param-cell-wrapper"):
        input_attrib=one.cssselect(".param-input")[0].attrib
        form_inputs.append({'label':one.cssselect(".param-cell-label span")[0].text_content(),
            'name':input_attrib['id'],'default_value':input_attrib['default'] })

    start_pos=re.search("function(\s)+reportHeaderDefault\(\)(\s)*\{(\s)*var(\s)*result(\s)*=(\s)*\{(\s)*columns(\s)*:",html_text,re.M).regs[0][1]
    end_pos=re.search(",(\s)*enabledSort(\s)*:(\s)*",html_text,re.M).regs[0][0]
    html_column_json= yaml.load(html_text[start_pos:end_pos])
    last_result=[]
    # 分析出来的表头，列与json的对应关系
    columns=parse_columns(html_column_json,last_result)

    #requests.
    #ashxUrl: '../Handler/AjaxHandler.ashx?',
    #type: 'AjaxGridReport2',
    #method: 'GetDataByParameters',


    return form_inputs,columns
    
def parse_rptExh001(rptExh001):
    """
    输入：http://10.20.49.154:9001/DMC-RPT-WEB/dev/module/reportformexhibition/reportformExhibition.html?reportId=20001194&viewFlag=0
    获取查询条件和表格样式：http://10.20.49.154:9001/DMC-RPT-WEB/front/sh/rptExh!execute?uid=rptExh001
    reportId: 20001194
viewFlag: 0
userId: 20832
versionCode: 
    """
    conditions=rptExh001['object']['conditions'] #查询条件
    items=rptExh001['object']['items']
    all_item=list([{"k":k,"alias":x["alias"],"aliasField":x['aliasField'],"valueField":x['valueField']} for k,x in items.items()])
    all_item.sort(key=lambda x:int(x["k"][4:]))

    all_item_has_not_conditions=set( [x['aliasField'] if x['valueField']=="" else x['valueField'] for x in filter(lambda x:x["k"] not in (conditions), all_item)] )
    query_feilds="prov_branch_code,prov_branch,plat_id,areflag,cxjjl_dy_fz,cxjjl_dy_fm,cxjjl_dy_result,cxjjl_yj_fz,cxjjl_yj_fm,cxjjl_yj_result,zyl_dy_fz,zyl_dy_fm,zyl_dy_result,zyl_yj_fz,zyl_yj_fm,zyl_yj_result,xjrlzb_dy_fz,xjrlzb_dy_fm,xjrlzb_dy_result,xjrlzb_yj_fz,xjrlzb_yj_fm,xjrlzb_yj_result,jdchl_dy_fz,jdchl_dy_fm,jdchl_dy_result,jdchl_yj_fz,jdchl_yj_fm,jdchl_yj_result,ryzb8f_dy_fz,ryzb8f_dy_fm,ryzb8f_dy_result,ryzb8f_yj_fz,ryzb8f_yj_fm,ryzb8f_yj_result".split(",")
    
    htmlTableHeader=[]
    htmlTableHeader.append("<table>\n")
    for row in rptExh001['object']['structInfo']['headerInfo']:
        htmlTableHeader.append("<tr>\n")
        for col in row['rpt_head_cont'].split(";"):
            htmlTableHeader.append("<td ")
            txt=""
            for idx,aaa  in enumerate(col.split("@")):
                if idx==0:
                    txt=aaa
                else:
                    htmlTableHeader.append(aaa.replace(":","='")+"' ")
            htmlTableHeader.append(">"+txt+"</td>")
        htmlTableHeader.append("</tr>\n")
    htmlTableHeader.append("</table>\n")

    table_result=htmltableToArray(lxml.html.fromstring("".join(htmlTableHeader) ))
    col_names,_=guess_col_names(table_result,"auto")

    colInfos=rptExh001['object']['structInfo']['colInfos'] # 列信息
    cols=list([x['data_column_name'] for x in colInfos ]) # 获取列名

    #提交查询条件，获取结果到rptExh002
    """
    http://10.20.49.154:9001/DMC-RPT-WEB/front/sh/rptExh!execute?uid=rptExh002
reportId: 20001194
orderField: 
orderDir: 
querywhere: {"key_1":"202102","key_4":"","key_6":""}
rptThirdType: 
queryField: prov_branch_code,prov_branch,plat_id,areflag,cxjjl_dy_fz,cxjjl_dy_fm,cxjjl_dy_result,cxjjl_yj_fz,cxjjl_yj_fm,cxjjl_yj_result,zyl_dy_fz,zyl_dy_fm,zyl_dy_result,zyl_yj_fz,zyl_yj_fm,zyl_yj_result,xjrlzb_dy_fz,xjrlzb_dy_fm,xjrlzb_dy_result,xjrlzb_yj_fz,xjrlzb_yj_fm,xjrlzb_yj_result,jdchl_dy_fz,jdchl_dy_fm,jdchl_dy_result,jdchl_yj_fz,jdchl_yj_fm,jdchl_yj_result,ryzb8f_dy_fz,ryzb8f_dy_fm,ryzb8f_dy_result,ryzb8f_yj_fz,ryzb8f_yj_fm,ryzb8f_yj_result
queryDistinct: 
queryType: btsx
refreshFlag: 0
versionCode: 1.10
orderBy: 
userId: 20832
querywhere2: 
querywhere3: 
pageNum: 1
pageSize: 40
haveMetaData: 0
upRptId: null
upRptVersion: null
    """
    ttt=pd.DataFrame(rptExh002)[cols] # 按表格列的顺序重排
    ttt=ttt.applymap(lambda x: (x[:-1]) if x.endswith("%") else x) # 所有列都去掉百分号
    ttt.columns=col_names # 按表格里面的中文名称重新命名pandas 数据
    # 很遗憾，找不到什么可以作为主键
    # show_cols=list([x['data_column_name'] for x in colInfos if x['checked_flag']=='1'])

    pass
    
if __name__ == '__main__':
    with open("C:\\其他省的\\总部rptExh002.json", 'r',encoding="utf8") as f:
        json_text = f.read()
    rptExh002=json.loads(json_text )['object']['rows']
    
    with open("C:\\其他省的\\总部rptExh001.json", 'r',encoding="utf8") as f:
        json_text = f.read()
    parse_rptExh001(json.loads(json_text ))


    #with open("C:\\其他省的\\安徽.html", 'r',encoding="utf8") as f:
    #    html_text = f.read()
    #parse_html(html_text)