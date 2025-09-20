import api from './index'
import type { ExperimentType, ApiResponse } from '../types'

export const experimentTypeApi = {
  // 获取所有试验类型
  getAll(): Promise<ExperimentType[]> {
    return api.get('/api/experiment-types').then(res => res.data.data)
  },

  // 创建试验类型
  create(data: {
    name: string
    description: string
    time_column: string
    data_columns: string[]
  }): Promise<ApiResponse> {
    return api.post('/api/experiment-types', data).then(res => res.data)
  },

  // 删除试验类型
  delete(id: number): Promise<ApiResponse> {
    return api.delete(`/api/experiment-types/${id}`).then(res => res.data)
  }
}
