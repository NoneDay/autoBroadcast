<template>
  <el-dialog :visible.sync="visible" title="模板输出生成" :close-on-click-modal="false"  :fullscreen="fullscreen" append-to-body>
    <vxe-grid
      ref="xGrid_template_output"
      border
      resizable
      height="230"
      :columns="tableColumn"
      :toolbar="tableToolbar"
      :data.sync="templateOutputAct"
      :edit-config="{trigger: 'click', mode: 'row', showStatus: true}"
      @toolbar-button-click="toolbarButtonClickEvent"
    />
        <div slot="title" >
          <span class="el-dialog__title">模板输出生成</span>
          <div style="right: 40px;    top: 20px;    position: absolute;">
            <i @click="fullscreen=!fullscreen"
              class="el-icon-full-screen"></i>
          </div>
        </div>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" @click="dialog_submit">确 定</el-button>
    </div>
  </el-dialog>
</template>

<script>
export default {
  props: { templateOutputAct: Array, visible: Boolean },
  data() {
    return {
      fullscreen:false,
      tableToolbar: {
        buttons: [
          { code: 'remove_selection', name: '移除数据' }
        ]
      },
      tableColumn: [
        { type: 'radio', width: 50 },
        { field: 'file', title: '文件名', width: 150 },
        { field: 'canOutput', title: '作为模板输出', width: 80,
          editRender: { name: 'select', options: [{ value: 'false', label: '否' }, { value: 'true', label: '是' }] }
        },
        { field: 'wx_file', title: '输出文件', editRender: { name: 'input' }},
        { field: 'wx_msg', title: '输出 图片/文本消息', editRender: { name: 'input' }},
        { field: 'loopForDS', title: '针对数据集循环', width: 80,
          editRender: { name: 'select', options: [{ value: 'false', label: '否' }, { value: 'true', label: '是' }] }
        },
      ]
    }
  },
  watch: {
    visible(val) {
      this.$emit('update:visible', val)
    }
  },
  methods: {
    toolbarButtonClickEvent({ button }) {
      console.info(button)
    },
    dialog_submit() {
      // this.config_data.act=this.template_output
      this.$emit('update:visible', false)
    }
  }
}
</script>

<style>

</style>
