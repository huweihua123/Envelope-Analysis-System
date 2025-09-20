import api from './index'
import type { ExperimentData, FilePreview, ApiResponse } from '../types'

export const dataApi = {
  // 获取实验数据列表
  getExperimentData(experimentTypeId: number): Promise<{ 
    experiment_type: any, 
    experiment_data: ExperimentData[],
    statistics: any 
  }> {
    return api.get(`/api/experiment-data/${experimentTypeId}`).then(res => res.data.data)
  },

  // 更新历史数据状态
  updateHistoricalStatus(dataId: number, isHistorical: boolean): Promise<ApiResponse> {
    return api.post(`/api/experiment-data/${dataId}/historical`, {
      is_historical: isHistorical
    }).then(res => res.data)
  },

  // 删除实验数据
  deleteExperimentData(dataId: number): Promise<ApiResponse> {
    return api.delete(`/api/experiment-data/${dataId}`).then(res => res.data)
  },

  // 获取实验数据详情
  getExperimentDataInfo(dataId: number): Promise<ExperimentData> {
    return api.get(`/api/experiment-data/${dataId}/info`).then(res => res.data.data)
  },

  // 文件预览
  previewFile(experimentTypeId: number, file: File): Promise<FilePreview> {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/preview/${experimentTypeId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(res => res.data.preview)
  },

  // 上传数据
  uploadData(experimentTypeId: number, file: File, dataName: string): Promise<ApiResponse> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('data_name', dataName)
    return api.post(`/api/upload/${experimentTypeId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(res => res.data)
  }
}
