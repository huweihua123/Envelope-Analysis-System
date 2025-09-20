import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/experiment-types',
    name: 'ExperimentTypes',
    component: () => import('../views/ExperimentTypes.vue')
  },
  {
    path: '/experiment-types/create',
    name: 'CreateExperimentType',
    component: () => import('../views/CreateExperimentType.vue')
  },
  {
    path: '/upload/:id',
    name: 'Upload',
    component: () => import('../views/Upload.vue'),
    props: true
  },
  {
    path: '/data-management/:id',
    name: 'DataManagement',
    component: () => import('../views/DataManagement.vue'),
    props: true
  },
  {
    path: '/envelope/:id',
    name: 'EnvelopeAnalysis',
    component: () => import('../views/EnvelopeAnalysis.vue'),
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
