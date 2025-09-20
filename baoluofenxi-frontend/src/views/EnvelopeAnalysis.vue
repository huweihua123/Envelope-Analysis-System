<template>
  <div class="envelope-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>包络分析 - {{ experimentType?.name }}</span>
          <div>
            <el-button type="info" @click="$router.push(`/data-management/${$route.params.id}`)">
              <el-icon><FolderOpened /></el-icon>
              数据管理
            </el-button>
            <el-button @click="$router.back()">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
          </div>
        </div>
      </template>
      
      <div v-if="experimentType" class="analysis-content">
        <!-- 步骤指引 -->
        <el-steps :active="currentStep" finish-status="success" style="margin-bottom: 20px;">
          <el-step title="选择数据列" />
          <el-step title="加载历史包络" />
          <el-step title="添加对比数据" />
          <el-step title="包络对比分析" />
        </el-steps>
        
        <!-- 第一步：列选择 -->
        <el-card shadow="hover" class="step-card" v-if="currentStep >= 0">
          <template #header>
            <span>步骤1: 选择要分析的数据列</span>
          </template>
          <el-checkbox-group v-model="selectedColumns" @change="handleColumnChange">
            <el-checkbox 
              v-for="column in experimentType.data_columns" 
              :key="column" 
              :label="column"
              :value="column"
            >
              {{ column }}
            </el-checkbox>
          </el-checkbox-group>
          <div style="margin-top: 15px;">
            <el-button 
              type="primary" 
              :disabled="selectedColumns.length === 0"
              @click="nextStep"
            >
              下一步：加载历史包络
            </el-button>
          </div>
        </el-card>

        <!-- 第二步：加载历史包络 -->
        <el-card shadow="hover" class="step-card" v-if="currentStep >= 1">
          <template #header>
            <span>步骤2: 加载历史数据包络线</span>
          </template>
          <div class="step-content">
            <el-alert 
              title="历史数据包络分析" 
              description="系统将分析所有历史数据，在每个时间点上计算最大值和最小值，形成上下包络线" 
              type="info" 
              show-icon 
              style="margin-bottom: 15px;"
            />
            
            <!-- 采样配置 -->
            <el-card shadow="never" style="margin-bottom: 15px; border: 1px dashed #dcdfe6;">
              <template #header>
                <span style="font-size: 14px;">数据处理配置</span>
              </template>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="数据处理模式:">
                    <el-radio-group v-model="useSampling">
                      <el-radio :value="true">采样处理（推荐）</el-radio>
                      <el-radio :value="false">完整数据处理</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item v-if="useSampling" label="采样点数:">
                    <el-input-number 
                      v-model="samplingPoints" 
                      :min="50" 
                      :max="2000" 
                      :step="50"
                      style="width: 120px"
                    />
                    <el-text type="info" size="small" style="margin-left: 10px;">
                      采样点越多越精细，但处理时间越长
                    </el-text>
                  </el-form-item>
                  <el-form-item v-else label="数据量:">
                    <el-text type="warning" size="small">
                      将处理所有原始数据点，可能较慢
                    </el-text>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-card>
            
            <el-button 
              type="primary" 
              @click="loadHistoricalEnvelope" 
              :loading="loadingEnvelope"
              :disabled="selectedColumns.length === 0"
            >
              <el-icon><Refresh /></el-icon>
              加载历史包络数据
              <span v-if="useSampling">（采样{{ samplingPoints }}点）</span>
              <span v-else>（完整数据）</span>
            </el-button>
            <el-button 
              v-if="envelopeData"
              type="success" 
              @click="nextStep"
            >
              下一步：添加对比数据
            </el-button>
          </div>
        </el-card>

        <!-- 第三步：添加对比数据 -->
        <el-card shadow="hover" class="step-card" v-if="currentStep >= 2">
          <template #header>
            <span>步骤3: 添加新数据进行对比</span>
          </template>
          <div class="step-content">
            <el-alert 
              title="添加对比数据" 
              description="上传CSV文件到ClickHouse进行对比分析，支持大文件处理" 
              type="info" 
              show-icon 
              style="margin-bottom: 15px;"
            />
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="false"
              accept=".csv"
              drag
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将CSV文件拖到此处，或<em>点击选择文件</em>
              </div>
            </el-upload>
            
            <div v-if="comparisonFile" style="margin-top: 15px;">
              <el-tag size="large" closable @close="removeComparisonFile">
                <el-icon><Document /></el-icon>
                {{ comparisonFile.name }}
              </el-tag>
              <div style="margin-top: 10px;">
                <el-button 
                  type="primary" 
                  @click="loadComparisonData" 
                  :loading="loadingComparison"
                >
                  上传到ClickHouse
                </el-button>
                <el-button 
                  v-if="tempComparisonData"
                  type="success" 
                  @click="nextStep"
                >
                  下一步：开始对比分析
                </el-button>
              </div>
            </div>
            
            <div v-if="tempComparisonData" style="margin-top: 15px; padding: 10px; background: #f5f5f5; border-radius: 4px;">
              <p><strong>上传成功！</strong></p>
              <p>数据行数: {{ tempComparisonData.row_count }}</p>
              <p>时间范围: {{ tempComparisonData.time_range.min }} - {{ tempComparisonData.time_range.max }}</p>
              <p>可用列: {{ tempComparisonData.columns.join(', ') }}</p>
            </div>
          </div>
        </el-card>

        <!-- 第四步：对比分析 -->
        <el-card shadow="hover" class="step-card" v-if="currentStep >= 3">
          <template #header>
            <span>步骤4: 执行对比分析</span>
          </template>
          <div class="step-content">
            <!-- 对比数据采样配置 -->
            <el-card shadow="never" style="margin-bottom: 15px; border: 1px dashed #dcdfe6;">
              <template #header>
                <span style="font-size: 14px;">对比数据处理配置</span>
              </template>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="对比数据处理模式:">
                    <el-radio-group v-model="comparisonUseSampling">
                      <el-radio :value="true">采样处理（推荐）</el-radio>
                      <el-radio :value="false">完整数据处理</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item v-if="comparisonUseSampling" label="对比采样点数:">
                    <el-input-number 
                      v-model="comparisonSamplingPoints" 
                      :min="50" 
                      :max="2000" 
                      :step="50"
                      style="width: 120px"
                    />
                    <el-text type="info" size="small" style="margin-left: 10px;">
                      建议与历史包络采样点数保持一致
                    </el-text>
                  </el-form-item>
                  <el-form-item v-else label="对比数据量:">
                    <el-text type="warning" size="small">
                      将处理对比数据的所有原始点
                    </el-text>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <!-- 采样一致性提示 -->
              <el-alert 
                v-if="envelopeData && (
                  (useSampling !== comparisonUseSampling) || 
                  (useSampling && comparisonUseSampling && samplingPoints !== comparisonSamplingPoints)
                )"
                title="数据处理不一致提醒" 
                type="warning" 
                show-icon
                :closable="false"
              >
                <template #default>
                  <p><strong>历史包络:</strong> {{ useSampling ? `采样${samplingPoints}点` : '完整数据' }}</p>
                  <p><strong>对比数据:</strong> {{ comparisonUseSampling ? `采样${comparisonSamplingPoints}点` : '完整数据' }}</p>
                  <p>建议保持相同的处理模式以确保对比准确性</p>
                </template>
              </el-alert>
            </el-card>
            
            <el-space>
              <el-button 
                type="primary"
                size="large"
                @click="performComparison"
                :loading="loadingComparison"
                :disabled="!envelopeData || !tempComparisonData || selectedColumns.length === 0"
              >
                <el-icon><TrendCharts /></el-icon>
                执行包络对比分析
                <span v-if="comparisonUseSampling">（采样{{ comparisonSamplingPoints }}点）</span>
                <span v-else>（完整数据）</span>
              </el-button>
              
              <el-input
                v-if="comparisonResult"
                v-model="dataName"
                placeholder="输入数据名称以保存到数据库"
                style="width: 200px;"
                clearable
              />
              
              <el-button 
                v-if="comparisonResult && dataName"
                type="success"
                @click="saveComparisonData"
              >
                <el-icon><Document /></el-icon>
                保存到数据库
              </el-button>
              
              <el-button 
                v-if="comparisonResult"
                type="warning"
                @click="deleteComparisonData"
              >
                清理临时数据
              </el-button>
            </el-space>
          </div>
        </el-card>
        
        <!-- 图表区域 -->
        <el-card v-if="envelopeData || comparisonResult" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>包络分析图表</span>
              <el-space>
                <el-select v-model="chartType" @change="updateChart" style="width: 120px;">
                  <el-option label="折线图" value="line" />
                  <el-option label="散点图" value="scatter" />
                </el-select>
                <el-button type="warning" @click="exportChart" :disabled="!chartInstance">
                  <el-icon><Download /></el-icon>
                  导出图表
                </el-button>
              </el-space>
            </div>
          </template>
          
          <!-- 数据统计信息 -->
          <el-row v-if="envelopeData" :gutter="16" style="margin-bottom: 16px;">
            <el-col :span="6">
              <el-statistic title="历史数据集数量" :value="envelopeData.data_count || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="包络数据点数" :value="envelopeData.sampling_points || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="原始数据点数" :value="envelopeData.original_points || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="处理模式">
                <template #default>
                  <el-tag :type="envelopeData.sampling_method === 'full_data' ? 'success' : 'primary'">
                    {{ envelopeData.sampling_method === 'full_data' ? '完整数据' : '采样处理' }}
                  </el-tag>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
          
          <div class="chart-container">
            <div
              ref="chartRef"
              class="chart"
              v-loading="loadingEnvelope || loadingComparison"
              element-loading-text="正在分析数据..."
            ></div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, 
  FolderOpened, 
  Refresh, 
  TrendCharts, 
  Download, 
  UploadFilled, 
  Document
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { envelopeApi } from '../api/envelope'
import type { ExperimentType, EnvelopeData, TempComparisonData, EnvelopeComparisonResult } from '../types'

const route = useRoute()
const router = useRouter()
const chartRef = ref<HTMLDivElement>()
const uploadRef = ref()

// 基础状态
const experimentType = ref<ExperimentType>()
const currentStep = ref(0)

// 数据相关
const selectedColumns = ref<string[]>([])
const envelopeData = ref<EnvelopeData>()
const tempComparisonData = ref<TempComparisonData>()
const comparisonResult = ref<EnvelopeComparisonResult>()
const comparisonFile = ref<File>()
const dataName = ref('')

// 采样配置
const useSampling = ref(true)
const samplingPoints = ref(200)

// 对比数据采样配置
const comparisonUseSampling = ref(true)
const comparisonSamplingPoints = ref(200)

// 加载状态
const loadingEnvelope = ref(false)
const loadingComparison = ref(false)

// 图表相关
const chartInstance = ref<echarts.ECharts>()
const chartType = ref('line')
const showHistoricalData = ref(false)

// 获取试验类型信息
const fetchExperimentType = async () => {
  try {
    const response = await envelopeApi.getInfo(Number(route.params.id))
    experimentType.value = response.experiment_type
    if (!experimentType.value) {
      ElMessage.error('试验类型不存在')
      router.push('/experiment-types')
      return
    }
    
    // 加载已保存的设置
    if (response.envelope_settings?.selected_columns) {
      selectedColumns.value = response.envelope_settings.selected_columns
    }
  } catch (error) {
    console.error('获取试验类型失败:', error)
    ElMessage.error('获取试验类型失败')
  }
}

// 步骤控制
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const handleColumnChange = (value: string[]) => {
  selectedColumns.value = value
  // 自动保存设置
  if (experimentType.value && value.length > 0) {
    envelopeApi.saveSettings(experimentType.value.id, value).catch(console.error)
  }
}

// 加载历史包络数据
const loadHistoricalEnvelope = async () => {
  if (!experimentType.value || selectedColumns.value.length === 0) {
    ElMessage.warning('请先选择数据列')
    return
  }
  
  loadingEnvelope.value = true
  try {
    // 构建请求参数，包含采样配置
    const params = {
      selected_columns: selectedColumns.value,
      use_sampling: useSampling.value,
      sampling_points: samplingPoints.value
    }
    
    const data = await envelopeApi.getEnvelopeData(experimentType.value.id, params)
    envelopeData.value = data
    
    await nextTick()
    renderChart()
    
    // 根据采样模式显示不同的成功消息
    const message = useSampling.value 
      ? `历史包络数据加载成功（采样${data.sampling_points || samplingPoints.value}点）`
      : `历史包络数据加载成功（完整${data.original_points || 0}点）`
    
    ElMessage.success(message)
  } catch (error) {
    console.error('加载包络数据失败:', error)
    ElMessage.error('加载包络数据失败')
  } finally {
    loadingEnvelope.value = false
  }
}

// 处理文件选择
const handleFileChange = (uploadFile: any) => {
  comparisonFile.value = uploadFile.raw
}

const removeComparisonFile = () => {
  comparisonFile.value = undefined
  tempComparisonData.value = undefined
  comparisonResult.value = undefined
  updateChart()
}

// 上传临时对比数据到ClickHouse
const loadComparisonData = async () => {
  if (!comparisonFile.value || !experimentType.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  loadingComparison.value = true
  try {
    const result = await envelopeApi.uploadTempComparisonData(experimentType.value.id, comparisonFile.value)
    if (result.success) {
      tempComparisonData.value = result.data
      ElMessage.success(`对比数据上传成功，共 ${result.data.row_count} 条记录`)
    } else {
      ElMessage.error(result.message || '上传失败')
    }
  } catch (error) {
    console.error('上传对比数据失败:', error)
    ElMessage.error('上传对比数据失败')
  } finally {
    loadingComparison.value = false
  }
}

// 执行对比分析
const performComparison = async () => {
  if (!envelopeData.value || !tempComparisonData.value || !experimentType.value) {
    ElMessage.warning('请先加载历史包络和对比数据')
    return
  }
  
  if (selectedColumns.value.length === 0) {
    ElMessage.warning('请选择要对比的数据列')
    return
  }
  
  loadingComparison.value = true
  try {
    // 构建对比分析参数，包含采样配置
    const compareParams = {
      selected_columns: selectedColumns.value,
      temp_data_id: tempComparisonData.value.temp_data_id,
      use_sampling: comparisonUseSampling.value,
      sampling_points: comparisonSamplingPoints.value
    }
    
    const result = await envelopeApi.compareEnvelopeData(
      experimentType.value.id,
      compareParams
    )
    
    comparisonResult.value = result
    
    // 根据采样模式显示不同的成功消息
    const message = comparisonUseSampling.value 
      ? `对比分析完成（对比数据采样${result.comparison_sampling_points || comparisonSamplingPoints.value}点）`
      : `对比分析完成（对比数据完整${result.comparison_original_points || 0}点）`
    
    ElMessage.success(message)
    updateChart()
  } catch (error) {
    console.error('对比分析失败:', error)
    ElMessage.error('对比分析失败')
  } finally {
    loadingComparison.value = false
  }
}

// 保存对比数据到MySQL
const saveComparisonData = async () => {
  if (!tempComparisonData.value || !experimentType.value || !dataName.value) {
    ElMessage.warning('请输入数据名称')
    return
  }
  
  try {
    const result = await envelopeApi.saveTempData(
      experimentType.value.id,
      tempComparisonData.value.temp_data_id,
      dataName.value,
      comparisonFile.value?.name || 'comparison_data.csv'
    )
    
    if (result.success) {
      ElMessage.success('数据保存成功')
      // 清理临时数据引用
      tempComparisonData.value = undefined
      comparisonFile.value = undefined
      dataName.value = ''
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存数据失败:', error)
    ElMessage.error('保存数据失败')
  }
}

// 删除临时数据
const deleteComparisonData = async () => {
  if (!tempComparisonData.value || !experimentType.value) {
    return
  }
  
  try {
    const result = await envelopeApi.deleteTempData(
      experimentType.value.id,
      tempComparisonData.value.temp_data_id
    )
    
    if (result.success) {
      ElMessage.success('临时数据已清理')
    }
  } catch (error) {
    console.error('清理临时数据失败:', error)
  }
  
  // 无论成功与否都清理本地引用
  tempComparisonData.value = undefined
  comparisonResult.value = undefined
  comparisonFile.value = undefined
  updateChart()
}

// 渲染图表
const renderChart = () => {
  if (!chartRef.value || !envelopeData.value) return
  
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  
  chartInstance.value = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: '包络分析图',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: generateLegendData(),
      bottom: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: experimentType.value?.time_column || 'Time',
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      name: '数值',
      nameLocation: 'middle',
      nameGap: 40
    },
    series: generateSeriesData()
  }
  
  chartInstance.value.setOption(option)
}

// 生成图例数据
const generateLegendData = () => {
  const legends: string[] = []
  selectedColumns.value.forEach(column => {
    legends.push(`${column} 上包络`)
    legends.push(`${column} 下包络`)
    if (comparisonResult.value) {
      legends.push(`${column} 新数据`)
    }
  })
  return legends
}

// 生成系列数据
const generateSeriesData = () => {
  const series: any[] = []
  
  if (!envelopeData.value) return series
    selectedColumns.value.forEach((column, index) => {
    // 历史包络数据颜色（较淡的颜色用于包络）
    const envelopeColors = ['#a0cfff', '#95d475', '#f0c674', '#f79c9c', '#c8c9cc']
    // 实际数据颜色（鲜艳颜色用于新数据）
    const actualDataColors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
    
    const envelopeColor = envelopeColors[index % envelopeColors.length]
    const actualColor = actualDataColors[index % actualDataColors.length]
    
    // 历史包络数据
    const envelopeColumn = envelopeData.value.envelope_data[column]
    if (envelopeColumn) {
      // 上包络线 - 使用虚线
      const upperData = envelopeData.value.time_points.map((time, i) => [time, envelopeColumn.upper[i]])
      series.push({
        name: `${column} 上包络`,
        type: chartType.value,
        data: upperData,
        itemStyle: { color: envelopeColor },
        lineStyle: { 
          width: 2, 
          type: 'dashed' // 虚线
        },
        symbol: 'none'
      })
      
      // 下包络线 - 使用虚线
      const lowerData = envelopeData.value.time_points.map((time, i) => [time, envelopeColumn.lower[i]])
      series.push({
        name: `${column} 下包络`,
        type: chartType.value,
        data: lowerData,
        itemStyle: { color: envelopeColor },
        lineStyle: { 
          width: 2, 
          type: 'dashed' // 虚线
        },
        symbol: 'none'
      })
    }
    
    // 新数据对比线 - 使用实线，鲜艳颜色
    if (comparisonResult.value && comparisonResult.value.comparison_data.data[column]) {
      const newData = comparisonResult.value.comparison_data.time_points.map((time, i) => [
        time,
        comparisonResult.value!.comparison_data.data[column][i]
      ])
      
      series.push({
        name: `${column} 新数据`,
        type: 'line',
        data: newData,
        itemStyle: { color: actualColor },
        lineStyle: { 
          width: 3, // 稍微粗一点突出显示
          type: 'solid' // 实线
        },
        symbol: 'circle',
        symbolSize: 4,
        emphasis: {
          itemStyle: {
            borderWidth: 2,
            borderColor: '#fff'
          }
        }
      })
    }
  })
  
  return series
}

// 更新图表
const updateChart = () => {
  if (envelopeData.value) {
    renderChart()
  }
}

// 导出图表
const exportChart = () => {
  if (!chartInstance.value) return
  
  const url = chartInstance.value.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })
  
  const link = document.createElement('a')
  link.href = url
  link.download = `envelope-analysis-${Date.now()}.png`
  link.click()
  
  ElMessage.success('图表导出成功')
}

// 窗口大小变化处理
const handleResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

watch(() => selectedColumns.value, () => {
  if (selectedColumns.value.length > 0 && envelopeData.value) {
    updateChart()
  }
})

// 同步采样设置：当历史包络采样设置改变时，自动同步到对比采样
watch(() => useSampling.value, (newValue) => {
  comparisonUseSampling.value = newValue
})

watch(() => samplingPoints.value, (newValue) => {
  comparisonSamplingPoints.value = newValue
})

onMounted(async () => {
  await fetchExperimentType()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header > div {
  display: flex;
  gap: 10px;
}

.step-card {
  margin-bottom: 20px;
}

.step-content {
  padding: 10px 0;
}

.chart-card {
  margin-top: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  position: relative;
  height: 500px;
}

.chart {
  width: 100%;
  height: 100%;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

:deep(.el-steps) {
  margin-bottom: 20px;
}
</style>
