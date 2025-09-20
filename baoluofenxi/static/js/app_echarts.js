// 包络分析系统前端JavaScript (基于ECharts)

// 全局变量
let envelopeChart = null;
let currentExperimentType = null;
let selectedColumns = [];
let historicalDataIds = [];

// DOM加载完成后执行
$(document).ready(function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化文件上传
    initFileUpload();
    
    // 初始化ECharts图表
    if ($('#envelopeChart').length) {
        initEChartsEnvelopeChart();
    }
    
    // 初始化列选择器
    if ($('.column-selector').length) {
        initColumnSelector();
    }
    
    // 初始化历史数据管理
    if ($('.historical-data-manager').length) {
        initHistoricalDataManager();
    }
    
    // 获取当前试验类型ID
    const expTypeId = $('[data-experiment-type-id]').data('experiment-type-id');
    if (expTypeId) {
        setCurrentExperimentType(expTypeId);
    }
});

// 初始化工具提示
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化ECharts包络图表
function initEChartsEnvelopeChart() {
    const chartContainer = document.getElementById('envelopeChart');
    if (!chartContainer) return;
    
    // 初始化ECharts实例
    envelopeChart = echarts.init(chartContainer);
    
    // 基础配置
    const option = {
        title: {
            text: '包络分析图',
            left: 'center',
            textStyle: {
                fontSize: 18,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
            },
            formatter: function(params) {
                let result = `时间: ${params[0].axisValue}<br/>`;
                params.forEach(param => {
                    result += `${param.seriesName}: ${param.value[1]}<br/>`;
                });
                return result;
            }
        },
        legend: {
            data: [],
            top: '10%',
            type: 'scroll'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            top: '25%',
            containLabel: true
        },
        toolbox: {
            feature: {
                saveAsImage: {
                    title: '保存为图片'
                },
                dataZoom: {
                    title: {
                        zoom: '区域缩放',
                        back: '还原缩放'
                    }
                },
                restore: {
                    title: '还原'
                }
            }
        },
        xAxis: {
            type: 'value',
            name: '时间',
            nameLocation: 'middle',
            nameGap: 30,
            axisLabel: {
                formatter: '{value}'
            }
        },
        yAxis: {
            type: 'value',
            name: '数值',
            nameLocation: 'middle',
            nameGap: 50
        },
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: 0,
                filterMode: 'none'
            },
            {
                type: 'slider',
                xAxisIndex: 0,
                filterMode: 'none',
                bottom: '5%'
            }
        ],
        series: []
    };
    
    envelopeChart.setOption(option);
    
    // 监听窗口大小变化
    window.addEventListener('resize', function() {
        envelopeChart.resize();
    });
}

// 更新ECharts图表数据
function updateEChartsData(envelopeData, newData) {
    if (!envelopeChart) return;
    
    const series = [];
    const legendData = [];
    
    // 生成颜色调色板
    const colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
        '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
    ];
    
    let colorIndex = 0;
    
    // 添加包络线（上下边界）
    if (envelopeData && selectedColumns.length > 0) {
        selectedColumns.forEach(column => {
            const color = colors[colorIndex % colors.length];
            colorIndex++;
            
            if (envelopeData.upper && envelopeData.upper[column]) {
                // 上包络线
                series.push({
                    name: `${column}_上包络`,
                    type: 'line',
                    data: envelopeData.upper[column].map(point => [point.t, point.value]),
                    lineStyle: {
                        color: color,
                        width: 2,
                        type: 'dashed'
                    },
                    symbol: 'none',
                    smooth: true,
                    itemStyle: {
                        color: color
                    }
                });
                legendData.push(`${column}_上包络`);
            }
            
            if (envelopeData.lower && envelopeData.lower[column]) {
                // 下包络线
                series.push({
                    name: `${column}_下包络`,
                    type: 'line',
                    data: envelopeData.lower[column].map(point => [point.t, point.value]),
                    lineStyle: {
                        color: color,
                        width: 2,
                        type: 'dashed'
                    },
                    symbol: 'none',
                    smooth: true,
                    itemStyle: {
                        color: color
                    },
                    // 填充区域
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: color + '20' },
                            { offset: 1, color: color + '05' }
                        ])
                    }
                });
                legendData.push(`${column}_下包络`);
            }
        });
    }
    
    // 添加新数据线
    if (newData && Array.isArray(newData)) {
        newData.forEach((dataItem, index) => {
            selectedColumns.forEach(column => {
                if (dataItem.data && dataItem.data[column]) {
                    const color = '#FF4444'; // 新数据用红色突出显示
                    series.push({
                        name: `${dataItem.name}_${column}`,
                        type: 'line',
                        data: dataItem.data[column].map(point => [point.t, point.value]),
                        lineStyle: {
                            color: color,
                            width: 2
                        },
                        symbol: 'circle',
                        symbolSize: 4,
                        smooth: false,
                        itemStyle: {
                            color: color
                        }
                    });
                    legendData.push(`${dataItem.name}_${column}`);
                }
            });
        });
    }
    
    // 更新图表
    envelopeChart.setOption({
        legend: {
            data: legendData
        },
        series: series
    });
}

// 文件上传功能
function initFileUpload() {
    const uploadArea = $('.upload-area');
    const fileInput = $('#fileInput');
    const uploadForm = $('#uploadForm');
    
    if (uploadArea.length === 0) return;
    
    // 拖拽上传
    uploadArea.on('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('dragover');
    });
    
    uploadArea.on('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragover');
    });
    
    uploadArea.on('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragover');
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            fileInput[0].files = files;
            handleFileSelection();
        }
    });
    
    // 点击上传
    uploadArea.on('click', function() {
        fileInput.click();
    });
    
    // 文件选择
    fileInput.on('change', handleFileSelection);
    
    // 表单提交
    if (uploadForm.length) {
        uploadForm.on('submit', handleFileUpload);
    }
}

// 处理文件选择
function handleFileSelection() {
    const files = $('#fileInput')[0].files;
    if (files.length > 0) {
        const file = files[0];
        $('.upload-area .upload-text').html(
            `<i class="fas fa-file-alt fa-2x text-success mb-2"></i><br>
             已选择文件: <strong>${file.name}</strong><br>
             <small class="text-muted">大小: ${formatFileSize(file.size)}</small>`
        );
        $('#uploadBtn').prop('disabled', false);
    }
}

// 处理文件上传
function handleFileUpload(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = $('#fileInput')[0];
    const dataName = $('#dataName').val();
    
    if (fileInput.files.length === 0) {
        showAlert('请选择文件', 'warning');
        return;
    }
    
    if (!dataName.trim()) {
        showAlert('请输入数据名称', 'warning');
        return;
    }
    
    formData.append('file', fileInput.files[0]);
    formData.append('data_name', dataName);
    
    // 显示上传进度
    showUploadProgress();
    
    // 上传文件
    $.ajax({
        url: $(e.target).attr('action'),
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                showAlert('文件上传成功！', 'success');
                resetUploadForm();
                // 可选：跳转到数据管理页面
                setTimeout(() => {
                    window.location.href = `/data-management/${currentExperimentType}`;
                }, 2000);
            } else {
                showAlert(response.message, 'error');
            }
        },
        error: function() {
            showAlert('上传失败，请重试', 'error');
        },
        complete: function() {
            hideUploadProgress();
        }
    });
}

// 显示上传进度
function showUploadProgress() {
    $('#uploadBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>上传中...');
    $('.upload-progress').show();
}

// 隐藏上传进度
function hideUploadProgress() {
    $('#uploadBtn').prop('disabled', false).html('<i class="fas fa-upload me-2"></i>上传文件');
    $('.upload-progress').hide();
}

// 重置上传表单
function resetUploadForm() {
    $('#fileInput').val('');
    $('#dataName').val('');
    $('.upload-area .upload-text').html(
        `<i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i><br>
         <h5>拖拽文件到此处或点击选择</h5>
         <p class="text-muted">支持 CSV, Excel 文件</p>`
    );
    $('#uploadBtn').prop('disabled', true);
}

// 初始化列选择器
function initColumnSelector() {
    $('.column-checkbox').on('change', function() {
        updateSelectedColumns();
        updateEnvelopeChart();
        saveColumnSettings();
    });
    
    // 初始化时获取选中的列
    updateSelectedColumns();
}

// 更新选中的列
function updateSelectedColumns() {
    selectedColumns = [];
    $('.column-checkbox:checked').each(function() {
        selectedColumns.push($(this).val());
    });
}

// 初始化历史数据管理
function initHistoricalDataManager() {
    $('.historical-data-toggle').on('change', function() {
        const dataId = $(this).data('data-id');
        const isHistorical = $(this).prop('checked');
        
        updateHistoricalStatus(dataId, isHistorical);
    });
    
    // 初始化时获取历史数据IDs
    updateHistoricalDataIds();
}

// 更新历史数据IDs
function updateHistoricalDataIds() {
    historicalDataIds = [];
    $('.historical-data-toggle:checked').each(function() {
        historicalDataIds.push($(this).data('data-id'));
    });
}

// 更新包络图表
function updateEnvelopeChart() {
    if (!envelopeChart || !currentExperimentType) return;
    
    if (selectedColumns.length === 0) {
        // 清空图表
        envelopeChart.setOption({
            series: [],
            legend: { data: [] }
        });
        return;
    }
    
    // 获取包络数据
    $.ajax({
        url: `/api/envelope/${currentExperimentType}/data`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            columns: selectedColumns,
            historical_data_ids: historicalDataIds
        }),
        success: function(response) {
            if (response.success) {
                updateEChartsData(response.envelope, response.new_data);
            } else {
                console.error('获取包络数据失败:', response.message);
            }
        },
        error: function() {
            console.error('网络错误：无法获取包络数据');
        }
    });
}

// 保存列设置
function saveColumnSettings() {
    if (!currentExperimentType) return;
    
    $.ajax({
        url: `/api/envelope/${currentExperimentType}/settings`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            selected_columns: selectedColumns
        }),
        success: function(response) {
            if (response.success) {
                console.log('列设置保存成功');
            }
        }
    });
}

// 更新历史数据状态
function updateHistoricalStatus(dataId, isHistorical) {
    $.ajax({
        url: `/api/data/${dataId}/historical`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            is_historical: isHistorical
        }),
        success: function(response) {
            if (response.success) {
                showAlert(isHistorical ? '已添加到历史数据集' : '已从历史数据集移除', 'success');
                updateHistoricalDataIds();
                updateEnvelopeChart();
            }
        },
        error: function() {
            showAlert('更新失败', 'error');
        }
    });
}

// 显示提示信息
function showAlert(message, type) {
    let alertClass = 'alert-info';
    if (type === 'error') alertClass = 'alert-danger';
    else if (type === 'warning') alertClass = 'alert-warning';
    else if (type === 'success') alertClass = 'alert-success';
    
    const alert = $(`
        <div class="alert ${alertClass} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('.container').first().prepend(alert);
    
    // 3秒后自动消失
    setTimeout(() => {
        alert.alert('close');
    }, 3000);
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 设置当前试验类型
function setCurrentExperimentType(typeId) {
    currentExperimentType = typeId;
    console.log('当前试验类型ID:', typeId);
}

// 删除数据
function deleteData(dataId, dataName) {
    if (confirm(`确定要删除数据 "${dataName}" 吗？此操作不可撤销！`)) {
        $.ajax({
            url: `/api/data/${dataId}/delete`,
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    showAlert('数据删除成功', 'success');
                    location.reload();
                } else {
                    showAlert(response.message, 'error');
                }
            },
            error: function() {
                showAlert('删除失败', 'error');
            }
        });
    }
}

// 导出图表
function exportChart() {
    if (!envelopeChart) {
        showAlert('图表未初始化', 'warning');
        return;
    }
    
    const url = envelopeChart.getDataURL({
        pixelRatio: 2,
        backgroundColor: '#fff'
    });
    
    const link = document.createElement('a');
    link.download = `envelope_chart_${new Date().getTime()}.png`;
    link.href = url;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showAlert('图表导出成功', 'success');
}

// 切换全屏显示图表
function toggleFullscreen() {
    const chartContainer = $('#envelopeChart').parent();
    
    if (!document.fullscreenElement) {
        chartContainer[0].requestFullscreen();
    } else {
        document.exitFullscreen();
    }
    
    // 监听全屏状态变化，调整图表大小
    $(document).on('fullscreenchange', function() {
        setTimeout(() => {
            if (envelopeChart) {
                envelopeChart.resize();
            }
        }, 100);
    });
}
