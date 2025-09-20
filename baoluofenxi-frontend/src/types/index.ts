export interface ExperimentType {
  id: number
  name: string
  description: string
  time_column: string
  data_columns: string[]
  created_at: string
}

export interface ExperimentData {
  id: number
  experiment_type_id: number
  data_name: string
  file_name: string
  clickhouse_table_name: string
  row_count: number
  upload_time: string
  upload_time_formatted?: string
  is_historical: boolean
  status: string
  clickhouse_info?: {
    table_name: string
    row_count: number
    columns: Array<{
      name: string
      type: string
      default_type: string
      default_expression: string
    }>
    error?: string
  }
}

export interface EnvelopeSettings {
  id: number
  experiment_type_id: number
  selected_columns: string[]
  time_range_start?: number
  time_range_end?: number
  updated_at: string
}

export interface EnvelopeData {
  time_points: number[]
  envelope_data: {
    [column: string]: {
      upper: number[]
      lower: number[]
    }
  }
  data_count: number
  time_range: {
    min: number
    max: number
  }
}

export interface ComparisonData {
  filename: string
  headers: string[]
  data: Array<Record<string, any>>
}

// 临时对比数据结构
export interface TempComparisonData {
  temp_data_id: string
  row_count: number
  columns: string[]
  time_range: {
    min: number
    max: number
  }
}

// 包络对比结果
export interface EnvelopeComparisonResult {
  envelope_data: EnvelopeData
  comparison_data: {
    time_points: number[]
    data: {
      [column: string]: number[]
    }
  }
}



export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
}

export interface FilePreview {
  file_info: {
    name: string
    rows_preview: number
    total_columns: number
    columns: string[]
  }
  validation: {
    is_valid: boolean
    valid: boolean
    issues: string[]
    message: string
  }
  data_preview: Record<string, any>[]
  column_info: Record<string, any>
}
