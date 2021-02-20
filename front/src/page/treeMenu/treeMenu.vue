<template>
  <div class="avue-sidebar">
    <logo></logo>
    <div class="app-main-left-projects" v-if="menuId.meta && menuId.meta.edit && menuId.meta.edit==true">
      <el-button @click="handleCommand('createCatalog',null,{})"
        class="create-project-btn"  type="primary" size="mini" >新建目录</el-button>
        <el-button @click="$router.push('/sysandlogin/index/')"
        class="create-project-btn"  type="primary" size="mini" >系统设置</el-button>
      <el-scrollbar style="height:100%">
        <el-tree :data="menu" 
            :props="defaultProps" node-key="id"
            :default-expanded-keys="treeExpandData"
            draggable
            @node-drop="handleDrop"
            @node-click="handleNodeClick" 
            :allow-drop="allowDrop" 
            :allow-drag="allowDrag"
          >
        <span class="custom-tree-node" slot-scope="{ node, data }" >
            <span v-if="data.is_catalog==1" 
                :title="data.label" 
                type="text" size="mini" 
                class="el-icon-folder custom-tree-node-label" 
                style="font-weight:700;"
            >
                {{ data.label }}
            </span>
            <span type="text" :title="data.label"  size="mini" class="el-icon-bell custom-tree-node-label"  v-else>
                {{ data.label }}
            </span>
            <el-dropdown @command="handleCommand($event, node,data)" style="background-color: #20222a;color: rgba(255, 255, 255, 0.8);;position: absolute;right: 0px">
              <span class="el-dropdown-link">
                <i class="el-icon-more"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item  v-if="data.is_catalog==1" command="createCatalog">新建目录</el-dropdown-item>
                <el-dropdown-item  v-if="data.is_catalog==1" command="createForm">新建表单</el-dropdown-item>
                <el-dropdown-item command="updateTitle">编辑名称</el-dropdown-item>
                <el-dropdown-item command="delete" style="color: #F56C6C">删除</el-dropdown-item>
                <el-dropdown-item  disabled style="color: gray">id：{{data.id}}</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </span>
        </el-tree>

         </el-scrollbar>

      </div>
    <div class="app-main-left-projects"  v-else>
      <el-scrollbar style="height:100%">
        <el-tree :data="menu" :props="defaultProps" 
            node-key="id" :default-expanded-keys="treeExpandData"
            @node-click="handleNodeClick" 
          >
          <span class="custom-tree-node" slot-scope="{ node, data }" >
            <span v-if="data.is_catalog==1" type="text" size="mini" 
                class="el-icon-folder custom-tree-node-label" 
                :title="data.label"  
                style="font-weight:700;"
            >
                {{ data.label }}
            </span>
            <span type="text" size="mini" class="el-icon-bell custom-tree-node-label " :title="data.label" v-else>
                {{ data.label }}
            </span>
          </span>
        </el-tree>
        <span style="color: white;">捐赠打赏</span>
        <el-image src="img/zsm.jpg" style="width: 100%"/>
      </el-scrollbar> 
    </div>
    
    </div>
</template>
  
  <script>
  import { mapGetters } from 'vuex'
  import {  getMenu,addPath } from '@/api/user'
  import config from "../index/sidebar/config.js";
  import logo from "../index/logo";
  import {update_title,create_one,move_one,delete_one} from '@/api/zb_weihu'
  import store from '@/store'
  import { resetRouter } from '@/router/router'

    export default {
      name:"TreeMenu",
      components: {  logo },
      props: {
        screen: {
          type: Number
        },
        first: {
          type: Boolean,
          default: false
        },
        props: {
          type: Object,
          default: () => {
            return {};
          }
        },
        collapse: {
          type: Boolean
        }
      },
      computed: {
        ...mapGetters(['menu','menuId']),
        prefix(){
          return this.menuId?.meta?.prefix;
        },
        labelKey () {
          return this.props.label || this.config.propsDefault.label;
        },
        pathKey () {
          return this.props.path || this.config.propsDefault.path;
        },
        iconKey () {
          return this.props.icon || this.config.propsDefault.icon;
        },
        childrenKey () {
          return this.props.children || this.config.propsDefault.children;
        },
        nowTagValue () {
          return this.$router.$avueRouter.getValue(this.$route);
        },
        treeExpandData(){
          let arr=[]
          let t_menu=[]
          if(Array.isArray(this.menu))
            t_menu=this.menu
          else 
            t_menu.push(this.menu)
          t_menu.forEach(z=>{
            if(z.children){
              arr.push(z.id)
              z.children.forEach(x=>{
                arr.push(x.id)
              })
            }
          })
          return arr
        }
      },
      data() {
        return {  
          config: config,      
          defaultProps: {
            children: 'children',
            label: 'name'
          },
          baseFormDesc : {
            title: {
              type: "input",
              label: "名称",
              required: true
            }
          },
          formDesc:{},
          dialogTitle:"xin jian",
          formData:{},
          
          curMenuItem:{},
          curCommand:""
        };
      },
      methods: {
        handleNodeClick(item) {
          if(item.is_catalog==1 || (item.children && item.children.length>0))
              return
          //data.meta.label=data.meta.label+"22"
          //this.$router.push(item.path)
          
          if (this.screen <= 1) this.$store.commit("SET_COLLAPSE");
          this.$router.$avueRouter.group = item.group;
          this.$router.$avueRouter.meta = item.meta;
          this.$router.push({
            path: this.$router.$avueRouter.getPath({
              name: item[this.labelKey],
              src: item[this.pathKey]
            }, item.meta),
            query: item.query,
            label:item[this.labelKey],
          });
        },
        remove(node, data){
            this.$router.push("/zhanbao/"+data.path)
        },
        handleCommand(command, node,data){
          this.curCommand=command
          this.curMenuItem=data
          const old_this=this
          switch(command){
            case "createCatalog":
                this.dialogTitle='新建目录'
                this.formData={}

                this.$prompt('请输入目录名字', '新建目录', {
                    confirmButtonText: '确定',
                    inputPattern:/^[a-zA-Z\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5]*$/,
                    cancelButtonText: '取消',
                    inputValue:""
                  }).then(async({ value }) => {
                    if(node!=null && old_this.has_name(node.data.children, value))
                      return
                    let res=await create_one( {prefix:old_this.menuId?.meta?.prefix,...old_this.curMenuItem,label:value,type:'Catalog'})
                    
                    this.$store.dispatch("GetMenu", this.menuId.parentId).then(data => {
                      if (data.length !== 0) {
                        resetRouter()
                        this.$router.$avueRouter.formatRoutes(data, true);
                      }
                    })

                }).catch(error=>error)
              break
            case "createForm":
                this.dialogTitle='新建文件'
                this.formData={}
                this.$prompt('请输入名字', '新建文件', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    inputValue:"",
                    inputPattern:/^[a-zA-Z\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5]*$/
                  }).then(async({ value }) => {
                    if(old_this.has_name(node.data.children,value))
                      return
                    let res= await create_one({prefix:old_this.menuId?.meta?.prefix,...old_this.curMenuItem,label:value,type:'form'})
                    this.$store.dispatch("GetMenu", this.menuId.parentId).then(data => {                      
                      if (data.length !== 0) {
                        resetRouter()
                        this.$router.$avueRouter.formatRoutes(data, true);
                      }
                    }).catch(error=>error)
                    //node.data.children.push(res)

                  }).catch(error=>error)
              break
            case "updateTitle":
              this.dialogTitle='修改名称'
              this.$prompt('请输入新名字', '修改名称', {confirmButtonText: '确定',
                  cancelButtonText: '取消',
                  inputPattern:/^[a-zA-Z\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5]*$/,
                  inputValue:old_this.curMenuItem.label
                }
              ).then(async ({ value }) => {
                    if(old_this.has_name(node.data.children,value))
                      return
                    old_this.curMenuItem.label=value;
                    
                    await update_title({prefix:old_this.menuId?.meta?.prefix,...old_this.curMenuItem})
                  }).catch(error=>error) 
              break
            case "delete":              
              if(data.is_catalog && data.children.length>0){
                this.$alert("目录不为空，不能删除！")
                return
              }              
              this.$confirm(`此操作将永久删除该文件, 是否继续?`, `文件：${this.curMenuItem.label}`, {confirmButtonText: '确定',cancelButtonText: '取消',type: 'warning'})
                    .then(async () => {
                      await delete_one({prefix:old_this.menuId?.meta?.prefix,...data});
                      let i=0
                      node.parent.data.children.forEach((x) => {
                        if (x.id === data.id) { node.parent.data.children.splice(i, 1) }
                        i = i + 1
                      })                                           
                    }).catch(error=>error);
              return
          }            
        },
        has_name(children,label){
          if(!label){
            this.$alert("名字不能为空");
            return true;
          }
          let has_tilte=children.filter(x=>x.label==label && x.id!=this.curMenuItem.id).length        
          if(has_tilte>0){
            this.$alert("名字不能重复");
            return true;
          }
          return false
        },
  
        async handleDrop(draggingNode, dropNode, dropType, ev) {
          await move_one({prefix:old_this.menuId?.meta?.prefix,draggingID:draggingNode.data.id,dropID:dropNode.data.id,dropType})          
        },
        allowDrop(draggingNode, dropNode, type) {
  
          if(dropNode.data.is_catalog==0 && type=="inner")
              return false;
            else 
            return true
        },
        allowDrag(draggingNode) {
          return true;//draggingNode.data.label.indexOf('三级 3-2-2') === -1;
        } 
      }
    };
  </script>
  <style lang="scss" scoped>
  .app-main-left-projects {
    line-height: 1.5em;
    height: 100%;
  
    .search-comps {
      padding: 10px;
      border-bottom: 1px solid #eee;
    }
  
    .create-project-btn {
      margin: 8px 10px;
    }

    .custom-tree-node {
      display: flex;
      justify-content: space-between;
      padding-right: 20px;
      width: 100%;
      align-items: center;
      font-size: 14px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      .el-down{
        position: absolute;right: 0px;
      }
      .custom-tree-node-label {
        flex: 1;
      }
  
      .operation-btns {
        display: none;
      }
  
      &:hover {
        .operation-btns {
          display: block;
        }
      }
    }
  }
  </style>