/**
 * 订单相关 API
 */
import request from './request'

// 创建订单
export const createOrder = (data) => {
  return request.post('/api/orders', data)
}

// 获取订单列表（role=buyer|seller）
export const getOrders = (params) => {
  return request.get('/api/orders', { params })
}

// 获取订单详情
export const getOrder = (id) => {
  return request.get(`/api/orders/${id}`)
}

// 更新订单状态
export const updateOrderStatus = (id, status) => {
  return request.patch(`/api/orders/${id}/status`, { status })
}