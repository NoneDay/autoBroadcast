<template>
  <div class="widget-form-item"   
      :prop="self.prop"
      v-bind="Object.assign({style:Object.assign({},self.style,self.height?{height:self.height}:{})}, self.params)"
      :class="{active: selectWidget.prop == self.prop, 
      'required': self.required }"
      @click.stop="handleSelectWidget(index)"> 
    <span v-if="self.type == 'title'"
          :style="self.styles"
          style="margin-left: 5px;">
      {{self.value}}
    </span>
    <component v-else draggable=".item"
               :is="getComponent(self.type, self.component)"
               :self="self" :parent="parent" 
               :select.sync="selectWidget"
               v-bind="Object.assign(this.deepClone(self), self.params, {content:undefined, size:self.size || 'small' })"
               
               @change="$emit('change')">

      <span v-if="params.html"
            v-html="params.html"></span>
    </component>
    <el-button title="删除"
                @click.stop="handleWidgetDelete(index)"
                class="widget-action-delete"
                v-if="context.canDraggable && selectWidget.prop == self.prop"
                circle
                plain
                size="small"
                type="danger">
      <i class="iconfont icon-delete"></i>
    </el-button>
    <el-button title="抓我移动"
                @click.stop="handleWidgetClone(index)"
                class="widget-action-clone"
                v-if="context.canDraggable && selectWidget.prop == self.prop"
                circle
                plain
                size="small"
                type="primary">
      <i class="iconfont icon-copy"></i>
    </el-button>
  </div>
</template>
<script>
import mixins from "./mixins"
export default {
  mixins:[mixins],

  mounted(){

  },
  name: 'widget-form-item',
  data () {
    return {
        form: {}
    }
  },
  methods: {
    getComponent (type, component) {
      let KEY_COMPONENT_NAME = 'avue-';
      let result = 'input';
      if (component) return component
      else if (['array', 'img', 'url'].includes(type)) result = 'array';
      else if (type === 'select') result = 'select';
      else if (type === 'radio') result = 'radio';
      else if (type === 'checkbox') result = 'checkbox';
      else if (['time', 'timerange'].includes(type)) result = 'time';
      else if (['dates', 'date', 'datetime', 'datetimerange', 'daterange', 'week', 'month', 'year'].includes(type))
        result = 'date';
      else if (type === 'cascader') result = 'cascader';
      else if (type === 'number') result = 'input-number';
      else if (type === 'password') result = 'input';
      else if (type === 'switch') result = 'switch';
      else if (type === 'rate') result = 'rate';
      else if (type === 'upload') result = 'upload';
      else if (type === 'slider') result = 'slider';
      else if (type === 'dynamic') result = 'dynamic';
      else if (type === 'icon') result = 'input-icon';
      else if (type === 'color') result = 'input-color';
      else if (type === 'map') result = 'input-map';
      return KEY_COMPONENT_NAME + result;
    },
    getPlaceholder (item) {
      const label = item.label;
      if (['select', 'checkbox', 'radio', 'tree', 'color', 'dates', 'date', 'datetime', 'datetimerange', 'daterange', 'week', 'month', 'year', 'map', 'icon'].includes(item.type))
        return `请选择 ${label}`;
      else return `请输入 ${label}`;
    },
    handleSelectWidget (index) {
        this.selectWidget = this.parent.children.column[index]
    },
    handleWidgetDelete (index) {
      this.self.isDelete=true
      if (this.parent.children.column.length - 1 === index) {
        if (index === 0) this.selectWidget = {}
        else this.handleSelectWidget(index - 1)
      } else this.handleSelectWidget(index + 1)
      //this.parent.children.column[index]
      this.$nextTick(() => {
        this.parent.children.column.splice(index, 1)
        this.$emit("change")
      })
    },
    handleWidgetClone (index) {
      //let cloneData = this.deepClone(this.parent.children.column[index])
      //cloneData.prop = Date.now() + '_' + Math.ceil(Math.random() * 99999)
      //this.parent.children.column.splice(index, 0, cloneData)
      //this.$nextTick(() => {
      //  this.handleSelectWidget(index + 1)
      //  this.$emit("change")
      //})
    },
  },
}
</script>