export default {
    provide(){
        return  {
            context: this._context,
            fresh_ele:this._fresh_ele,
            clickedEle:this._clickedEle
        }
    },
    data: () => ({
        parentCompent:this, 
        old_content:"" 
    }),
    mounted(){
    this.old_content=this.self.content
    },
    computed: { 
        _context(){
            return this.context
        }, 
        _fresh_ele(){
            return this.fresh_ele
        }, 
        _clickedEle(){
            return this.clickedEle
        }, 
    },
    methods:{
        refresh(){
            let _this=this
            this.old_content=""
            setTimeout(()=>{
                _this.old_content=_this.self.content
                _this.buildDisplayData()
            })
        }
    },
    watch: { 
        "self.content"(){
        let _this=this
        setTimeout(function(){
            _this.old_content=_this.self.content
        })
        }
    },
}