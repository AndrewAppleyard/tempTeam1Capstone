import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useViewModeStore = defineStore('viewMode', () => {
  const viewMode = ref(null) 

  function setViewMode(mode) {
    viewMode.value = mode
  }

  return {
    viewMode,
    setViewMode,
  }
})
