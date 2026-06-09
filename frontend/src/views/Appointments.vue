<template>
  <div class="appointments-page">
    <el-card>
      <div class="toolbar">
        <div class="filters">
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            @change="loadAppointments"
          />
          <el-select v-model="selectedDoctor" placeholder="选择医生" clearable @change="loadAppointments" style="width: 140px;">
            <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
          </el-select>
          <el-select v-model="selectedStatus" placeholder="选择状态" clearable @change="loadAppointments" style="width: 120px;">
            <el-option label="已预约" value="scheduled" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon> 新增预约
        </el-button>
      </div>

      <el-table :data="appointments" style="margin-top: 16px;">
        <el-table-column prop="patient_name" label="患者姓名" width="100" />
        <el-table-column prop="appointment_type" label="项目类型" width="100" />
        <el-table-column prop="appointment_date" label="日期" width="110" />
        <el-table-column prop="start_time" label="开始时间" width="90" />
        <el-table-column label="时长" width="80">
          <template #default="{ row }">{{ row.duration_minutes }}分钟</template>
        </el-table-column>
        <el-table-column prop="room" label="诊室" width="90" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="markComplete(row)" v-if="row.status === 'scheduled'">完成</el-button>
            <el-button size="small" type="danger" @click="cancelAppt(row)" v-if="row.status === 'scheduled'">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新增预约" width="500px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="患者">
          <el-input v-model="form.patient_name" placeholder="输入患者姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="搜索患者" @blur="searchPatient" />
        </el-form-item>
        <el-form-item label="医生">
          <el-select v-model="form.doctor_id" style="width: 100%;">
            <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目类型">
          <el-select v-model="form.appointment_type" style="width: 100%;" @change="onTypeChange">
            <el-option v-for="t in appointmentTypes" :key="t.type" :label="t.type" :value="t.type" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.appointment_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="时间">
          <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="诊室">
          <el-select v-model="form.room" style="width: 100%;">
            <el-option v-for="r in rooms" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAppointment">确认预约</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { Plus } from '@element-plus/icons-vue'

const appointments = ref([])
const doctors = ref([])
const appointmentTypes = ref([])
const rooms = ref([])
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedDoctor = ref('')
const selectedStatus = ref('')
const showAddDialog = ref(false)

const form = ref({
  patient_id: '',
  patient_name: '',
  phone: '',
  doctor_id: 'doc-001',
  appointment_type: '初诊',
  appointment_date: new Date().toISOString().split('T')[0],
  start_time: '09:00',
  room: '1号诊室',
  notes: '',
})

const statusType = (s) => ({ scheduled: '', completed: 'success', cancelled: 'info' }[s] || '')
const statusText = (s) => ({ scheduled: '已预约', completed: '已完成', cancelled: '已取消' }[s] || s)

const loadAppointments = async () => {
  try {
    let url = '/appointments'
    const params = []
    if (selectedDate.value) params.push(`date=${selectedDate.value}`)
    if (selectedDoctor.value) params.push(`doctor_id=${selectedDoctor.value}`)
    if (selectedStatus.value) params.push(`status=${selectedStatus.value}`)
    if (params.length) url += '?' + params.join('&')
    appointments.value = await api.get(url)
  } catch (e) {
    ElMessage.error('加载预约失败')
  }
}

const searchPatient = async () => {
  if (!form.value.phone) return
  try {
    const res = await api.get(`/patients/search/by-phone/${form.value.phone}`)
    if (res.found && res.patients.length) {
      form.value.patient_id = res.patients[0].id
      form.value.patient_name = res.patients[0].name
    }
  } catch (e) {}
}

const onTypeChange = () => {}

const submitAppointment = async () => {
  try {
    if (!form.value.patient_id) {
      ElMessage.warning('请先通过手机号搜索患者')
      return
    }
    await api.post('/appointments', form.value)
    ElMessage.success('预约成功')
    showAddDialog.value = false
    loadAppointments()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '预约失败，可能时间冲突')
  }
}

const markComplete = async (row) => {
  try {
    await api.put(`/appointments/${row.id}/status?status=completed`)
    ElMessage.success('已标记完成')
    loadAppointments()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const cancelAppt = async (row) => {
  try {
    await api.delete(`/appointments/${row.id}`)
    ElMessage.success('已取消预约')
    loadAppointments()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(async () => {
  try {
    doctors.value = await api.get('/schedule/doctors')
    appointmentTypes.value = await api.get('/appointments/types/list')
    rooms.value = await api.get('/appointments/rooms/list')
    loadAppointments()
  } catch (e) {
    console.error(e)
  }
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
