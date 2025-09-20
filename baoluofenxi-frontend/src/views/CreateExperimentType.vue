<template>
  <div class="create-experiment-type">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新建试验类型</span>
          <el-button @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="类型名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入试验类型名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入试验类型描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="时间列名称" prop="time_column">
          <el-input
            v-model="form.time_column"
            placeholder="时间列在数据文件中的列名，如：t, time, timestamp"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="数据列" prop="data_columns">
          <div class="data-columns-input">
            <el-input
              v-for="(column, index) in form.data_columns"
              :key="index"
              v-model="form.data_columns[index]"
              placeholder="请输入数据列名称"
              style="margin-bottom: 10px;"
              maxlength="50"
            >
              <template #append>
                <el-button 
                  type="danger" 
                  @click="removeColumn(index)"
                  :disabled="form.data_columns.length <= 1"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-button type="primary" plain @click="addColumn" style="width: 100%;">
              <el-icon><Plus /></el-icon>
              添加数据列
            </el-button>
          </div>
          <div class="form-tip">
            数据列是指数据文件中需要分析的列名，如：C1, C2, C3 等
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            <el-icon><Check /></el-icon>
            创建试验类型
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置表单
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { ArrowLeft, Plus, Delete, Check, Refresh } from '@element-plus/icons-vue'
import { experimentTypeApi } from '../api/experimentType'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  name: '',
  description: '',
  time_column: 't',
  data_columns: ['C1']
})

const rules = {
  name: [
    { required: true, message: '请输入试验类型名称', trigger: 'blur' }
  ],
  time_column: [
    { required: true, message: '请输入时间列名称', trigger: 'blur' }
  ],
  data_columns: [
    { 
      validator: (rule: any, value: string[], callback: (error?: Error) => void) => {
        if (!value || value.length === 0) {
          callback(new Error('请至少添加一个数据列'))
        } else if (value.some(col => !col.trim())) {
          callback(new Error('数据列名称不能为空'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ]
}

const addColumn = () => {
  form.data_columns.push(`C${form.data_columns.length + 1}`)
}

const removeColumn = (index: number) => {
  if (form.data_columns.length > 1) {
    form.data_columns.splice(index, 1)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    loading.value = true
    await experimentTypeApi.create({
      name: form.name,
      description: form.description,
      time_column: form.time_column,
      data_columns: form.data_columns.filter(col => col.trim())
    })
    
    ElMessage.success('试验类型创建成功')
    router.push('/experiment-types')
  } catch (error) {
    console.error('创建试验类型失败:', error)
    ElMessage.error('创建试验类型失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  form.data_columns = ['C1']
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-columns-input {
  width: 100%;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
