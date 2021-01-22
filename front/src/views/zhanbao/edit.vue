<template>
<div>
   <vxe-grid
          border
          resizable
          export-config
          import-config
          keep-source
          height="530"
          
          :proxy-config="tableProxy"
          :columns="tableColumn"
          :toolbar="tableToolbar"
          :edit-config="{trigger: 'click', mode: 'row', showStatus: true}"
          @toolbar-button-click="toolbarButtonClickEvent"></vxe-grid>
</div>
</template>

<script>
import * as service from '@/api/zb_weihu'
import { mapGetters } from 'vuex'
export default {
    name: 'zhanbao_manager',
    computed: {
        ...mapGetters(['menuId']),
    },
    data() {
        return {
            tablePage: {
                pageSize: 25
              },
            tableColumn: [
                { type: 'checkbox', width: 50 },
                {field: 'id',title: 'id',width: 250},
                {field: 'report_name',title: '名称',width: 250,editRender: {name: 'input'}}
            ],
            tableProxy: {
                props: {
                    result: 'result',
                    total: 'page.total'
                },
                ajax: {
                    // page 对象： { pageSize, currentPage }
                    query: ({
                        page
                    }) => service.zb_list(),
                    // body 对象： { removeRecords }
                    delete: ({
                        body
                    }) => service.zb_save(body),
                    // body 对象： { insertRecords, updateRecords, removeRecords, pendingRecords }
                    save: ({
                        body
                    }) => service.zb_save(body)
                }
            },
            tableToolbar: {
                id: 'toolbar_demo_1',
                buttons: [{
                        code: 'insert_actived',
                        name: '新增'
                    },
                    {
                        code: 'mark_cancel',
                        name: 'app.body.button.markCancel',
                        dropdowns: [{
                                code: 'delete',
                                name: 'app.body.button.deleteSelectedRecords',
                                type: 'text'
                            },
                            {
                                code: 'remove',
                                name: '移除数据',
                                type: 'text'
                            }
                        ]
                    },
                    {
                        code: 'save',
                        name: 'app.body.button.save',
                        status: 'success'
                    },
                ],
                refresh: true,
                import: true,
                export: true,
                zoom: true,
                resizable: {
                    storage: true
                },
                custom: {
                    storage: true
                }
            }
        }
    },
    methods: {
    toolbarButtonClickEvent ({ code }, event) {
        switch (code) {
        case 'myBtn':
            this.$XModal.alert(code)
            break
        }
    }
    }
}
</script>

<style>

</style>
