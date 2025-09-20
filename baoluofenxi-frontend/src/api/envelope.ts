import api from './index'
import type { EnvelopeSettings, ApiResponse } from '../types'

export const envelopeApi = {
  // 获取包络分析信息
  getInfo(experimentTypeId: number): Promise<any> {
    return api.get(`/api/envelope/${experimentTypeId}/info`).then(res => res.data.data)
  },

  // 获取包络设置
  getSettings(experimentTypeId: number): Promise<EnvelopeSettings> {
    return api.get(`/api/envelope/${experimentTypeId}/settings`).then(res => res.data)
  },

  // 保存包络设置
  saveSettings(experimentTypeId: number, selectedColumns: string[]): Promise<ApiResponse> {
    return api.post(`/api/envelope/${experimentTypeId}/settings`, {
      selected_columns: selectedColumns
    }).then(res => res.data)
  },

  // 获取包络数据 - 历史数据的包络线
  getEnvelopeData(experimentTypeId: number, params: {
    selected_columns: string[]
    use_sampling?: boolean
    sampling_points?: number
  }): Promise<any> {
    return api.post(`/api/envelope/${experimentTypeId}/envelope`, params).then(res => res.data.data)
  },

  // 上传临时对比数据到ClickHouse
  uploadTempComparisonData(experimentTypeId: number, file: File): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/envelope/${experimentTypeId}/temp-upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(res => res.data)
  },

  // 获取包络对比数据
  compareEnvelopeData(experimentTypeId: number, params: {
    selected_columns: string[]
    temp_data_id: string
    use_sampling?: boolean
    sampling_points?: number
  }): Promise<any> {
    return api.post(`/api/envelope/${experimentTypeId}/compare`, params).then(res => res.data.data)
  },

  // 保存临时数据到MySQL
  saveTempData(experimentTypeId: number, tempDataId: string, dataName: string, fileName: string): Promise<any> {
    return api.post(`/api/envelope/${experimentTypeId}/save-temp`, {
      temp_data_id: tempDataId,
      data_name: dataName,
      file_name: fileName
    }).then(res => res.data)
  },

  // 删除临时数据
  deleteTempData(experimentTypeId: number, tempDataId: string): Promise<any> {
    return api.post(`/api/envelope/${experimentTypeId}/delete-temp`, {
      temp_data_id: tempDataId
    }).then(res => res.data)
  }
}
