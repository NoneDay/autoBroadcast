<template>
  <div>
    <el-tabs type="border-card" v-model="editableTabsValue" 
    style="height:100%" 

    :editable="context.canDraggable" 
    @edit="handleTabsEdit"> 
          <el-tab-pane :key="groupIndex"  style="height:100%" 
                v-for="(item, groupIndex) in self.children.column"
                  :md="item.span || 12" 
                  :xs="24" :label="item.label" :name="item.label"
                  :offset="item.offset || 0">
              <widget-form-item :self="item" :parent="self"  :index="groupIndex"
                      :select.sync="selectWidget"
              ></widget-form-item>     
          </el-tab-pane>
    </el-tabs>
    
  </div>
</template>
<script>
import draggable from 'vuedraggable'
import {widget_div_layout} from '../fieldsConfig'
import { resultGrid2HtmlTable } from '../utils/util'
import mixins from "./mixins"
export default {
  name: 'widget-form-tabs',
  mixins:[mixins],
  components: { draggable },
  updated(){
      if(this.self.children.column.length>0){
          if(!this.self.children.column.some(element => element.label===this.editableTabsValue))
            this.editableTabsValue = this.self.children.column[0].label;
      }
      this.self.children.column.forEach(element => {
        if(element.gridName  && element.gridName!="_random_")
          this.context?.allElementSet.add(element.gridName)  
      });
  },
  computed:{
    
    
  },
  watch:{
    editableTabsValue:function(val){
      function resize(node) {
          if(node.self && node.self.type=="echart" ){
            if(node.myChart){
              node.myChart.resize();
            }
          }
          node?.$children?.forEach(ele=>{
            resize(ele)
          })
      }
      this.$nextTick(_ => {
          resize(this)
        })
    }
  },
  data () {
    return {
      editableTabsValue:"Tab0"
    }
  },
  methods: {
    handleWidgetGroupAdd (evt) {
      let newIndex = evt.newIndex;
      const item = evt.item;

      if (newIndex == 1 && newIndex > this.self.children.column.length - 1) newIndex = 0

      const data = this.deepClone(this.self.children.column[newIndex]);
      if (!data.prop) data.prop = Date.now() + '_' + Math.ceil(Math.random() * 99999)
      delete data.icon
      data.span = 24
      this.$set(this.self.children.column, newIndex, { ...data })
      this.selectWidget = this.self.children.column[newIndex]
      this.editableTabsValue=data.label
      //this.$emit("change")
    },
    handleTabsEdit(targetName, action) {
        if (action === 'add') {
          let newIndex = (this.self.children.column.length) ;
          let data={...widget_div_layout(), prop : Date.now() + '_' + Math.ceil(Math.random() * 99999) };
          let idx=newIndex
          while(this.self.children.column.find(item=>item.label=='Tab'+idx)){
            idx++
          }
          data.label='Tab'+idx
          this.$set(this.self.children.column, newIndex, { ...data })
          this.editableTabsValue = data.label;
        }
        if (action === 'remove') {
          let tabs = this.self.children.column;
          let activeName = this.editableTabsValue;
          if (activeName === targetName) {
            tabs.forEach((tab, index) => {
              if (tab.label === targetName) {
                let nextTab = tabs[index + 1] || tabs[index - 1];
                if (nextTab) {
                  activeName = nextTab.label;
                }
              }
            });
          }
          
          this.editableTabsValue = activeName;
          this.self.children.column = tabs.filter(tab => tab.label !== targetName);
        }
      }
  },
}
</script>