import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '首页概览', icon: 'DataBoard' }
  },
  {
    path: '/appointments',
    name: 'Appointments',
    component: () => import('../views/Appointments.vue'),
    meta: { title: '预约管理', icon: 'Calendar' }
  },
  {
    path: '/patients',
    name: 'Patients',
    component: () => import('../views/Patients.vue'),
    meta: { title: '患者档案', icon: 'User' }
  },
  {
    path: '/patients/:id',
    name: 'PatientDetail',
    component: () => import('../views/PatientDetail.vue'),
    meta: { title: '患者详情', hidden: true }
  },
  {
    path: '/charts',
    name: 'Charts',
    component: () => import('../views/Charts.vue'),
    meta: { title: '病历管理', icon: 'Document' }
  },
  {
    path: '/charts/:id',
    name: 'ChartDetail',
    component: () => import('../views/ChartDetail.vue'),
    meta: { title: '病历详情', hidden: true }
  },
  {
    path: '/billing',
    name: 'Billing',
    component: () => import('../views/Billing.vue'),
    meta: { title: '收费管理', icon: 'Wallet' }
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../views/Schedule.vue'),
    meta: { title: '排班管理', icon: 'Clock' }
  },
  {
    path: '/recall',
    name: 'Recall',
    component: () => import('../views/Recall.vue'),
    meta: { title: '召回管理', icon: 'Bell' }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/Statistics.vue'),
    meta: { title: '数据统计', icon: 'DataLine' }
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
