import sys, os, zipfile,re, requests,shutil,json,glob
import yaml
import lxml
import lxml.html

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

if __name__ == '__main__':
    with open("C:\\其他省的\\安徽.html", 'r',encoding="utf8") as f:
        html_text = f.read()
    parse_html(html_text)