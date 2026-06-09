<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon appointment">
              <el-icon :size="32"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_appointments }}</div>
              <div class="stat-label">今日预约</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon patient">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_patients }}</div>
              <div class="stat-label">患者总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon revenue">
              <el-icon :size="32"><Wallet /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ stats.this_month_revenue }}</div>
              <div class="stat-label">本月营收</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon chart">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_charts }}</div>
              <div class="stat-label">病历总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>今日预约</span>
          </template>
          <el-table :data="todayAppointments" size="small">
            <el-table-column prop="patient_name" label="患者" width="100" />
            <el-table-column prop="appointment_type" label="类型" width="100" />
            <el-table-column prop="start_time" label="时间" width="80" />
            <el-table-column prop="room" label="诊室" width="80" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">
                  {{ statusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/appointments')">
              <el-icon><Calendar /></el-icon> 新增预约
            </el-button>
            <el-button type="success" @click="$router.push('/patients')">
              <el-icon><User /></el-icon> 患者建档
            </el-button>
            <el-button type="warning" @click="$router.push('/billing')">
              <el-icon><Wallet /></el-icon> 收费结算
            </el-button>
            <el-button type="info" @click="$router.push('/charts')">
              <el-icon><Edit /></el-icon> 写病历
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { Calendar, User, Wallet, Document, Plus, Edit } from '@element-plus/icons-vue'

const stats = ref({
  today_appointments: 0,
  total_patients: 0,
  this_month_revenue: 0,
  total_charts: 0,
})

const todayAppointments = ref([])

const statusType = (status) => {
  const map = { scheduled: '', completed: 'success', cancelled: 'info' }
  return map[status] || ''
}

const statusText = (status) => {
  const map = { scheduled: '已预约', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

onMounted(async () => {
  try {
    stats.value = await api.get('/statistics/overview')
    const today = new Date().toISOString().split('T')[0]
    todayAppointments.value = await api.get(`/appointments?date=${today}`)
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.stat-card {
  border-radius: 8px;
}
.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.stat-icon.appointment { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-icon.patient { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-icon.revenue { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-icon.chart { background: linear-gradient(135deg, #43e97b, #38f9d7); }
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.quick-actions .el-button {
  width: 140px;
  height: 48px;
}
</style>
