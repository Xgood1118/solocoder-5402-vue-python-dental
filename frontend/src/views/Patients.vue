<template>
  <div class="patients-page">
    <el-card>
      <div class="toolbar">
        <div class="search-bar">
          <el-input v-model="searchKeyword" placeholder="搜索患者姓名或手机号" clearable style="width: 280px;" @keyup.enter="loadPatients">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button type="primary" @click="loadPatients">搜索</el-button>
        </div>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon> 新建档案
        </el-button>
      </div>

      <el-table :data="patients" style="margin-top: 16px;" @row-click="goToDetail">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="birth_date" label="出生日期" width="120" />
        <el-table-column label="家庭成员" width="100">
          <template #default="{ row }">
            <el-tag size="small" v-if="row.family_members?.length">{{ row.family_members.length }}人</el-tag>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_visit_date" label="上次就诊" width="120" />
        <el-table-column prop="allergy_history" label="过敏史" show-overflow-tooltip />
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新建患者档案" width="500px">
      <el-form :model="form" label-width="90px" :rules="rules" ref="formRef">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="form.id_card" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="form.birth_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="过敏史" prop="allergy_history">
          <el-input v-model="form.allergy_history" type="textarea" :rows="2" placeholder="请填写过敏史，无则填无" />
          <div class="tip">过敏史必填，否则无法创建病历</div>
        </el-form-item>
        <el-form-item label="既往史">
          <el-input v-model="form.past_history" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPatient">确认建档</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import { Plus, Search } from '@element-plus/icons-vue'

const router = useRouter()
const patients = ref([])
const searchKeyword = ref('')
const showAddDialog = ref(false)
const formRef = ref(null)

const form = ref({
  name: '',
  phone: '',
  id_card: '',
  gender: '男',
  birth_date: '',
  allergy_history: '',
  past_history: '',
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  id_card: [{ required: true, message: '请输入身份证号', trigger: 'blur' }],
  allergy_history: [{ required: true, message: '请填写过敏史', trigger: 'blur' }],
}

const loadPatients = async () => {
  try {
    let url = '/patients'
    if (searchKeyword.value) {
      if (/^\d+$/.test(searchKeyword.value)) {
        const res = await api.get(`/patients/search/by-phone/${searchKeyword.value}`)
        patients.value = res.patients || []
        return
      }
      url += `?name=${searchKeyword.value}`
    }
    patients.value = await api.get(url)
  } catch (e) {
    console.error(e)
  }
}

const goToDetail = (row) => {
  router.push(`/patients/${row.id}`)
}

const submitPatient = async () => {
  try {
    await formRef.value.validate()
    await api.post('/patients', form.value)
    ElMessage.success('建档成功')
    showAddDialog.value = false
    loadPatients()
  } catch (e) {
    if (e.response) {
      ElMessage.error(e.response.data.detail)
    }
  }
}

onMounted(() => {
  loadPatients()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-bar {
  display: flex;
  gap: 8px;
}
.tip {
  font-size: 12px;
  color: #f56c6c;
  margin-top: 4px;
}
.muted {
  color: #c0c4cc;
}
</style>
