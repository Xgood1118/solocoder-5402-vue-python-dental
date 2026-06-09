<template>
  <div class="billing-page">
    <el-card>
      <div class="toolbar">
        <div class="filters">
          <el-input v-model="searchPatient" placeholder="搜索患者" clearable style="width: 180px;" />
          <el-button type="primary" @click="loadBills">查询</el-button>
        </div>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon> 新建收费
        </el-button>
      </div>

      <el-table :data="bills" style="margin-top: 16px;">
        <el-table-column prop="patient_name" label="患者" width="100" />
        <el-table-column label="日期" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="总金额" width="100">
          <template #default="{ row }">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column label="医保" width="100">
          <template #default="{ row }">¥{{ row.insurance_amount }}</template>
        </el-table-column>
        <el-table-column label="自费" width="100">
          <template #default="{ row }">¥{{ row.self_amount }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="success">已支付</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="printReceipt(row, 'insurance')">医保联</el-button>
            <el-button size="small" @click="printReceipt(row, 'self')">自费联</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新建收费单" width="650px" top="5vh">
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
        <el-form-item label="医生">
          <el-select v-model="form.doctor_id" style="width: 100%;">
            <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="收费项目">
          <div class="items-section">
            <div class="item-row" v-for="(item, idx) in form.items" :key="idx">
              <el-select v-model="item.item_code" placeholder="选择项目" style="width: 180px;" @change="(v) => onItemChange(idx, v)">
                <el-option
                  v-for="cat in catalog"
                  :key="cat.code"
                  :label="`${cat.name} - ¥${cat.price}`"
                  :value="cat.code"
                />
              </el-select>
              <el-input-number v-model="item.quantity" :min="1" :max="10" size="small" @change="calcTotal" />
              <span class="item-price">¥{{ item.unit_price || 0 }}</span>
              <span class="item-ratio">自付{{ (item.self_ratio * 100).toFixed(0) }}%</span>
              <el-button type="danger" text @click="removeItem(idx)">删除</el-button>
            </div>
            <el-button type="primary" plain size="small" @click="addItem">+ 添加项目</el-button>
          </div>
        </el-form-item>

        <el-form-item label="支付方式">
          <el-radio-group v-model="form.payment_method">
            <el-radio value="现金">现金</el-radio>
            <el-radio value="医保">医保</el-radio>
            <el-radio value="微信">微信</el-radio>
            <el-radio value="支付宝">支付宝</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <div class="amount-summary">
        <div class="amount-row">
          <span>总金额：</span>
          <span class="amount total">¥{{ totals.total_amount }}</span>
        </div>
        <div class="amount-row">
          <span>医保报销：</span>
          <span class="amount insurance">¥{{ totals.insurance_amount }}</span>
        </div>
        <div class="amount-row">
          <span>自费金额：</span>
          <span class="amount self">¥{{ totals.self_amount }}</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBill">确认收费</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { Plus } from '@element-plus/icons-vue'

const bills = ref([])
const doctors = ref([])
const catalog = ref([])
const searchPatient = ref('')
const showAddDialog = ref(false)

const form = reactive({
  patient_id: '',
  patient_name: '',
  phone: '',
  doctor_id: 'doc-001',
  items: [],
  payment_method: '现金',
})

const totals = computed(() => {
  let total = 0, insurance = 0, self = 0
  form.items.forEach(item => {
    const itemTotal = (item.unit_price || 0) * (item.quantity || 0)
    const itemSelf = itemTotal * (item.self_ratio || 0)
    total += itemTotal
    insurance += (itemTotal - itemSelf)
    self += itemSelf
  })
  return {
    total_amount: total.toFixed(2),
    insurance_amount: insurance.toFixed(2),
    self_amount: self.toFixed(2),
  }
})

const formatDate = (d) => d ? d.replace('T', ' ').substring(0, 16) : ''

const loadBills = async () => {
  try {
    bills.value = await api.get('/billing')
  } catch (e) {
    console.error(e)
  }
}

const loadCatalog = async () => {
  try {
    catalog.value = await api.get('/billing/insurance-catalog')
  } catch (e) {}
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

const addItem = () => {
  form.items.push({
    item_code: '',
    item_name: '',
    quantity: 1,
    unit_price: 0,
    self_ratio: 0.3,
    category: '',
  })
}

const onItemChange = (idx, code) => {
  const item = catalog.value.find(c => c.code === code)
  if (item) {
    form.items[idx].item_name = item.name
    form.items[idx].unit_price = item.price
    form.items[idx].self_ratio = item.self_ratio
    form.items[idx].category = item.category
  }
}

const removeItem = (idx) => {
  form.items.splice(idx, 1)
}

const calcTotal = () => {}

const submitBill = async () => {
  if (!form.patient_id) {
    ElMessage.warning('请先搜索患者')
    return
  }
  if (!form.items.length) {
    ElMessage.warning('请添加收费项目')
    return
  }
  try {
    await api.post('/billing', form)
    ElMessage.success('收费成功')
    showAddDialog.value = false
    loadBills()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const printReceipt = (row, type) => {
  window.open(`/receipt/${type}/${row.id}`, '_blank', 'width=320,height=600')
}

onMounted(async () => {
  loadBills()
  loadCatalog()
  doctors.value = await api.get('/schedule/doctors')
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
.items-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.item-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.item-price {
  color: #f56c6c;
  font-weight: 500;
  min-width: 80px;
}
.item-ratio {
  font-size: 12px;
  color: #909399;
  min-width: 70px;
}
.amount-summary {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin: 16px 0;
}
.amount-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin: 6px 0;
  font-size: 14px;
}
.amount {
  font-weight: 600;
  min-width: 100px;
  text-align: right;
}
.amount.total { color: #303133; font-size: 16px; }
.amount.insurance { color: #67c23a; }
.amount.self { color: #f56c6c; }
</style>
