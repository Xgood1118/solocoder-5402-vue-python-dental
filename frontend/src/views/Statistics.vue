<template>
  <div class="statistics-page">
    <el-card>
      <div class="toolbar">
        <span class="title">数据统计</span>
        <el-date-picker
          v-model="selectedMonth"
          type="month"
          placeholder="选择月份"
          value-format="YYYY-MM"
          @change="loadStats"
        />
      </div>

      <el-row :gutter="20" style="margin-top: 16px;">
        <el-col :span="8">
          <el-card class="stat-card total">
            <div class="stat-label">总接诊量</div>
            <div class="stat-value">{{ clinicStats.total_visits }}</div>
            <div class="stat-sub">人次</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card revenue">
            <div class="stat-label">总营收</div>
            <div class="stat-value">¥{{ clinicStats.total_revenue }}</div>
            <div class="stat-sub">元</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card avg">
            <div class="stat-label">平均客单价</div>
            <div class="stat-value">¥{{ avgPrice }}</div>
            <div class="stat-sub">元/人</div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top: 16px;">
      <template #header>
        <span>医生业绩统计</span>
      </template>
      <el-table :data="clinicStats.doctor_stats || []" border>
        <el-table-column prop="doctor_id" label="医生" width="120">
          <template #default="{ row }">{{ getDoctorName(row.doctor_id) }}</template>
        </el-table-column>
        <el-table-column prop="total_visits" label="接诊量" width="100" sortable>
          <template #default="{ row }">{{ row.total_visits }} 人次</template>
        </el-table-column>
        <el-table-column prop="total_patients" label="接诊患者数" width="120">
          <template #default="{ row }">{{ row.total_patients }} 人</template>
        </el-table-column>
        <el-table-column prop="total_revenue" label="总营收" width="120" sortable>
          <template #default="{ row }">¥{{ row.total_revenue }}</template>
        </el-table-column>
        <el-table-column prop="avg_price" label="客单价" width="120" sortable>
          <template #default="{ row }">¥{{ row.avg_price }}</template>
        </el-table-column>
        <el-table-column prop="follow_up_rate" label="复诊率" width="120" sortable>
          <template #default="{ row }">
            <el-progress
              :percentage="(row.follow_up_rate * 100).toFixed(1)"
              :stroke-width="12"
              :show-text="true"
            />
          </template>
        </el-table-column>
        <el-table-column prop="follow_up_count" label="复诊人数" width="100">
          <template #default="{ row }">{{ row.follow_up_count }} 人</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card style="margin-top: 16px;">
      <template #header>
        <span>统计说明</span>
      </template>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="接诊量">当月完成预约的总人次</el-descriptions-item>
        <el-descriptions-item label="客单价">总营收 ÷ 接诊量</el-descriptions-item>
        <el-descriptions-item label="复诊率">
          6个月内有回访记录的患者数 ÷ 总接诊过的患者数
        </el-descriptions-item>
        <el-descriptions-item label="统计周期">自然月统计，每月1日自动更新上月数据</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const selectedMonth = ref(new Date().toISOString().substring(0, 7))
const clinicStats = ref({
  total_visits: 0,
  total_revenue: 0,
  doctor_stats: [],
})

const doctors = ref([])

const avgPrice = computed(() => {
  if (!clinicStats.value.total_visits) return '0.00'
  return (clinicStats.value.total_revenue / clinicStats.value.total_visits).toFixed(2)
})

const getDoctorName = (id) => {
  const doc = doctors.value.find(d => d.id === id)
  return doc?.name || id
}

const loadStats = async () => {
  try {
    clinicStats.value = await api.get(`/statistics/clinic/monthly?year_month=${selectedMonth.value}`)
  } catch (e) {
    console.error(e)
  }
}

const loadDoctors = async () => {
  try {
    doctors.value = await api.get('/schedule/doctors')
  } catch (e) {}
}

onMounted(() => {
  loadDoctors().then(loadStats)
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.stat-card {
  text-align: center;
  border: none;
}
.stat-card :deep(.el-card__body) {
  padding: 24px;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  line-height: 1.2;
}
.stat-sub {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}
.stat-card.total .stat-value { color: #409EFF; }
.stat-card.revenue .stat-value { color: #67c23a; }
.stat-card.avg .stat-value { color: #e6a23c; }
</style>
