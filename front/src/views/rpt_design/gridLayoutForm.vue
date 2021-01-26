<template>
    <div  class="widget-form-container">
         <grid-layout :layout.sync="layout"
                     :col-num="colNum" 
                     :row-height="row_height"
                     :margin="[1, 1]"
                     :is-draggable="context.canDraggable"
                     :is-resizable="context.canDraggable"
                     :vertical-compact="true"
                     :use-css-transforms="true"
        >
            <grid-item v-for="item in layout"
                       :static="item.static" :key="item.i"
                       :x="item.x"
                       :y="item.y"
                       :w="item.w"
                       :h="item.h"
                       :i="item.i"
            >
              <div  style="height:100%" >
                    <widget-form-group class="widget-form-list" 
                        :self="item.element" 
                        :parent="item.element"
                         
                        :select.sync="selectWidget"
                        >
                    </widget-form-group>

                     <span v-if="!context.isPreview" class="remove" @click="removeItem(item.i)">
                       x 
                       </span>
                </div>
            </grid-item>
        </grid-layout>
    </div>
</template>

<script>
import {GridLayout, GridItem} from "vue-grid-layout"
import {widget_div_layout} from './fieldsConfig.js'
import { deepClone } from './utils/util.js';
import mixins from "./element/mixins"
export default {
    name: "gridLayoutForm",
    mixins: [history,mixins],
    components: {
        GridLayout,GridItem,
    },
    props:['layout'],
    data() {
        return { 
            draggable: true,
            resizable: true,
            row_height:30,
            colNum:12,
            newX:0,
            newY:0,
            
        }
    },
    mounted() {
        // this.$gridlayout.load();
        this.gridLayoutIndex = this.layout.length;
        let max_rows=0
        if(this.context.isPreview){
            this.layout.forEach(element => {
                if(max_rows < element.y+element.h)
                    max_rows = element.y+element.h
            });
            this.row_height= this.$parent.$el.clientHeight/max_rows
        }
    },
    methods: {
        
        addItem: function () {
            // Add a new item. It must have a unique key!
            let x=0,w=2,   h=2,y=0             
            while(true){
                let all_correct=true
                this.layout.forEach(element => {
                    if( ((x>= element.x && x< element.x +element.w ) && (y>= element.y && y< element.y +element.h ) ) ||
                        ((element.y>= y && element.y< y +h ) && (element.x>= x && element.x< x +w ) )
                    ){
                        all_correct=false
                         return false
                    }
                });
                 if(all_correct)
                        break;
                x++
                if(x+2>this.col_num)
                {
                    x=0
                    y++
                }
            }
            this.layout.push({x,y,w,h,i: this.gridLayoutIndex,element:widget_div_layout() });
            // Increment the counter to ensure key is always unique.
            this.gridLayoutIndex++;
        },
        setDelateFlagForElement(ele){
            ele.isDelete=true
            if(ele.children?.column){
                ele.children.column.forEach(one=>{
                    this.setDelateFlagForElement(one)
                });
            }
        },
        removeItem: function (val) {
            const index = this.layout.map(item => item.i).indexOf(val);
            this.setDelateFlagForElement(this.layout[index].element)
            this.layout.splice(index, 1);
        },
    }
}
</script>

<style>
.layoutJSON {
    background: #ddd;
    border: 1px solid black;
    margin-top: 10px;
    padding: 10px;
}
.columns {
    -moz-columns: 120px;
    -webkit-columns: 120px;
    columns: 120px;
}
/*************************************/
.remove {
    position: absolute;
    right: 2px;
    top: 0;
    cursor: pointer;
}
.vue-grid-layout {
    background: #eee;
}
.vue-grid-item:not(.vue-grid-placeholder) {
    background: rgb(255, 254, 254);
    border: 1px solid black;
}
.vue-grid-item .resizing {
    opacity: 0.9;
}
.vue-grid-item .static {
    background: #cce;
}
.vue-grid-item .text {
    font-size: 24px;
    text-align: center;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;
    height: 100%;
    width: 100%;
}
.vue-grid-item .no-drag {
    height: 100%;
    width: 100%;
}
.vue-grid-item .minMax {
    font-size: 12px;
}
.vue-grid-item .add {
    cursor: pointer;
}
.vue-draggable-handle {
    position: absolute;
    width: 20px;
    height: 20px;
    top: 0;
    left: 0;
    background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='5' cy='5' r='5' fill='#999999'/></svg>") no-repeat;
    background-position: bottom right;
    padding: 0 8px 8px 0;
    background-repeat: no-repeat;
    background-origin: content-box;
    box-sizing: border-box;
    cursor: pointer;
}
</style>