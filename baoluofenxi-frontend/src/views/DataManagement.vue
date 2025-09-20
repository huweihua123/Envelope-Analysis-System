<template>
  <div class="data-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon class="title-icon"><DataBoard /></el-icon>
            数据管理
          </h1>
          <p class="page-subtitle">{{ experimentType?.name }}</p>
        </div>
        <div class="action-section">
          <el-button type="primary" size="large" @click="$router.push(`/upload/${$route.params.id}`)">
            <el-icon><Upload /></el-icon>
            上传数据
          </el-button>
          <el-button size="large" @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </div>

    <div class="content-container">
      <div v-if="experimentType" class="data-content">
        <!-- 试验类型信息卡片 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><InfoFilled /></el-icon>
              <span class="header-title">试验配置信息</span>
            </div>
          </template>
          <el-descriptions :column="3" border size="large">
            <el-descriptions-item>
              <template #label>
                <div class="label-with-icon">
                  <el-icon><Setting /></el-icon>
                  类型名称
                </div>
              </template>
              <el-tag type="primary" size="large">{{ experimentType.name }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item>
              <template #label>
                <div class="label-with-icon">
                  <el-icon><Timer /></el-icon>
                  时间列
                </div>
              </template>
              <el-tag type="info" size="large">{{ experimentType.time_column }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item>
              <template #label>
                <div class="label-with-icon">
                  <el-icon><DataLine /></el-icon>
                  数据列
                </div>
              </template>
              <div class="tags-container">
                <el-tag 
                  v-for="(column, index) in experimentType.data_columns" 
                  :key="column" 
                  :type="['success', 'warning', 'danger', 'info'][index % 4]"
                  size="large"
                  class="data-column-tag"
                >
                  {{ column }}
                </el-tag>
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <!-- 数据统计卡片 -->
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><TrendCharts /></el-icon>
              <span class="header-title">数据统计</span>
            </div>
          </template>
          <el-row :gutter="24">
            <el-col :span="6">
              <div class="stat-item">
                <el-statistic 
                  title="总数据集" 
                  :value="statistics?.total_count || 0"
                  :precision="0"
                >
                  <template #prefix>
                    <el-icon class="stat-icon total"><DataBoard /></el-icon>
                  </template>
                </el-statistic>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <el-statistic 
                  title="历史数据集" 
                  :value="statistics?.historical_count || 0"
                  :precision="0"
                >
                  <template #prefix>
                    <el-icon class="stat-icon historical"><FolderOpened /></el-icon>
                  </template>
                </el-statistic>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <el-statistic 
                  title="活跃数据集" 
                  :value="statistics?.active_count || 0"
                  :precision="0"
                >
                  <template #prefix>
                    <el-icon class="stat-icon active"><CircleCheck /></el-icon>
                  </template>
                </el-statistic>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <el-statistic 
                  title="总数据行数" 
                  :value="statistics?.total_rows || 0"
                  :precision="0"
                >
                  <template #prefix>
                    <el-icon class="stat-icon rows"><DataAnalysis /></el-icon>
                  </template>
                </el-statistic>
              </div>
            </el-col>
          </el-row>
        </el-card>
        
        <!-- 数据列表卡片 -->
        <el-card class="table-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><List /></el-icon>
              <span class="header-title">数据列表</span>
              <div class="header-actions">
                <el-input
                  v-model="searchText"
                  placeholder="搜索数据..."
                  style="width: 200px"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="filteredData" 
            v-loading="loading" 
            class="modern-table"
            :row-class-name="tableRowClassName"
          >
            <el-table-column prop="data_name" label="数据名称" min-width="200">
              <template #default="{ row }">
                <div class="data-name-cell">
                  <el-icon class="cell-icon"><Document /></el-icon>
                  <span class="cell-text">{{ row.data_name }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="file_name" label="文件名" min-width="280">
              <template #default="{ row }">
                <div class="file-name-cell">
                  <el-icon class="cell-icon"><Files /></el-icon>
                  <el-tooltip :content="row.file_name" placement="top">
                    <span class="cell-text file-name-text">{{ row.file_name }}</span>
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="row_count" label="数据行数" width="140" align="center">
              <template #default="{ row }">
                <div class="count-cell">
                  <el-tag type="info" size="small">
                    {{ row.row_count?.toLocaleString() || 0 }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="upload_time" label="上传时间" width="180" align="center">
              <template #default="{ row }">
                <div class="time-cell">
                  <el-icon class="cell-icon"><Timer /></el-icon>
                  <span class="cell-text">{{ row.upload_time_formatted || formatDate(row.upload_time) }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="is_historical" label="历史数据" width="120" align="center">
              <template #default="{ row }">
                <div class="switch-cell">
                  <el-switch
                    v-model="row.is_historical"
                    @change="handleHistoricalToggle(row)"
                    :disabled="updating.has(row.id)"
                    active-color="#67c23a"
                    inactive-color="#dcdfe6"
                  />
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag 
                  :type="row.status === 'active' ? 'success' : 'info'"
                  effect="dark"
                  round
                >
                  <el-icon>
                    <CircleCheck v-if="row.status === 'active'" />
                    <Warning v-else />
                  </el-icon>
                  {{ row.status === 'active' ? '活跃' : '已删除' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="240" align="center" fixed="right">
              <template #default="{ row }">
                <div class="action-buttons">
                  <el-button size="small" type="primary" plain @click="handleViewData(row)">
                    <el-icon><View /></el-icon>
                    查看
                  </el-button>
                  <el-button 
                    size="small" 
                    type="success" 
                    plain
                    @click="$router.push(`/envelope/${$route.params.id}`)"
                  >
                    <el-icon><TrendCharts /></el-icon>
                    分析
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    plain
                    @click="handleDelete(row)"
                    :disabled="row.status !== 'active'"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-if="!loading && experimentData.length === 0" class="empty-state">
            <el-empty description="暂无数据" :image-size="120">
              <template #image>
                <div class="empty-image">
                  <el-icon><DataBoard /></el-icon>
                </div>
              </template>
              <template #description>
                <p class="empty-description">还没有上传任何数据</p>
                <p class="empty-hint">点击下面的按钮开始上传您的第一组数据</p>
              </template>
              <el-button type="primary" size="large" @click="$router.push(`/upload/${$route.params.id}`)">
                <el-icon><Upload /></el-icon>
                上传数据
              </el-button>
            </el-empty>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 数据查看对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="`数据详情 - ${selectedData?.data_name}`"
      width="80%"
      top="5vh"
    >
      <div v-if="selectedData">
        <el-descriptions :column="2" border size="small" style="margin-bottom: 20px;">
          <el-descriptions-item label="数据名称">{{ selectedData.data_name }}</el-descriptions-item>
          <el-descriptions-item label="文件名">{{ selectedData.file_name }}</el-descriptions-item>
          <el-descriptions-item label="数据行数">{{ selectedData.row_count?.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="上传时间">
            {{ selectedData.upload_time_formatted || formatDate(selectedData.upload_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="历史数据">
            <el-tag :type="selectedData.is_historical ? 'success' : 'info'">
              {{ selectedData.is_historical ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedData.status === 'active' ? 'success' : 'warning'">
              {{ selectedData.status === 'active' ? '活跃' : '已删除' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="ClickHouse表名" :span="2">
            <el-tag type="primary" v-if="selectedData.clickhouse_table_name">
              {{ selectedData.clickhouse_table_name }}
            </el-tag>
            <span v-else>未分配</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- ClickHouse表信息 -->
        <div v-if="selectedData.clickhouse_info && !selectedData.clickhouse_info.error" style="margin-bottom: 20px;">
          <h4>ClickHouse表信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="表名">{{ selectedData.clickhouse_info.table_name }}</el-descriptions-item>
            <el-descriptions-item label="实际行数">{{ selectedData.clickhouse_info.row_count?.toLocaleString() }}</el-descriptions-item>
          </el-descriptions>
          
          <h5 style="margin-top: 15px; margin-bottom: 10px;">列信息</h5>
          <el-table :data="selectedData.clickhouse_info.columns" size="small" border>
            <el-table-column prop="name" label="列名" width="200" />
            <el-table-column prop="type" label="数据类型" width="150" />
            <el-table-column prop="default_type" label="默认类型" width="120" />
            <el-table-column prop="default_expression" label="默认表达式" />
          </el-table>
          
          <!-- 样本数据 -->
          <div v-if="selectedData.clickhouse_info.sample_data && selectedData.clickhouse_info.sample_data.length > 0" style="margin-top: 20px;">
            <h5 style="margin-bottom: 10px;">样本数据（前10行）</h5>
            <el-table 
              :data="selectedData.clickhouse_info.sample_data" 
              size="small" 
              border 
              height="300"
              style="width: 100%"
            >
              <el-table-column 
                v-for="column in selectedData.clickhouse_info.columns" 
                :key="column.name"
                :prop="column.name" 
                :label="column.name"
                :width="getColumnWidth(column.name)"
                show-overflow-tooltip
              >
                <template #default="{ row }">
                  <span class="sample-data-cell">{{ formatCellValue(row[column.name]) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        
        <!-- 错误信息 -->
        <el-alert
          v-if="selectedData.clickhouse_info?.error"
          title="ClickHouse信息获取失败"
          type="warning"
          :closable="false"
          style="margin-bottom: 15px;"
        >
          <p>{{ selectedData.clickhouse_info.error }}</p>
        </el-alert>
        
        <!-- 操作提示 -->
        <el-alert
          title="操作提示"
          type="info"
          :closable="false"
        >
          <p>• 您可以通过切换"历史数据"开关来标记此数据是否用于包络分析</p>
          <p>• 历史数据将用于生成包络边界，为实时数据提供对比基准</p>
          <p>• 点击下方"包络分析"按钮可以查看基于历史数据的包络图表</p>
        </el-alert>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="viewDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="goToAnalysis">
            <el-icon><TrendCharts /></el-icon>
            包络分析
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Upload,
  View,
  Delete,
  TrendCharts,
  Setting,
  Timer,
  InfoFilled,
  FolderOpened,
  CircleCheck,
  DataAnalysis,
  List,
  Search,
  Document,
  Files,
  Warning
} from '@element-plus/icons-vue'
import { dataApi } from '@/api'
import type { ExperimentType, ExperimentData } from '@/types'

const route = useRoute()
const router = useRouter()

const experimentType = ref<ExperimentType>()
const experimentData = ref<ExperimentData[]>([])
const statistics = ref<{
  total_count: number
  historical_count: number
  active_count: number
  total_rows: number
}>()
const loading = ref(false)
const updating = ref(new Set<number>())
const searchText = ref('')
const viewDialogVisible = ref(false)
const selectedData = ref<ExperimentData | null>(null)

// 搜索过滤后的数据
const filteredData = computed(() => {
  if (!searchText.value) {
    return experimentData.value
  }
  
  const search = searchText.value.toLowerCase()
  return experimentData.value.filter(item => 
    item.data_name.toLowerCase().includes(search) ||
    item.file_name.toLowerCase().includes(search)
  )
})

// 表格行样式
const tableRowClassName = ({ row }: { row: ExperimentData }) => {
  if (row.status !== 'active') return 'disabled-row'
  if (row.is_historical) return 'historical-row'
  return 'active-row'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return '-'
  }
}

const fetchData = async () => {
  try {
    loading.value = true
    const id = parseInt(route.params.id as string)
    
    // 获取实验数据（包含试验类型信息和统计信息）
    const response = await dataApi.getExperimentData(id)
    experimentType.value = response.experiment_type
    experimentData.value = response.experiment_data
    statistics.value = response.statistics
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleHistoricalToggle = async (row: ExperimentData) => {
  try {
    updating.value.add(row.id)
    await dataApi.updateHistoricalStatus(row.id, row.is_historical)
    ElMessage.success('更新成功')
    await fetchData() // 重新获取统计数据
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败')
    row.is_historical = !row.is_historical // 回滚状态
  } finally {
    updating.value.delete(row.id)
  }
}

const handleViewData = async (row: ExperimentData) => {
  try {
    // 调用后端API获取详细信息
    const detailInfo = await dataApi.getExperimentDataInfo(row.id)
    selectedData.value = detailInfo
    viewDialogVisible.value = true
  } catch (error) {
    console.error('获取数据详情失败:', error)
    ElMessage.error('获取数据详情失败')
  }
}

// 格式化单元格值
const formatCellValue = (value: any) => {
  if (value === null || value === undefined) {
    return 'NULL'
  }
  if (typeof value === 'number') {
    // 如果是小数，保留4位小数
    if (value % 1 !== 0) {
      return value.toFixed(4)
    }
    return value.toString()
  }
  return value.toString()
}

// 获取列宽度
const getColumnWidth = (columnName: string) => {
  // 根据列名设置不同的宽度
  if (columnName.includes('time') || columnName.includes('timestamp')) {
    return 180
  }
  if (columnName.length > 15) {
    return 150
  }
  return 120
}

const goToAnalysis = () => {
  viewDialogVisible.value = false
  router.push(`/envelope/${route.params.id}`)
}

const handleDelete = async (row: ExperimentData) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据 "${row.data_name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false,
        customClass: 'delete-confirm-dialog'
      }
    )
    
    await dataApi.deleteExperimentData(row.id)
    ElMessage({
      type: 'success',
      message: '删除成功',
      duration: 2000
    })
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(fetchData)
</script>

<style scoped>
/* 页面容器 */
.data-management {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
}

/* 页面头部 */
.page-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 24px 0;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  color: white;
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
  color: #ffd700;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  margin: 0;
  font-weight: 500;
}

.action-section {
  display: flex;
  gap: 12px;
}

/* 内容容器 */
.content-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px 40px;
}

.data-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 卡片样式 */
.info-card,
.stats-card,
.table-card {
  border-radius: 16px;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.info-card:hover,
.stats-card:hover,
.table-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  font-weight: 600;
  color: #2c3e50;
}

.header-icon {
  font-size: 20px;
  color: #667eea;
  margin-right: 8px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 描述列表样式 */
.label-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.data-column-tag {
  margin: 2px;
  font-weight: 500;
}

/* 统计卡片 */
.stat-item {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fc 0%, #ecf0f9 100%);
  border-radius: 12px;
  border: 1px solid rgba(103, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(103, 126, 234, 0.3);
}

.stat-item:hover .stat-icon {
  color: white !important;
}

.stat-icon {
  font-size: 24px;
  margin-right: 8px;
}

.stat-icon.total {
  color: #667eea;
}

.stat-icon.historical {
  color: #52c41a;
}

.stat-icon.active {
  color: #1890ff;
}

.stat-icon.rows {
  color: #722ed1;
}

/* 表格样式 */
.modern-table {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e8ecf4;
}

.modern-table :deep(.el-table__header-wrapper) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.modern-table :deep(.el-table__header th) {
  background: transparent !important;
  color: white !important;
  font-weight: 600;
  border: none;
  padding: 16px;
}

.modern-table :deep(.el-table__row) {
  transition: all 0.2s ease;
}

.modern-table :deep(.el-table__row:hover) {
  background: rgba(103, 126, 234, 0.05) !important;
}

.modern-table :deep(.active-row) {
  background: rgba(82, 196, 26, 0.02);
}

.modern-table :deep(.historical-row) {
  background: rgba(24, 144, 255, 0.02);
}

.modern-table :deep(.disabled-row) {
  background: rgba(0, 0, 0, 0.02);
  color: #999;
}

.modern-table :deep(.el-table td) {
  border-color: #f0f2f5;
  padding: 16px;
}

/* 表格单元格 */
.data-name-cell,
.file-name-cell,
.time-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cell-icon {
  font-size: 16px;
  color: #667eea;
  flex-shrink: 0;
}

.cell-text {
  font-weight: 500;
  color: #2c3e50;
}

.file-name-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.count-cell,
.switch-cell {
  display: flex;
  justify-content: center;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.action-buttons .el-button {
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 空状态 */
.empty-state {
  margin-top: 60px;
  text-align: center;
}

.empty-image {
  font-size: 80px;
  color: #d9d9d9;
  margin-bottom: 16px;
}

.empty-description {
  font-size: 18px;
  color: #666;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 14px;
  color: #999;
  margin-bottom: 24px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-container {
    padding: 24px 16px 32px;
  }
  
  .header-content {
    padding: 0 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .action-section {
    flex-direction: column;
    gap: 8px;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .action-section {
    flex-direction: row;
    justify-content: center;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .data-content {
    gap: 24px;
  }
  
  .stat-item {
    padding: 16px 12px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .action-buttons .el-button {
    width: 100%;
    padding: 4px 8px;
    font-size: 12px;
  }
}

/* Element Plus 组件样式覆盖 */
:deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(103, 126, 234, 0.1);
}

:deep(.el-card__body) {
  padding: 24px;
}

:deep(.el-descriptions__label) {
  font-weight: 600 !important;
  color: #2c3e50 !important;
}

:deep(.el-descriptions__content) {
  color: #495057 !important;
}

:deep(.el-tag) {
  font-weight: 500;
  border-radius: 6px;
}

:deep(.el-switch) {
  height: 24px;
}

:deep(.el-switch__core) {
  height: 24px;
  border-radius: 12px;
}

:deep(.el-statistic__number) {
  font-weight: 700;
  color: inherit;
}

:deep(.el-statistic__title) {
  font-weight: 600;
  color: inherit;
}

/* 样本数据表格样式 */
.sample-data-cell {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #333;
}

/* 样本数据表格的表头样式 */
:deep(.el-table__header-wrapper .el-table__header) {
  background-color: #f5f7fa;
}

:deep(.el-table__body-wrapper .el-table__row:nth-child(even)) {
  background-color: #fafafa;
}

:deep(.el-table__body-wrapper .el-table__row:hover) {
  background-color: #e8f4fd !important;
}
</style>
