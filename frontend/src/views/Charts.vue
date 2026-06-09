<template>
  <div class="charts-page">
    <el-card>
      <div class="toolbar">
        <div class="filters">
          <el-input v-model="searchPatient" placeholder="搜索患者姓名" clearable style="width: 200px;" />
          <el-select v-model="selectedDoctor" placeholder="选择医生" clearable style="width: 140px;">
            <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
          </el-select>
          <el-button type="primary" @click="loadCharts">查询</el-button>
        </div>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon> 新建病历
        </el-button>
      </div>

      <el-table :data="charts" style="margin-top: 16px;" @row-click="goToDetail">
        <el-table-column prop="patient_name" label="患者" width="100" />
        <el-table-column prop="doctor_name" label="医生" width="100" />
        <el-table-column prop="chief_complaint" label="主诉" show-overflow-tooltip />
        <el-table-column prop="diagnosis" label="诊断" show-overflow-tooltip />
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="最后修改" width="160">
          <template #default="{ row }">
            <span v-if="row.last_modified_by">{{ formatDate(row.last_modified_at) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="代录人" width="100">
          <template #default="{ row }">{{ row.transcriber || '-' }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新建病历" width="700px" top="5vh">
      <el-form :model="form" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="患者">
              <el-input v-model="form.patient_name" placeholder="患者姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="form.phone" placeholder="搜索患者" @blur="searchPatientByPhone" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="医生">
              <el-select v-model="form.doctor_id" style="width: 100%;" @change="onDoctorChange">
                <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="代录人">
              <el-input v-model="form.transcriber" placeholder="前台代录则填写" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="主诉">
          <el-input v-model="form.chief_complaint" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="现病史">
          <el-input v-model="form.present_illness" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="口腔检查">
          <el-input v-model="form.oral_examination" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="诊断">
          <el-input v-model="form.diagnosis" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="治疗计划">
          <el-input v-model="form.treatment_plan" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="医嘱">
          <el-input v-model="form.advice" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="牙位检查">
          <div class="tooth-section">
            <ToothChart :teeth-data="teethDisplay" @tooth-click="openToothDialog" />
            <div class="selected-info">
              <span v-if="selectedTooth">当前选中：{{ selectedTooth }}号牙</span>
              <span v-else>点击牙齿查看/编辑状态</span>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitChart">保存病历</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showToothDialog" :title="`${selectedTooth}号牙 检查记录`" width="400px">
      <el-form label-width="80px">
        <el-form-item label="状态">
          <el-checkbox-group v-model="currentToothStatuses">
            <el-checkbox v-for="s in toothStatuses" :key="s" :label="s">{{ s }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="currentToothNotes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showToothDialog = false">取消</el-button>
        <el-button type="primary" @click="saveToothRecord">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import ToothChart from '../components/ToothChart.vue'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const charts = ref([])
const doctors = ref([])
const searchPatient = ref('')
const selectedDoctor = ref('')
const showAddDialog = ref(false)
const showToothDialog = ref(false)
const selectedTooth = ref(null)
const currentToothStatuses = ref([])
const currentToothNotes = ref('')
const toothStatuses = ['龋齿', '缺失', '修复', '种植', '牙周炎', '阻生']

const form = reactive({
  patient_id: '',
  patient_name: '',
  phone: '',
  doctor_id: 'doc-001',
  doctor_name: '张医生',
  chief_complaint: '',
  present_illness: '',
  oral_examination: '',
  diagnosis: '',
  treatment_plan: '',
  advice: '',
  transcriber: '',
  teeth_records: [],
})

const teethDisplay = computed(() => {
  const map = {}
  form.teeth_records.forEach(t => {
    map[t.tooth_id] = {
      statuses: t.statuses,
      display_status: getDisplayStatus(t.statuses),
      notes: t.notes || '',
    }
  })
  return map
})

const getDisplayStatus = (statuses) => {
  if (!statuses?.length) return '健康'
  const priority = { '种植': 6, '修复': 5, '阻生': 4, '龋齿': 3, '牙周炎': 2, '缺失': 1 }
  return [...statuses].sort((a, b) => priority[b] - priority[a])[0]
}

const formatDate = (d) => d ? d.replace('T', ' ').substring(0, 16) : ''

const loadCharts = async () => {
  try {
    let url = '/charts'
    const params = []
    if (selectedDoctor.value) params.push(`doctor_id=${selectedDoctor.value}`)
    if (params.length) url += '?' + params.join('&')
    charts.value = await api.get(url)
  } catch (e) {
    console.error(e)
  }
}

const searchPatientByPhone = async () => {
  if (!form.phone) return
  try {
    const res = await api.get(`/patients/search/by-phone/${form.phone}`)
    if (res.found && res.patients.length) {
      form.patient_id = res.patients[0].id
      form.patient_name = res.patients[0].name
    }
  } catch (e) {}
}

const onDoctorChange = (val) => {
  const doc = doctors.value.find(d => d.id === val)
  if (doc) form.doctor_name = doc.name
}

const openToothDialog = (toothId) => {
  selectedTooth.value = toothId
  const record = form.teeth_records.find(t => t.tooth_id === toothId)
  currentToothStatuses.value = record ? [...record.statuses] : []
  currentToothNotes.value = record?.notes || ''
  showToothDialog.value = true
}

const saveToothRecord = () => {
  const idx = form.teeth_records.findIndex(t => t.tooth_id === selectedTooth.value)
  if (currentToothStatuses.value.length) {
    const record = { tooth_id: selectedTooth.value, statuses: [...currentToothStatuses.value], notes: currentToothNotes.value }
    if (idx >= 0) {
      form.teeth_records[idx] = record
    } else {
      form.teeth_records.push(record)
    }
  } else if (idx >= 0) {
    form.teeth_records.splice(idx, 1)
  }
  showToothDialog.value = false
}

const submitChart = async () => {
  try {
    if (!form.patient_id) {
      ElMessage.warning('请先通过手机号搜索患者')
      return
    }
    if (!form.chief_complaint.trim()) {
      ElMessage.warning('主诉不能为空')
      return
    }
    await api.post('/charts', form)
    ElMessage.success('病历保存成功')
    showAddDialog.value = false
    loadCharts()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  }
}

const goToDetail = (row) => {
  router.push(`/charts/${row.id}`)
}

onMounted(async () => {
  try {
    doctors.value = await api.get('/schedule/doctors')
    loadCharts()
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
.tooth-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.selected-info {
  font-size: 13px;
  color: #909399;
}
</style>
