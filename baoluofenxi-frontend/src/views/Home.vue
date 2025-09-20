<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>包络分析系统</span>
            </div>
          </template>
          
          <div class="welcome-content">
            <div class="system-info">
              <h2>系统功能</h2>
              <ul>
                <li>试验类型管理</li>
                <li>数据文件上传与预览</li>
                <li>包络数据分析与可视化</li>
                <li>历史数据管理</li>
              </ul>
            </div>
            
            <el-divider />
            
            <div class="quick-actions">
              <h3>快速操作</h3>
              <el-space wrap>
                <el-button type="primary" @click="$router.push('/experiment-types')">
                  <el-icon><Setting /></el-icon>
                  管理试验类型
                </el-button>
                <el-button type="success" @click="goToUpload" :disabled="!hasExperimentTypes">
                  <el-icon><Upload /></el-icon>
                  上传数据
                </el-button>
                <el-button type="info" @click="goToAnalysis" :disabled="!hasExperimentTypes">
                  <el-icon><TrendCharts /></el-icon>
                  包络分析
                </el-button>
              </el-space>
            </div>
            
            <el-divider />
            
            <div class="experiment-types-summary" v-if="experimentTypes.length > 0">
              <h3>现有试验类型</h3>
              <el-row :gutter="20">
                <el-col :span="8" v-for="type in experimentTypes" :key="type.id">
                  <el-card class="type-card" shadow="hover">
                    <h4>{{ type.name }}</h4>
                    <p>{{ type.description || '无描述' }}</p>
                    <div class="type-actions">
                      <el-button 
                        size="small" 
                        type="primary" 
                        @click="$router.push(`/upload/${type.id}`)"
                      >
                        上传数据
                      </el-button>
                      <el-button 
                        size="small" 
                        type="warning"
                        @click="$router.push(`/data-management/${type.id}`)"
                      >
                        数据管理
                      </el-button>
                      <el-button 
                        size="small" 
                        type="success"
                        @click="$router.push(`/envelope/${type.id}`)"
                      >
                        分析
                      </el-button>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Setting, Upload, TrendCharts } from '@element-plus/icons-vue'
import { experimentTypeApi } from '../api/experimentType'
import type { ExperimentType } from '../types'

const router = useRouter()
const experimentTypes = ref<ExperimentType[]>([])

const hasExperimentTypes = computed(() => experimentTypes.value.length > 0)

const fetchExperimentTypes = async () => {
  try {
    experimentTypes.value = await experimentTypeApi.getAll()
  } catch (error) {
    console.error('获取试验类型失败:', error)
    ElMessage.error('获取试验类型失败')
  }
}

const goToUpload = () => {
  if (experimentTypes.value.length > 0) {
    // 如果只有一个试验类型，直接跳转
    if (experimentTypes.value.length === 1) {
      router.push(`/upload/${experimentTypes.value[0].id}`)
    } else {
      // 多个类型时跳转到类型列表
      router.push('/experiment-types')
    }
  }
}

const goToAnalysis = () => {
  if (experimentTypes.value.length > 0) {
    if (experimentTypes.value.length === 1) {
      router.push(`/envelope/${experimentTypes.value[0].id}`)
    } else {
      router.push('/experiment-types')
    }
  }
}

onMounted(() => {
  fetchExperimentTypes()
})
</script>

<style scoped>
.welcome-content {
  text-align: left;
}

.system-info ul {
  list-style-type: disc;
  margin-left: 20px;
}

.quick-actions {
  margin: 20px 0;
}

.type-card {
  margin-bottom: 20px;
}

.type-card h4 {
  margin: 0 0 10px 0;
  color: #409eff;
}

.type-card p {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 14px;
}

.type-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
