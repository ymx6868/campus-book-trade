/**
 * 书籍相关 API
 */
import request from './request'

// 获取书籍列表
export const getBooks = (params) => {
  return request.get('/api/books', { params })
}

// 获取书籍详情
export const getBook = (id) => {
  return request.get(`/api/books/${id}`)
}

// 发布书籍
export const createBook = (data) => {
  return request.post('/api/books', data)
}

// 修改书籍
export const updateBook = (id, data) => {
  return request.put(`/api/books/${id}`, data)
}

// 下架书籍
export const deleteBook = (id) => {
  return request.delete(`/api/books/${id}`)
}