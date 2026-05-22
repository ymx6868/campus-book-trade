/**
 * 留言相关 API
 */
import request from './request'

// 获取某本书的留言列表
export const getComments = (bookId) => {
  return request.get(`/api/books/${bookId}/comments`)
}

// 发表留言（含回复，传parent_id）
export const createComment = (bookId, data) => {
  return request.post(`/api/books/${bookId}/comments`, data)
}

// 删除留言
export const deleteComment = (id) => {
  return request.delete(`/api/comments/${id}`)
}

// 获取我的留言
export const getMyComments = () => {
  return request.get('/api/comments/my')
}