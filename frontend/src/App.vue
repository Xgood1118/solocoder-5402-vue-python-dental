<template>
  <el-container class="app-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="28" color="#409EFF"><Star /></el-icon>
        <span class="logo-text">口腔诊所管理</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item v-for="route in menuRoutes" :key="route.path" :index="route.path">
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <span>{{ route.meta.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="page-title">{{ pageTitle }}</span>
        <div class="header-right">
          <el-tag type="success">张医生</el-tag>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Calendar, User, Document, Wallet, Clock, Bell, DataLine, DataBoard, Star } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const menuRoutes = computed(() => {
  return router.options.routes.filter(r => r.meta && !r.meta.hidden && r.path !== '/')
})

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '首页')
</script>

<style scoped>
.app-container {
  height: 100vh;
}
.sidebar {
  background: #304156;
  color: #fff;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid #1f2d3d;
}
.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
}
.menu {
  border: none;
}
.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
.main-content {
  background: #f0f2f5;
  padding: 20px;
}
</style>
