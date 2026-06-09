<template>
  <div class="tooth-chart">
    <div class="jaw upper-jaw">
      <div class="quadrant q1">
        <div class="teeth-row">
          <button
            v-for="tooth in quadrant1Teeth"
            :key="tooth"
            class="tooth-btn"
            :class="getToothClass(tooth)"
            @click="$emit('tooth-click', tooth)"
            :title="getToothTitle(tooth)"
          >
            {{ tooth }}
          </button>
        </div>
      </div>
      <div class="quadrant q2">
        <div class="teeth-row">
          <button
            v-for="tooth in quadrant2Teeth"
            :key="tooth"
            class="tooth-btn"
            :class="getToothClass(tooth)"
            @click="$emit('tooth-click', tooth)"
            :title="getToothTitle(tooth)"
          >
            {{ tooth }}
          </button>
        </div>
      </div>
    </div>
    <div class="jaw-divider"></div>
    <div class="jaw lower-jaw">
      <div class="quadrant q4">
        <div class="teeth-row">
          <button
            v-for="tooth in quadrant4Teeth"
            :key="tooth"
            class="tooth-btn"
            :class="getToothClass(tooth)"
            @click="$emit('tooth-click', tooth)"
            :title="getToothTitle(tooth)"
          >
            {{ tooth }}
          </button>
        </div>
      </div>
      <div class="quadrant q3">
        <div class="teeth-row">
          <button
            v-for="tooth in quadrant3Teeth"
            :key="tooth"
            class="tooth-btn"
            :class="getToothClass(tooth)"
            @click="$emit('tooth-click', tooth)"
            :title="getToothTitle(tooth)"
          >
            {{ tooth }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  teethData: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['tooth-click'])

const quadrant1Teeth = computed(() => {
  const arr = []
  for (let i = 1; i <= 8; i++) arr.push(`1${i}`)
  return arr
})

const quadrant2Teeth = computed(() => {
  const arr = []
  for (let i = 8; i >= 1; i--) arr.push(`2${i}`)
  return arr
})

const quadrant3Teeth = computed(() => {
  const arr = []
  for (let i = 1; i <= 8; i++) arr.push(`3${i}`)
  return arr
})

const quadrant4Teeth = computed(() => {
  const arr = []
  for (let i = 8; i >= 1; i--) arr.push(`4${i}`)
  return arr
})

const getToothClass = (toothId) => {
  const tooth = props.teethData[toothId]
  if (!tooth || !tooth.display_status || tooth.display_status === '健康') return ''
  const status = tooth.display_status
  const classMap = {
    '龋齿': 'status-caries',
    '缺失': 'status-missing',
    '修复': 'status-restored',
    '种植': 'status-implant',
    '牙周炎': 'status-periodontitis',
    '阻生': 'status-impacted',
  }
  return classMap[status] || ''
}

const getToothTitle = (toothId) => {
  const tooth = props.teethData[toothId]
  if (!tooth || !tooth.statuses?.length) return `${toothId}号牙 - 健康`
  return `${toothId}号牙 - ${tooth.statuses.join('、')}`
}
</script>

<style scoped>
.tooth-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  width: 500px;
}
.jaw {
  display: flex;
  justify-content: center;
  gap: 0;
}
.upper-jaw {
  border-radius: 50% 50% 0 0 / 80% 80% 0 0;
}
.lower-jaw {
  border-radius: 0 0 50% 50% / 0 0 80% 80%;
}
.jaw-divider {
  height: 2px;
  background: #dcdfe6;
  margin: 4px 20px;
}
.quadrant {
  display: flex;
}
.teeth-row {
  display: flex;
  gap: 3px;
}
.tooth-btn {
  width: 38px;
  height: 42px;
  border: 2px solid #dcdfe6;
  border-radius: 6px 6px 10px 10px;
  background: #fff;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: #606266;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tooth-btn:hover {
  border-color: #409EFF;
  background: #ecf5ff;
}
.status-caries {
  background: #fef0f0;
  border-color: #f56c6c;
  color: #f56c6c;
}
.status-missing {
  background: #f4f4f5;
  border-color: #909399;
  color: #909399;
  text-decoration: line-through;
}
.status-restored {
  background: #ecf5ff;
  border-color: #409EFF;
  color: #409EFF;
}
.status-implant {
  background: #f0f9eb;
  border-color: #67c23a;
  color: #67c23a;
}
.status-periodontitis {
  background: #fdf6ec;
  border-color: #e6a23c;
  color: #e6a23c;
}
.status-impacted {
  background: #fef0f0;
  border-color: #f56c6c;
  color: #f56c6c;
}
</style>
