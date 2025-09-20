<template>
  <div class="experiment-types">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>试验类型管理</span>
          <el-button type="primary" @click="$router.push('/experiment-types/create')">
            <el-icon><Plus /></el-icon>
            新建试验类型
          </el-button>
        </div>
      </template>
      
      <el-table :data="experimentTypes" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="类型名称" width="200" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="time_column" label="时间列" width="120" />
        <el-table-column prop="data_columns" label="数据列" width="200">
          <template #default="{ row }">
            <el-tag v-for="column in row.data_columns" :key="column" size="small" style="margin-right: 5px;">
              {{ column }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="$router.push(`/upload/${row.id}`)">
              <el-icon><Upload /></el-icon>
              上传数据
            </el-button>
            <el-button size="small" type="success" @click="$router.push(`/envelope/${row.id}`)">
              <el-icon><TrendCharts /></el-icon>
              分析
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!loading && experimentTypes.length === 0" class="empty-state">
        <el-empty description="暂无试验类型">
          <el-button type="primary" @click="$router.push('/experiment-types/create')">
            创建第一个试验类型
          </el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, TrendCharts, Delete } from '@element-plus/icons-vue'
import { experimentTypeApi } from '../api/experimentType'
import type { ExperimentType } from '../types'

const experimentTypes = ref<ExperimentType[]>([])
const loading = ref(false)

const fetchExperimentTypes = async () => {
  loading.value = true
  try {
    experimentTypes.value = await experimentTypeApi.getAll()
  } catch (error) {
    console.error('获取试验类型失败:', error)
    ElMessage.error('获取试验类型失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (type: ExperimentType) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除试验类型 "${type.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await experimentTypeApi.delete(type.id)
    ElMessage.success('删除成功')
    await fetchExperimentTypes()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchExperimentTypes()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  text-align: center;
  margin: 40px 0;
}
</style>
