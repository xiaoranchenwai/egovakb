import SearchDatasetVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class SearchKnowledgeBaseNode extends AppNode {
  constructor(props: any) {
    super(props, SearchDatasetVue)
  }
}
export default {
  type: 'search-knowledge-base-node',
  model: AppNodeModel,
  view: SearchKnowledgeBaseNode
}
