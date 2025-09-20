<template>
  <div class="upload-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据上传 - {{ experimentType?.name }}</span>
          <el-button @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </template>
      
      <div v-if="experimentType" class="upload-content">
        <!-- 试验类型信息 -->
        <el-descriptions :column="3" border style="margin-bottom: 20px;">
          <el-descriptions-item label="类型名称">{{ experimentType.name }}</el-descriptions-item>
          <el-descriptions-item label="时间列">{{ experimentType.time_column }}</el-descriptions-item>
          <el-descriptions-item label="数据列">
            <el-tag v-for="column in experimentType.data_columns" :key="column" size="small" style="margin-right: 5px;">
              {{ column }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="3">{{ experimentType.description || '无描述' }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 上传表单 -->
        <el-form ref="uploadFormRef" :model="uploadForm" :rules="uploadRules" label-width="100px">
          <el-form-item label="数据名称" prop="dataName">
            <el-input
              v-model="uploadForm.dataName"
              placeholder="请输入数据名称，用于标识这组数据"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="选择文件" prop="file">
            <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :limit="1"
              accept=".csv,.xlsx,.xls"
              :file-list="fileList"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 CSV, Excel 文件格式，文件大小不超过 100MB
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
        
        <!-- 预览按钮 -->
        <div class="action-buttons" style="margin: 20px 0;">
          <el-button type="info" @click="handlePreview" :loading="previewLoading" :disabled="!selectedFile">
            <el-icon><View /></el-icon>
            预览文件
          </el-button>
          <el-button type="primary" @click="handleUpload" :loading="uploadLoading" :disabled="!canUpload">
            <el-icon><Upload /></el-icon>
            上传数据
          </el-button>
        </div>
        
        <!-- 预览结果 -->
        <el-card v-if="previewData" class="preview-card" shadow="hover">
          <template #header>
            <span>文件预览</span>
          </template>
          
          <div class="preview-info">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="文件名">{{ previewData.file_info.name }}</el-descriptions-item>
              <el-descriptions-item label="预览行数">{{ previewData.file_info.rows_preview }}</el-descriptions-item>
              <el-descriptions-item label="总列数">{{ previewData.file_info.total_columns }}</el-descriptions-item>
              <el-descriptions-item label="验证状态">
                <el-tag :type="previewData.validation.is_valid ? 'success' : 'danger'">
                  {{ previewData.validation.is_valid ? '格式正确' : '格式错误' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 验证问题 -->
            <div v-if="!previewData.validation.is_valid" class="validation-issues">
              <el-alert
                title="数据格式问题"
                type="warning"
                :closable="false"
                style="margin: 10px 0;"
              >
                <ul>
                  <li v-for="issue in previewData.validation.issues" :key="issue">{{ issue }}</li>
                </ul>
              </el-alert>
            </div>
            
            <!-- 数据预览表格 -->
            <div class="data-preview" style="margin-top: 15px;">
              <h4>数据预览（前{{ previewData.file_info.rows_preview }}行）</h4>
              <el-table :data="previewData.data_preview" border size="small" max-height="300">
                <el-table-column
                  v-for="column in previewData.file_info.columns"
                  :key="column"
                  :prop="column"
                  :label="column"
                  width="120"
                  show-overflow-tooltip
                />
              </el-table>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type UploadInstance, type UploadProps, type UploadUserFile } from 'element-plus'
import { ArrowLeft, Upload, View, UploadFilled } from '@element-plus/icons-vue'
import { experimentTypeApi } from '../api/experimentType'
import { dataApi } from '../api/data'
import type { ExperimentType, FilePreview } from '../types'

const route = useRoute()
const router = useRouter()
const uploadFormRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()

const experimentType = ref<ExperimentType>()
const selectedFile = ref<File>()
const fileList = ref<UploadUserFile[]>([])
const previewData = ref<FilePreview>()
const previewLoading = ref(false)
const uploadLoading = ref(false)

const uploadForm = reactive({
  dataName: '',
  file: null
})

const uploadRules = {
  dataName: [
    { required: true, message: '请输入数据名称', trigger: 'blur' }
  ]
}

const canUpload = computed(() => {
  return selectedFile.value && 
         uploadForm.dataName.trim() && 
         previewData.value?.validation?.is_valid
})

// 获取试验类型信息
const fetchExperimentType = async () => {
  try {
    const types = await experimentTypeApi.getAll()
    experimentType.value = types.find(t => t.id === Number(route.params.id))
    if (!experimentType.value) {
      ElMessage.error('试验类型不存在')
      router.push('/experiment-types')
    }
  } catch (error) {
    console.error('获取试验类型失败:', error)
    ElMessage.error('获取试验类型失败')
  }
}

const handleFileChange: UploadProps['onChange'] = (uploadFile) => {
  if (uploadFile.raw) {
    selectedFile.value = uploadFile.raw
    fileList.value = [uploadFile]
    // 清除之前的预览数据
    previewData.value = undefined
  }
}

const handleFileRemove: UploadProps['onRemove'] = () => {
  selectedFile.value = undefined
  fileList.value = []
  previewData.value = undefined
}

const handlePreview = async () => {
  if (!selectedFile.value || !experimentType.value) return
  
  previewLoading.value = true
  try {
    previewData.value = await dataApi.previewFile(experimentType.value.id, selectedFile.value)
    
    if (previewData.value.validation.is_valid) {
      ElMessage.success('文件格式验证通过')
    } else {
      ElMessage.warning('文件格式存在问题，请查看详情')
    }
  } catch (error) {
    console.error('预览文件失败:', error)
    ElMessage.error('预览文件失败')
  } finally {
    previewLoading.value = false
  }
}

const handleUpload = async () => {
  if (!uploadFormRef.value || !selectedFile.value || !experimentType.value) return
  
  try {
    const valid = await uploadFormRef.value.validate()
    if (!valid) return
    
    if (!previewData.value?.validation?.is_valid) {
      ElMessage.error('请先预览文件并确保格式正确')
      return
    }
    
    uploadLoading.value = true
    const result = await dataApi.uploadData(
      experimentType.value.id,
      selectedFile.value,
      uploadForm.dataName
    )
    
    if (result.success) {
      ElMessage.success('数据上传成功')
      router.push(`/data-management/${experimentType.value.id}`)
    } else {
      ElMessage.error(result.message || '上传失败')
    }
  } catch (error) {
    console.error('上传数据失败:', error)
    ElMessage.error('上传数据失败')
  } finally {
    uploadLoading.value = false
  }
}

onMounted(() => {
  fetchExperimentType()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-demo {
  width: 100%;
}

.preview-card {
  margin-top: 20px;
}

.validation-issues ul {
  margin: 0;
  padding-left: 20px;
}

.data-preview h4 {
  margin-bottom: 10px;
  color: #409eff;
}

.action-buttons {
  display: flex;
  gap: 10px;
}
</style>
