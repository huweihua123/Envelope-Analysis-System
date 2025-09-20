<template>
  <div id="app">
    <el-container>
      <!-- 头部导航 -->
      <el-header>
        <el-menu
          mode="horizontal"
          :default-active="$route.path"
          router
          class="header-menu"
        >
          <el-menu-item index="/" class="logo">
            <el-icon><TrendCharts /></el-icon>
            <span>包络分析系统</span>
          </el-menu-item>
          <div class="flex-grow" />
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/experiment-types">试验类型</el-menu-item>
        </el-menu>
      </el-header>
      
      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { TrendCharts } from '@element-plus/icons-vue'
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.el-container {
  height: 100vh;
  width: 100vw;
}

.el-header {
  padding: 0;
  background-color: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  height: 60px !important;
  flex-shrink: 0;
}

.header-menu {
  border-bottom: none;
  height: 60px;
  padding: 0 20px;
}

.header-menu .el-menu-item {
  height: 60px;
  line-height: 60px;
}

.logo {
  font-weight: bold;
  color: #409eff !important;
  font-size: 18px;
}

.logo .el-icon {
  margin-right: 8px;
}

.flex-grow {
  flex-grow: 1;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  height: calc(100vh - 60px);
  overflow-y: auto;
  flex: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-menu {
    padding: 0 10px;
  }
  
  .el-main {
    padding: 10px;
  }
  
  .logo {
    font-size: 16px;
  }
  
  .header-menu .el-menu-item {
    padding: 0 10px;
  }
}
</style>
