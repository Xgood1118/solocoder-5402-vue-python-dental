<template>
  <div class="recall-page">
    <el-card>
      <div class="toolbar">
        <div class="filters">
          <el-date-picker
            v-model="selectedMonth"
            type="month"
            placeholder="选择月份"
            value-format="YYYY-MM"
            @change="loadLogs"
          />
          <el-select v-model="smsStatus" placeholder="短信状态" clearable style="width: 140px;" @change="loadLogs">
            <el-option label="待发送" value="pending" />
            <el-option label="已发送" value="sent" />
            <el-option label="发送失败" value="send_fail" />
          </el-select>
        </div>
        <el-button type="primary" @click="generateRecall">
          <el-icon><Refresh /></el-icon> 生成召回名单
        </el-button>
      </div>

      <el-table :data="recallLogs" style="margin-top: 16px;">
        <el-table-column prop="patient_name" label="患者姓名" width="100" />
        <el-table-column prop="patient_phone" label="手机号" width="130" />
        <el-table-column prop="last_visit_date" label="上次就诊" width="110" />
        <el-table-column prop="months_since_last_visit" label="未复诊月数" width="100">
          <template #default="{ row }">{{ row.months_since_last_visit }}个月</template>
        </el-table-column>
        <el-table-column prop="reason" label="召回理由" show-overflow-tooltip />
        <el-table-column prop="recall_month" label="召回月份" width="100" />
        <el-table-column label="短信状态" width="100">
          <template #default="{ row }">
            <el-tag :type="smsStatusType(row.sms_status)" size="small">
              {{ smsStatusText(row.sms_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              link
              v-if="row.sms_status === 'send_fail' || row.sms_status === 'pending'"
              @click="resend(row)"
            >
              重发
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card style="margin-top: 16px;">
      <template #header>
        <span>召回说明</span>
      </template>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="召回条件">超过上次就诊6个月未复诊的患者</el-descriptions-item>
        <el-descriptions-item label="触发频率">每月生成一次召回名单</el-descriptions-item>
        <el-descriptions-item label="短信通知">召回名单生成后自动发短信，发送失败不影响记录写入</el-descriptions-item>
        <el-descriptions-item label="召回理由">格式：距上次就诊X个月未复诊</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import { Refresh } from '@element-plus/icons-vue'

const recallLogs = ref([])
const selectedMonth = ref('')
const smsStatus = ref('')

const smsStatusType = (s) => ({
  pending: 'warning',
  sent: 'success',
  send_fail: 'danger',
}[s] || 'info')

const smsStatusText = (s) => ({
  pending: '待发送',
  sent: '已发送',
  send_fail: '发送失败',
}[s] || s)

const loadLogs = async () => {
  try {
    let url = '/recall/logs'
    const params = []
    if (selectedMonth.value) params.push(`month=${selectedMonth.value}`)
    if (smsStatus.value) params.push(`sms_status=${smsStatus.value}`)
    if (params.length) url += '?' + params.join('&')
    recallLogs.value = await api.get(url)
  } catch (e) {
    console.error(e)
  }
}

const generateRecall = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要生成本月召回名单吗？系统会自动筛选超过6个月未复诊的患者。',
      '确认生成',
      { type: 'warning' }
    )
    const res = await api.get('/recall/generate')
    ElMessage.success(`已生成 ${res.count} 条召回记录`)
    loadLogs()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('生成失败')
    }
  }
}

const resend = async (row) => {
  try {
    await api.post(`/recall/logs/${row.id}/resend`)
    ElMessage.success('已重新发送')
    loadLogs()
  } catch (e) {
    ElMessage.error('重发失败')
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filters {
  display: flex;
  gap: 12px;
}
</style>
