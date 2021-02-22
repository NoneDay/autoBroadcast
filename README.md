
## 介绍

+ 智能播报是一款能够抓取网页上的数据的软件，他能自由合并组合各类数据，管理人员可借此生成图片、文本、excel文件等多种格式的数据，然后推送到通信软件中。
+ 支持对不限数量的网页数据抓取。
+ 支持多数据集、定时备份、数据合并，自定义变量、sql查询
+ 支持excel 模板生成、ppt模板生成、文本模板生成
+ 支持对单一数据集循环模式按模板生成


## 临时安装文档
+ 1、新建一个目录，将front 和 end 解压到这个目录下
+ 2、解压redis 到一个目录，进入这个目录，运行redis-server.exe ，这是redis 缓存服务
+ 3、在sql server 服务器的数据库中建表，脚本在end/sql数据库.sql中
+ 4、修改end 目录下的两个ini 文件，里面是一些配置参数，要改成你们的。主要是验证和发送消息.需要针对你们的情况，我们再沟通

+ 5、end 是后端程序，在配置好python环境后，运行：conda activate my_flasks2 ,然后在当前目录 ，运行 python  start.py，这是启动能让前台访问界面和定时调度的flask程序。定时调度真正的运行时在cerely中，下一步就是启动celery

+ 6、在end 目录下运行:celery -A hnclic.taskMain worker --pool=solo --loglevel=info
    这是后台异步作业调度执行的程序
+ 7、front 是前台的全部程序。外面的权限架构等是基于avue.js的。现在你们不用管，只需要解压到正确的目录就行。见第一步
+ 8、没提供核心设置的ini文件，找我要

## 开发
+ 已经适配的报表：cellReport、帆软报表
+ 如果你要适配自己的报表，需要编写适配器。放到end/data_adapter目录下。里面有已经做好的例子，可供参考。
+ 适配器必须继承DataInterface，子类必须实现方法：
```
async def getData(self,url,input_params={}):  
    """ url和input_params是已经经过模板替换后的数据，可以直接在提交url中使用。必须使用异步提交，以提高并行效率。
      能执行到这一步，已经是经过了正确的模拟登陆，
     预定义post方法，内部已经实现了对于headers、cookies的合并，可以直接调用
     在这个方法中，你要实现真正的取数动作，然后缓存到当前实例中，以便在调用后续load_data_for_p的时候使用。
     同时要实现提取form的各项必要数据并放到返回数据的第二个参数中，以便合并到配置中，之后可以供前台人员修改缺省参数。
     如果你没有提供，系统将提供缺省配置，表头是返回表格的第一行。
     需要判断data_from['ds']是否有数据，没有的话，你要自己至少插入一条配置，供后续load_data_for_p调用使用。新增的配置里面一定要有一条名字叫：修改这里。
    """
def load_data_for_p(self,p):
    # 这个方法是为了针对一个url取数对应多个数据集的，根据用户配置取数
```
```
# 克隆项目

# 进入项目

# 安装依赖

# 启动服务


```
## 功能

## License

[MIT](http://opensource.org/licenses/MIT)

Copyright (c) 2021-present, Noneday