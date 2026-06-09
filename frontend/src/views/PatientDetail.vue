<template>
  <div class="patient-detail">
    <el-page-header @back="$router.back()" :content="patient?.name || '患者详情'" />

    <el-row :gutter="20" style="margin-top: 16px;">
      <el-col :span="8">
        <el-card>
          <template #header>基本信息</template>
          <div class="info-item" v-if="patient">
            <p><span class="label">姓名：</span>{{ patient.name }}</p>
            <p><span class="label">手机号：</span>{{ patient.phone }}</p>
            <p><span class="label">性别：</span>{{ patient.gender || '-' }}</p>
            <p><span class="label">出生日期：</span>{{ patient.birth_date || '-' }}</p>
            <p><span class="label">上次就诊：</span>{{ patient.last_visit_date || '-' }}</p>
            <p><span class="label">过敏史：</span>
              <span :class="{'text-red': !patient.allergy_history}">
                {{ patient.allergy_history || '未填写' }}
              </span>
            </p>
            <p><span class="label">既往史：</span>{{ patient.past_history || '无' }}</p>
          </div>

          <el-divider />
          <div class="section-title">家庭成员
            <el-button type="primary" link @click="showAddFamily = true">添加</el-button>
          </div>
          <div class="family-list" v-if="patient?.family_members?.length">
            <div class="family-item" v-for="fm in patient.family_members" :key="fm.id">
              <span>{{ fm.name }}</span>
              <el-tag size="small">{{ fm.relation }}</el-tag>
            </div>
          </div>
          <p class="empty" v-else>暂无家庭成员</p>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="病历记录" name="charts">
              <div class="chart-list">
                <div class="chart-item" v-for="chart in charts" :key="chart.id" @click="goToChart(chart.id)">
                  <div class="chart-header">
                    <span class="chart-date">{{ chart.created_at?.split('T')[0] }}</span>
                    <el-tag size="small">{{ chart.doctor_name }}</el-tag>
                  </div>
                  <div class="chart-chief">主诉：{{ chart.chief_complaint }}</div>
                  <div class="chart-diagnosis">诊断：{{ chart.diagnosis }}</div>
                </div>
                <p class="empty" v-if="!charts.length">暂无病历记录</p>
              </div>
            </el-tab-pane>
            <el-tab-pane label="预约记录" name="appointments">
              <el-table :data="patientAppointments" size="small">
                <el-table-column prop="appointment_date" label="日期" width="120" />
                <el-table-column prop="appointment_type" label="类型" width="100" />
                <el-table-column prop="start_time" label="时间" width="80" />
                <el-table-column prop="room" label="诊室" width="90" />
                <el-table-column label="状态" width="90">
                  <template #default="{ row }">
                    <el-tag size="small" :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="收费记录" name="bills">
              <el-table :data="bills" size="small">
                <el-table-column prop="created_at" label="日期" width="160">
                  <template #default="{ row }">{{ row.created_at?.split('T')[0] }}</template>
                </el-table-column>
                <el-table-column prop="total_amount" label="总金额" width="100">
                  <template #default="{ row }">¥{{ row.total_amount }}</template>
                </el-table-column>
                <el-table-column prop="insurance_amount" label="医保" width="100">
                  <template #default="{ row }">¥{{ row.insurance_amount }}</template>
                </el-table-column>
                <el-table-column prop="self_amount" label="自费" width="100">
                  <template #default="{ row }">¥{{ row.self_amount }}</template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showAddFamily" title="添加家庭成员" width="400px">
      <el-form :model="familyForm" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="familyForm.name" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="familyForm.id_card" />
        </el-form-item>
        <el-form-item label="关系">
          <el-input v-model="familyForm.relation" placeholder="如：子女、配偶" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddFamily = false">取消</el-button>
        <el-button type="primary" @click="addFamilyMember">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const route = useRoute()
const router = useRouter()
const patientId = route.params.id

const patient = ref(null)
const charts = ref([])
const patientAppointments = ref([])
const bills = ref([])
const activeTab = ref('charts')
const showAddFamily = ref(false)
const familyForm = ref({ name: '', id_card: '', relation: '' })

const statusType = (s) => ({ scheduled: '', completed: 'success', cancelled: 'info' }[s] || '')
const statusText = (s) => ({ scheduled: '已预约', completed: '已完成', cancelled: '已取消' }[s] || s)

const loadPatient = async () => {
  try {
    patient.value = await api.get(`/patients/${patientId}`)
  } catch (e) {
    console.error(e)
  }
}

const loadCharts = async () => {
  try {
    charts.value = await api.get(`/charts?patient_id=${patientId}`)
  } catch (e) {
    console.error(e)
  }
}

const loadAppointments = async () => {
  try {
    patientAppointments.value = await api.get(`/appointments?patient_id=${patientId}`)
  } catch (e) {}
}

const loadBills = async () => {
  try {
    bills.value = await api.get(`/billing?patient_id=${patientId}`)
  } catch (e) {}
}

const goToChart = (id) => {
  router.push(`/charts/${id}`)
}

const addFamilyMember = async () => {
  try {
    await api.post(`/patients/${patientId}/family`, familyForm.value)
    ElMessage.success('添加成功')
    showAddFamily.value = false
    loadPatient()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '添加失败')
  }
}

onMounted(() => {
  loadPatient()
  loadCharts()
  loadAppointments()
  loadBills()
})
</script>

<style scoped>
.info-item p {
  margin: 8px 0;
  font-size: 14px;
}
.label {
  color: #909399;
  display: inline-block;
  width: 80px;
}
.text-red {
  color: #f56c6c;
  font-weight: 500;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.family-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.family-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
.empty {
  color: #c0c4cc;
  font-size: 14px;
  text-align: center;
  padding: 20px;
}
.chart-list {
  max-height: 400px;
  overflow-y: auto;
}
.chart-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.chart-item:hover {
  border-color: #409EFF;
  background: #f5fafe;
}
.chart-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}
.chart-date {
  font-weight: 600;
  color: #303133;
}
.chart-chief, .chart-diagnosis {
  font-size: 13px;
  color: #606266;
  margin: 2px 0;
}
</style>
