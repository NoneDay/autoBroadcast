<template>
  <el-dialog :visible.sync="dialogVisible" :title="title" :close-on-click-modal="false"
  :fullscreen="fullscreen"
   append-to-body v-if="dialogVisible">
        <div slot="title" >
          <span class="el-dialog__title">{{title}}</span>
          <div style="right: 40px;    top: 20px;    position: absolute;">
            <i @click="fullscreen=!fullscreen"
              class="el-icon-full-screen"></i>
          </div>
        </div>
      <avue-form v-model="obj" :option="option"  @submit="dialog_submit"   >
          <template slot-scope="{row}" :slot="item.prop" v-for="(item,index) in formOption.column.filter(x=>x.formslot!=undefined)">
            {{row[item.prop]}}
          </template>
      </avue-form>
    <div v-if="dialogVisible && formOption.appendTxt!=undefined" v-html="formOption.appendTxt"></div>
    <div slot="footer" class="dialog-footer" v-if="dialogVisible && Array.isArray(obj)">
      <el-button type="primary" @click="dialog_submit">确 定</el-button>
    </div>

  </el-dialog>
</template>

<script>
export default {
  props: { visible: Boolean,
    title: String,
    oldFormInput: [Array,Object],
    formOption:Object
  },
  data() {
    return {
      fullscreen:false,
      dialogVisible:false,
      option:{},
      obj:[]
    }
  }, 
  watch: {
    dialogVisible(val) {
      this.$emit('update:visible', val)
    },
    oldFormInput(val){
      this.obj=this.deepClone(val)
    },
    visible(val) {
      this.obj=this.deepClone(this.oldFormInput)
      if(Array.isArray(this.oldFormInput)){
        this.option={formHeight:9,size:'mini', column:[{
                label: '明细',prop: 'obj',type: 'dynamic',span:24,maxHeight:100,size:'mini',
                children: this.formOption} ]
            }
        this.obj={obj:this.obj}
      }
      else{
        this.option=this.formOption      
      }
      this.dialogVisible=val
      this.$emit('update:visible', val)
    }
  },
  methods: {
    rowSave(form,done,loading){
      this.obj.push(form)
      done();    
      loading();
    },  
    rowUpdate(form,index,done,loading){
      done();    
      loading();
    },    
    rowDel(form,index){
        this.obj.splice(index,1)
    }, 
    dialog_submit() {
      if(Array.isArray(this.oldFormInput)){
        this.$emit('update:oldFormInput', this.obj.obj)
        this.$emit('form_input_submit', this.obj.obj)
      }else{
        this.$emit('update:oldFormInput', this.obj)
        this.$emit('form_input_submit', this.obj)
      }
      this.$emit('update:visible', false)
    },
  }

}
</script>

<style>

</style>
