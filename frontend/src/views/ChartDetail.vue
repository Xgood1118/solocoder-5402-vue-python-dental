<template>
  <div class="chart-detail">
    <el-page-header @back="$router.back()" content="病历详情" />

    <el-row :gutter="20" style="margin-top: 16px;" v-if="chart">
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>病历信息</span>
              <el-tag size="small" type="info">{{ chart.doctor_name }}</el-tag>
            </div>
          </template>
          <div class="detail-section">
            <div class="detail-row">
              <span class="label">患者：</span>
              <span>{{ chart.patient_name }}</span>
            </div>
            <div class="detail-row">
              <span class="label">创建时间：</span>
              <span>{{ formatDate(chart.created_at) }}</span>
            </div>
            <div class="detail-row" v-if="chart.transcriber">
              <span class="label">代录人：</span>
              <span>{{ chart.transcriber }}</span>
            </div>
            <div class="detail-row" v-if="chart.last_modified_by">
              <span class="label">最后修改：</span>
              <span>{{ chart.last_modified_by }} {{ formatDate(chart.last_modified_at) }}</span>
            </div>
          </div>

          <el-divider />

          <div class="section">
            <div class="section-title">主诉</div>
            <p class="section-content">{{ chart.chief_complaint }}</p>
          </div>
          <div class="section">
            <div class="section-title">现病史</div>
            <p class="section-content">{{ chart.present_illness }}</p>
          </div>
          <div class="section">
            <div class="section-title">口腔检查</div>
            <p class="section-content">{{ chart.oral_examination }}</p>
          </div>
          <div class="section">
            <div class="section-title">诊断</div>
            <p class="section-content">{{ chart.diagnosis }}</p>
          </div>
          <div class="section">
            <div class="section-title">治疗计划</div>
            <p class="section-content">{{ chart.treatment_plan }}</p>
          </div>
          <div class="section">
            <div class="section-title">医嘱</div>
            <p class="section-content">{{ chart.advice }}</p>
          </div>
        </el-card>

        <el-card style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span>牙位图</span>
              <span class="tip">点击查看详情</span>
            </div>
          </template>
          <div class="tooth-wrapper">
            <ToothChart :teeth-data="chart.teeth_display || {}" />
          </div>
          <div class="legend">
            <span class="legend-item"><i class="dot caries"></i>龋齿</span>
            <span class="legend-item"><i class="dot restored"></i>修复</span>
            <span class="legend-item"><i class="dot implant"></i>种植</span>
            <span class="legend-item"><i class="dot missing"></i>缺失</span>
            <span class="legend-item"><i class="dot periodontitis"></i>牙周炎</span>
            <span class="legend-item"><i class="dot impacted"></i>阻生</span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>X 光影像</span>
              <el-button type="primary" size="small" @click="showUpload = true">上传</el-button>
            </div>
          </template>
          <div class="image-list">
            <div class="image-item" v-for="img in images" :key="img.id" @click="viewImage(img)">
              <div class="image-thumb" v-if="!img.file_type?.includes('dcm')">
                <img :src="`/api/images/${img.id}/file`" alt="" />
              </div>
              <div class="image-thumb dcm-thumb" v-else>
                <el-icon :size="40" color="#909399"><Document /></el-icon>
                <span>DCM文件</span>
              </div>
              <div class="image-info">
                <div class="image-name">{{ img.description || img.original_filename }}</div>
                <div class="image-meta">{{ img.image_type }} · {{ formatSize(img.file_size) }}</div>
              </div>
            </div>
            <p class="empty" v-if="!images.length">暂无影像</p>
          </div>
        </el-card>

        <el-card style="margin-top: 16px;">
          <template #header>
            <span>相关收费</span>
          </template>
          <el-table :data="relatedBills" size="small">
            <el-table-column prop="created_at" label="日期" width="110">
              <template #default="{ row }">{{ row.created_at?.split('T')[0] }}</template>
            </el-table-column>
            <el-table-column prop="total_amount" label="金额">
              <template #default="{ row }">¥{{ row.total_amount }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showUpload" title="上传X光片" width="480px">
      <el-upload
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".png,.jpg,.jpeg,.dcm"
      >
        <el-button type="primary">选择文件</el-button>
        <template #tip>
          <div class="el-upload__tip">支持 png/jpg/jpeg/dcm 格式，单张不超过10MB</div>
        </template>
      </el-upload>
      <el-form label-width="80px" style="margin-top: 16px;">
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" placeholder="如：右上6号牙根尖片" />
        </el-form-item>
        <el-form-item label="关联牙位">
          <el-input v-model="uploadForm.tooth_id" placeholder="如：16" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="uploadForm.image_type" style="width: 100%;">
            <el-option label="小牙片" value="xray" />
            <el-option label="全景片" value="panoramic" />
            <el-option label="CBCT" value="cbct" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" @click="submitUpload">上传</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showImageViewer" title="影像查看" width="800px" top="5vh">
      <div class="image-viewer" v-if="currentImage">
        <canvas ref="canvasRef" v-if="!isDcm" @mousedown="startDraw" @mousemove="draw" @mouseup="endDraw"></canvas>
        <div v-else class="dcm-viewer">
          <el-empty description="DCM格式需专业查看器" />
          <el-button type="primary" @click="downloadDcm">下载DCM文件</el-button>
        </div>
        <div class="viewer-tools">
          <el-button-group>
            <el-button size="small" :type="drawMode === 'arrow' ? 'primary' : ''" @click="drawMode = 'arrow'">箭头</el-button>
            <el-button size="small" :type="drawMode === 'text' ? 'primary' : ''" @click="drawMode = 'text'">文字</el-button>
          </el-button-group>
          <el-button size="small" @click="clearAnnotations">清除标注</el-button>
          <el-button size="small" type="success" @click="saveAnnotations">保存标注</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import ToothChart from '../components/ToothChart.vue'
import { Document } from '@element-plus/icons-vue'

const route = useRoute()
const chartId = route.params.id

const chart = ref(null)
const images = ref([])
const relatedBills = ref([])
const showUpload = ref(false)
const showImageViewer = ref(false)
const currentImage = ref(null)
const canvasRef = ref(null)
const drawMode = ref('arrow')
const isDrawing = ref(false)
const annotations = ref([])
const startPoint = ref({ x: 0, y: 0 })

const uploadForm = ref({
  file: null,
  description: '',
  tooth_id: '',
  image_type: 'xray',
})

const isDcm = computed(() => currentImage.value?.file_type === '.dcm')

const formatDate = (d) => d ? d.replace('T', ' ').substring(0, 16) : ''
const formatSize = (s) => s < 1024 ? s + 'B' : (s / 1024).toFixed(1) + 'KB'

const loadChart = async () => {
  try {
    chart.value = await api.get(`/charts/${chartId}?doctor_id=doc-001`)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加载失败')
  }
}

const loadImages = async () => {
  try {
    images.value = await api.get(`/images?chart_id=${chartId}`)
  } catch (e) {}
}

const loadBills = async () => {
  try {
    relatedBills.value = await api.get(`/billing?patient_id=${chart.value?.patient_id}`)
  } catch (e) {}
}

const handleFileChange = (file) => {
  uploadForm.value.file = file.raw
}

const submitUpload = async () => {
  if (!uploadForm.value.file) {
    ElMessage.warning('请选择文件')
    return
  }
  const formData = new FormData()
  formData.append('file', uploadForm.value.file)
  formData.append('patient_id', chart.value.patient_id)
  formData.append('chart_id', chartId)
  formData.append('description', uploadForm.value.description)
  formData.append('tooth_id', uploadForm.value.tooth_id)
  formData.append('image_type', uploadForm.value.image_type)

  try {
    await api.post('/images/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('上传成功')
    showUpload.value = false
    loadImages()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  }
}

const viewImage = async (img) => {
  currentImage.value = img
  annotations.value = img.annotations || []
  showImageViewer.value = true
  if (!img.file_type?.includes('dcm')) {
    await nextTick()
    drawCanvas()
  }
}

const drawCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const img = new Image()
  img.onload = () => {
    canvas.width = 600
    canvas.height = 400
    ctx.drawImage(img, 0, 0, 600, 400)
    drawAllAnnotations(ctx)
  }
  img.src = `/api/images/${currentImage.value.id}/file`
}

const drawAllAnnotations = (ctx) => {
  annotations.value.forEach(a => {
    if (a.type === 'arrow') {
      ctx.strokeStyle = a.color || '#ff0000'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(a.x, a.y)
      ctx.lineTo(a.x2 || a.x + 50, a.y2 || a.y)
      ctx.stroke()
    }
  })
}

const startDraw = (e) => {
  if (drawMode.value === 'arrow') {
    isDrawing.value = true
    const rect = canvasRef.value.getBoundingClientRect()
    startPoint.value = { x: e.clientX - rect.left, y: e.clientY - rect.top }
  }
}

const draw = (e) => {
  if (!isDrawing.value) return
  const ctx = canvasRef.value.getContext('2d')
  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  ctx.clearRect(0, 0, 600, 400)
  const img = new Image()
  img.onload = () => {
    ctx.drawImage(img, 0, 0, 600, 400)
    drawAllAnnotations(ctx)
    ctx.strokeStyle = '#ff0000'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(startPoint.value.x, startPoint.value.y)
    ctx.lineTo(x, y)
    ctx.stroke()
  }
  img.src = `/api/images/${currentImage.value.id}/file`
}

const endDraw = (e) => {
  if (!isDrawing.value) return
  isDrawing.value = false
  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  annotations.value.push({
    id: Date.now().toString(),
    type: 'arrow',
    x: startPoint.value.x,
    y: startPoint.value.y,
    x2: x,
    y2: y,
    color: '#ff0000',
  })
}

const clearAnnotations = () => {
  annotations.value = []
  drawCanvas()
}

const saveAnnotations = async () => {
  try {
    await api.post(`/images/${currentImage.value.id}/annotations`, annotations.value)
    ElMessage.success('标注已保存')
    loadImages()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const downloadDcm = () => {
  window.open(`/api/images/${currentImage.value.id}/file`)
}

onMounted(() => {
  loadChart().then(() => {
    loadImages()
    loadBills()
  })
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tip {
  font-size: 12px;
  color: #909399;
}
.section {
  margin-bottom: 16px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}
.section-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
.detail-section {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.detail-row {
  font-size: 14px;
}
.label {
  color: #909399;
}
.tooth-wrapper {
  display: flex;
  justify-content: center;
}
.legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;
  font-size: 12px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
}
.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot.caries { background: #f56c6c; }
.dot.restored { background: #409EFF; }
.dot.implant { background: #67c23a; }
.dot.missing { background: #909399; }
.dot.periodontitis { background: #e6a23c; }
.dot.impacted { background: #f56c6c; }

.image-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}
.image-item {
  display: flex;
  gap: 10px;
  padding: 8px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  cursor: pointer;
}
.image-item:hover {
  border-color: #409EFF;
  background: #f5fafe;
}
.image-thumb {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.dcm-thumb {
  flex-direction: column;
  font-size: 10px;
  color: #909399;
  gap: 4px;
}
.image-info {
  flex: 1;
}
.image-name {
  font-size: 13px;
  color: #303133;
  margin-bottom: 2px;
}
.image-meta {
  font-size: 12px;
  color: #909399;
}
.empty {
  text-align: center;
  color: #c0c4cc;
  padding: 20px;
}
.image-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
canvas {
  border: 1px solid #dcdfe6;
  cursor: crosshair;
}
.viewer-tools {
  display: flex;
  gap: 10px;
}
.dcm-viewer {
  padding: 40px;
  text-align: center;
}
</style>
