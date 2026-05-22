/**
 * Axios 封装：统一处理请求和响应
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  timeout: 10000
})

// 请求拦截器：自动添加Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.error || '请求失败'

    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 延迟跳转，让用户看到提示
      setTimeout(() => {
        window.location.href = '/login'
      }, 1000)
    } else {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  }
)

export default request