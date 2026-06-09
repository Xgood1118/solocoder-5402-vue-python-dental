<template>
  <div class="schedule-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>本周排班</span>
            </div>
          </template>
          <el-table :data="weeklySchedule" border>
            <el-table-column prop="day_cn" label="日期" width="100" />
            <el-table-column label="上午" width="200">
              <template #default="{ row }">
                <div class="shift-info">
                  <div v-for="doc in row.morning" :key="doc.doctor">
                    <el-tag size="small">{{ doc.doctor }}</el-tag>
                    <span class="room">{{ doc.room }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="下午" width="200">
              <template #default="{ row }">
                <div class="shift-info">
                  <div v-for="doc in row.afternoon" :key="doc.doctor">
                    <el-tag size="small" type="success">{{ doc.doctor }}</el-tag>
                    <span class="room">{{ doc.room }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card style="margin-top: 16px;">
          <template #header>
            <span>换班记录</span>
          </template>
          <el-table :data="swapLogs" size="small">
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="doctor_id" label="申请人" width="100">
              <template #default="{ row }">{{ getDoctorName(row.doctor_id) }}</template>
            </el-table-column>
            <el-table-column prop="swap_with_doctor" label="换班人" width="100">
              <template #default="{ row }">{{ getDoctorName(row.swap_with_doctor) }}</template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" show-overflow-tooltip />
            <el-table-column label="影响绩效" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.performance_impacted" type="danger" size="small">是</el-tag>
                <span v-else class="muted">-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>申请换班</span>
          </template>
          <el-form :model="swapForm" label-width="80px">
            <el-form-item label="日期">
              <el-date-picker v-model="swapForm.date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="申请人">
              <el-select v-model="swapForm.doctor_id" style="width: 100%;">
                <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="换班人">
              <el-select v-model="swapForm.swap_with_doctor" style="width: 100%;">
                <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="原班次">
              <el-select v-model="swapForm.original_shift" style="width: 100%;">
                <el-option label="上午班" value="morning" />
                <el-option label="下午班" value="afternoon" />
              </el-select>
            </el-form-item>
            <el-form-item label="换班原因">
              <el-input v-model="swapForm.reason" type="textarea" :rows="3" placeholder="超过2次换班需填写原因" />
            </el-form-item>
            <div class="tip" v-if="swapCount >= 2">
              <el-alert :title="`本月已换班 ${swapCount} 次，超过2次将影响绩效`" type="warning" show-icon :closable="false" />
            </div>
            <el-button type="primary" style="width: 100%; margin-top: 8px;" @click="submitSwap">提交换班</el-button>
          </el-form>
        </el-card>

        <el-card style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span>节假日配置</span>
              <el-button type="primary" size="small" @click="showHolidayDialog = true">添加</el-button>
            </div>
          </template>
          <div class="holiday-list">
            <div class="holiday-item" v-for="h in holidays" :key="h.id">
              <div class="holiday-name">{{ h.name }}</div>
              <div class="holiday-date">{{ h.start_date }} ~ {{ h.end_date }}</div>
              <el-button type="danger" text size="small" @click="deleteHoliday(h.id)">删除</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showHolidayDialog" title="添加节假日" width="400px">
      <el-form :model="holidayForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="holidayForm.name" placeholder="如：春节" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="holidayForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="holidayForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showHolidayDialog = false">取消</el-button>
        <el-button type="primary" @click="addHoliday">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const weeklySchedule = ref([])
const swapLogs = ref([])
const doctors = ref([])
const holidays = ref([])
const showHolidayDialog = ref(false)

const swapForm = ref({
  date: '',
  doctor_id: 'doc-001',
  swap_with_doctor: 'doc-002',
  original_shift: 'morning',
  reason: '',
})

const holidayForm = ref({
  name: '',
  start_date: '',
  end_date: '',
})

const dayNames = {
  monday: '周一', tuesday: '周二', wednesday: '周三',
  thursday: '周四', friday: '周五', saturday: '周六', sunday: '周日'
}

const swapCount = computed(() => {
  const now = new Date()
  const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  return swapLogs.value.filter(s => s.date.startsWith(month) && s.status !== 'cancelled').length
})

const getDoctorName = (id) => {
  const doc = doctors.value.find(d => d.id === id)
  return doc?.name || id
}

const loadSchedule = async () => {
  try {
    const data = await api.get('/schedule/weekly')
    weeklySchedule.value = data.map(s => ({
      day: s.day,
      day_cn: dayNames[s.day] || s.day,
      morning: Object.entries(s.doctor_shifts || {}).map(([id, shift]) => ({
        doctor: getDoctorName(id),
        room: shift.room,
      })),
      afternoon: Object.entries(s.afternoon_shifts || {}).map(([id, shift]) => ({
        doctor: getDoctorName(id),
        room: shift.room,
      })),
    }))
  } catch (e) {
    console.error(e)
  }
}

const loadSwapLogs = async () => {
  try {
    swapLogs.value = await api.get('/schedule/swaps')
  } catch (e) {}
}

const loadHolidays = async () => {
  try {
    holidays.value = await api.get('/schedule/holidays')
  } catch (e) {}
}

const loadDoctors = async () => {
  try {
    doctors.value = await api.get('/schedule/doctors')
  } catch (e) {}
}

const submitSwap = async () => {
  try {
    await api.post('/schedule/swap', swapForm.value)
    ElMessage.success('换班申请已提交')
    loadSwapLogs()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  }
}

const addHoliday = async () => {
  if (!holidayForm.value.name || !holidayForm.value.start_date || !holidayForm.value.end_date) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await api.post('/schedule/holidays', holidayForm.value)
    ElMessage.success('添加成功')
    showHolidayDialog.value = false
    loadHolidays()
    holidayForm.value = { name: '', start_date: '', end_date: '' }
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const deleteHoliday = async (id) => {
  try {
    await api.delete(`/schedule/holidays/${id}`)
    ElMessage.success('已删除')
    loadHolidays()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  await loadDoctors()
  loadSchedule()
  loadSwapLogs()
  loadHolidays()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.shift-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.shift-info > div {
  display: flex;
  align-items: center;
  gap: 6px;
}
.room {
  font-size: 12px;
  color: #909399;
}
.muted {
  color: #c0c4cc;
}
.holiday-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.holiday-item {
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.holiday-name {
  font-weight: 600;
  color: #303133;
}
.holiday-date {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
.tip {
  margin-top: 8px;
}
</style>
