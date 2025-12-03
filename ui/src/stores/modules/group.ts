import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import groupApi from '@/api/group'

export interface GroupState {
  groups: any[]
  selectedGroupId: string | null
  loading: boolean
}

const useGroupStore = defineStore({
  id: 'group',
  
  state: (): GroupState => ({
    groups: [],
    selectedGroupId: null,
    loading: false
  }),
  
  actions: {
    setGroups(groups: any[]) {
      this.groups = groups
    },
    
    setSelectedGroup(groupId: string | null) {
      this.selectedGroupId = groupId
    },
    
    setLoading(loading: boolean) {
      this.loading = loading
    },
    
    async loadGroups(loading?: Ref<boolean>) {
      try {
        this.loading = true
        const res = await groupApi.getGroups({}, loading)
        this.groups = res.data
      } catch (error) {
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    
    selectGroup(groupId: string | null) {
      this.selectedGroupId = groupId
    }
  }
})

export type GroupStore = ReturnType<typeof useGroupStore>
export default useGroupStore