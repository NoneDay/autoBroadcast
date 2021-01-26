import Config from './config'
import FormDesign from './design_index.vue'
import index_priview from './index_priview'

export default {
  install (Vue) {
    Vue.use(Config)
    Vue.use(index_priview)
    Vue.component('CellReport' + FormDesign.name, FormDesign);
  }
}
