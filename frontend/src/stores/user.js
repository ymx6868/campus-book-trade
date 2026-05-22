/**
 * 用户状态管理（Pinia）
 * 存储登录token和用户信息
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 从localStorage恢复登录状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // 设置登录状态
  const setLogin = (newToken, newUser) => {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  // 退出登录
  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 检查是否登录
  const isLoggedIn = () => {
    return !!token.value
  }

  return {
    token,
    user,
    setLogin,
    logout,
    isLoggedIn
  }
})