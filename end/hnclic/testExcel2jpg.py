from win32com.client import Dispatch, DispatchEx
import pythoncom
from PIL import ImageGrab, Image
import sys, os
import uuid,json

_work = """
[
  {
    "uuid": 1602637351746,
    "title": "",
    "elements": [
      {
        "name": "lbp-background",
        "uuid": 1602637351746,
        "pluginProps": {
          "uuid": 1602637351746,
          "imgSrc": "https://cdn.pixabay.com/photo/2017/12/30/13/25/portrait-3050076_150.jpg",
          "backgroundColor": "rgba(255, 255, 255, 0.2)",
          "waterMarkText": "水印文字",
          "waterMarkFontSize": 16,
          "waterMarkRotate": 10,
          "waterMarkColor": "rgba(184, 184, 184, 0.2)"
        },
        "commonStyle": {
          "color": "#000000",
          "width": 100,
          "left": 100,
          "height": 40,
          "fontSize": 14,
          "top": 100,
          "backgroundColor": "rgba(255, 255, 255, 0)",
          "zindex": 1,
          "textAlign": "center"
        },
        "events": [],
        "animations": []
      },
      {
        "name": "lbp-picture",
        "uuid": 1602637370696,
        "pluginProps": {
          "uuid": 1602637370696,
          "imgSrc": "",
          "fillType": "contain"
        },
        "commonStyle": {
          "color": "#000000",
          "width": 100,
          "left": -470.92706298828125,
          "height": 40,
          "fontSize": 14,
          "top": 288.0026092529297,
          "backgroundColor": "rgba(255, 255, 255, 0)",
          "zindex": 2,
          "textAlign": "center"
        },
        "events": [],
        "animations": []
      },
      {
        "name": "lbp-line-chart",
        "uuid": 1602650124041,
        "pluginProps": {
          "uuid": 1602650124041,
          "dataset": [
            [
              "日期",
              "销售量"
            ],
            [
              "1月1日",
              123
            ],
            [
              "1月2日",
              1223
            ],
            [
              "1月3日",
              2123
            ],
            [
              "1月4日",
              4123
            ],
            [
              "1月5日",
              3123
            ],
            [
              "1月6日",
              7123
            ]
          ],
          "type": "histogram",
          "colors": [
            "#19d4ae",
            "#5ab1ef",
            "#fa6e86",
            "#ffb980",
            "#0067a6",
            "#c4b4e4",
            "#d87a80",
            "#9cbbff",
            "#d9d0c7",
            "#87a997",
            "#d49ea2",
            "#5b4947",
            "#7ba3a8"
          ]
        },
        "commonStyle": {
          "color": "#000000",
          "width": 320,
          "left": 5,
          "height": 400,
          "fontSize": 14,
          "top": 2.0026092529296875,
          "backgroundColor": "rgba(255, 255, 255, 0)",
          "zindex": 3,
          "textAlign": "center"
        },
        "events": [],
        "animations": []
      },
      {
        "name": "lbp-table",
        "uuid": 1602650188280,
        "pluginProps": {
          "uuid": 1602650188280,
          "theme": "lbp-table-theme-stripe",
          "columnWidth": 100,
          "freezeCount": 0,
          "dataset": [
            [
              "列A",
              "列B",
              "列C"
            ],
            [
              "————",
              "————",
              "————"
            ],
            [
              "————",
              "————",
              "————"
            ],
            [
              "————",
              "————",
              "————"
            ]
          ]
        },
        "commonStyle": {
          "color": "#000000",
          "width": 320,
          "left": 5,
          "height": 150,
          "fontSize": 14,
          "top": 363,
          "backgroundColor": "rgba(255, 255, 255, 0)",
          "zindex": 4,
          "textAlign": "center"
        },
        "events": [],
        "animations": []
      },
      {
        "name": "lbp-text",
        "uuid": 1602637432803,
        "pluginProps": {
          "uuid": 1602637432803,
          "backgroundColor": "rgba(0, 0, 0, 0)",
          "borderWidth": 0,
          "borderRadius": 10,
          "borderColor": "#000000",
          "text": "<p>{{'sdasda' \\"sdasd\\"}}</p>",
          "editorMode": "preview"
        },
        "commonStyle": {
          "color": "#000000",
          "width": 198,
          "left": 59,
          "height": 45,
          "fontSize": 14,
          "top": 520,
          "backgroundColor": "rgba(255, 255, 255, 0)",
          "zindex": 5,
          "textAlign": "center"
        },
        "events": [],
        "animations": []
      },
      {
        "name": "lbp-text",
        "uuid": 1602655409071,
        "pluginProps": {
          "uuid": 1602655409071,
          "backgroundColor": "rgba(0, 0, 0, 0)",
          "borderWidth": 0,
          "borderRadius": 10,
          "borderColor": "#000000",
          "text": "<p>双击修改<strong>文字</strong></p>",
          "editorMode": "preview"
        },
        "commonStyle": {
          "color": "#000000",
          "width": 100,
          "left": 65,
          "height": 40,
          "fontSize": 14,
          "top": 41.00260925292969,
          "backgroundColor": "rgba(255, 255, 255, 0)",
          "zindex": 6,
          "textAlign": "center"
        },
        "events": [],
        "animations": []
      }
    ]
  }
]
"""
aa="sdasd\"aad"
w_json=json.loads(_work)
print(w_json)