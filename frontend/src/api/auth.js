/**
 * 用户认证相关 API
 */
import request from './request'

// 注册
export const register = (data) => {
  return request.post('/api/auth/register', data)
}

// 登录
export const login = (data) => {
  return request.post('/api/auth/login', data)
}

// 获取个人资料
export const getProfile = () => {
  return request.get('/api/auth/profile')
}

// 更新个人资料
export const updateProfile = (data) => {
  return request.put('/api/auth/profile', data)
}