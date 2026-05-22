<template>
  <div class="book-detail-container" v-loading="loading">
    <div v-if="book" class="detail-layout">
      <el-row :gutter="40">
        <el-col :xs="24" :sm="10">
          <div class="book-cover">📖</div>
        </el-col>
        <el-col :xs="24" :sm="14" class="info-side">
          <h1 class="book-title">{{ book.title }}</h1>
          
          <div class="price-bar">
            <span class="price-label">转让价</span>
            <span class="price-num">¥{{ book.price }}</span>
          </div>

          <div class="meta-list">
            <p><strong>作者：</strong>{{ book.author || '未知' }}</p>
            <p>
              <strong>品相成色：</strong>
              <el-tag :type="getConditionType(book.condition)">
                {{ getConditionLabel(book.condition) }}
              </el-tag>
            </p>
            <p>
              <strong>状态：</strong>
              <el-tag :type="getStatusType(book.status)">
                {{ getStatusLabel(book.status) }}
              </el-tag>
            </p>
            <p><strong>卖家：</strong>{{ book.seller_name || '热心校友' }}</p>
            <p><strong>发布时间：</strong>{{ formatDate(book.created_at) }}</p>
          </div>

          <div class="description-box">
            <h4>💡 书籍简介与描述：</h4>
            <p>{{ book.description || '主人很懒，什么都没有写~' }}</p>
          </div>

          <div class="action-bar">
            <template v-if="book.status === 'on_sale'">
              <template v-if="isSeller">
                <el-button type="warning" size="large" icon="Edit" disabled>修改信息</el-button>
                <el-button 
                  type="danger" 
                  size="large" 
                  icon="Delete" 
                  :loading="submittingDelete"
                  @click="handleDelete"
                >
                  下架商品
                </el-button>
              </template>
              <template v-else>
                <el-button 
                  type="danger" 
                  size="large" 
                  icon="ShoppingCart"
                  :loading="submittingOrder"
                  @click="handleBuy"
                >
                  立即购买
                </el-button>
              </template>
            </template>
            
            <el-button v-else type="info" size="large" disabled>
              {{ book.status === 'sold' ? '该书已售罄' : '该商品已下架' }}
            </el-button>
            
            <el-button size="large" @click="router.push('/')">返回列表</el-button>
          </div>
        </el-col>
      </el-row>

      <el-divider />

      <div class="comment-section">
        <h3>💬 校园校友留言问答</h3>
        
        <div class="comment-input-box">
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="3"
            placeholder="对书本成色、交易地点有疑问？在这里给卖家留言吧..."
            maxlength="200"
            show-word-limit
          />
          <div class="submit-comment-btn">
            <el-button type="primary" :disabled="!newComment.trim()" @click="submitComment">
              发表留言
            </el-button>
          </div>
        </div>

        <div v-if="comments.length === 0" class="no-comment">
          暂无留言，快来抢沙发吧~
        </div>
        <div v-else class="comment-list">
          <div v-for="item in comments" :key="item.id" class="comment-item">
            <div class="comment-user-info">
              <span class="username">{{ item.user_name || item.user?.username || '匿名同学' }}</span>
              <span class="time">{{ formatDate(item.created_at) }}</span>
            </div>
            <div class="comment-content">
              {{ item.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBook, deleteBook } from '../api/book'
import { getComments, createComment } from '../api/comment'
import { createOrder } from '../api/order'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const bookId = route.params.id
const book = ref(null)
const comments = ref([])
const loading = ref(false)
const submittingOrder = ref(false)
const submittingDelete = ref(false)
const newComment = ref('')

// 严格判断当前登录用户是不是卖家本人
const isSeller = computed(() => {
  if (!userStore.user || !book.value) return false
  return userStore.user.id === book.value.seller_id || userStore.user.username === book.value.seller_name
})

const loadData = async () => {
  loading.value = true
  try {
    const resp = await getBook(bookId)
    book.value = resp.book || resp
    
    const commentResp = await getComments(bookId)
    comments.value = commentResp.comments || commentResp || []
  } catch (error) {
    console.error('获取详情页失败:', error)
  } finally {
    loading.value = false
  }
}

// 卖家下架商品逻辑
const handleDelete = () => {
  ElMessageBox.confirm(`确定要下架《${book.value.title}》吗？下架后同学们将无法在首页浏览和购买。`, '提示', {
    confirmButtonText: '确定下架',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    submittingDelete.value = true
    try {
      await deleteBook(book.value.id)
      ElMessage.success('商品下架成功！')
      router.push('/')
    } catch (e) {
      console.error(e)
    } finally {
      submittingDelete.value = false
    }
  }).catch(() => {})
}

const handleBuy = () => {
  if (!userStore.token) {
    ElMessage.warning('请先登录后再进行购买！')
    router.push('/login')
    return
  }
  
  ElMessageBox.confirm(`确认以 ¥${book.value.price} 的价格购买《${book.value.title}》吗？`, '确认订单', {
    confirmButtonText: '确认下单',
    cancelButtonText: '取消',
    type: 'success'
  }).then(async () => {
    submittingOrder.value = true
    try {
      await createOrder({ book_id: book.value.id })
      ElMessage.success('下单成功！正在转跳到订单页...')
      router.push('/my-orders')
    } catch (e) {
      console.error(e)
    } finally {
      submittingOrder.value = false
    }
  }).catch(() => {})
}

const submitComment = async () => {
  if (!userStore.token) {
    ElMessage.warning('登录后即可参与留言讨论')
    router.push('/login')
    return
  }
  try {
    await createComment(bookId, { content: newComment.value })
    ElMessage.success('留言成功！')
    newComment.value = ''
    loadData()
  } catch (e) {
    console.error(e)
  }
}

const getConditionType = (c) => {
  return { 'new': 'danger', 'like_new': 'success', 'good': 'primary', 'fair': 'warning', 'poor': 'info' }[c] || 'info'
}
const getConditionLabel = (c) => {
  return { 'new': '全新', 'like_new': '九成新', 'good': '八成新', 'fair': '七成新', 'poor': '较旧' }[c] || c
}
const getStatusType = (s) => {
  return { 'on_sale': 'success', 'sold': 'info', 'off_shelf': 'danger' }[s] || 'info'
}
const getStatusLabel = (s) => {
  return { 'on_sale': '在售', 'sold': '已售出', 'off_shelf': '已下架' }[s] || s
}
const formatDate = (str) => {
  if (!str) return ''
  return new Date(str).toLocaleString()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.book-detail-container { max-width: 1000px; margin: 30px auto; padding: 20px; text-align: left; }
.book-cover { height: 260px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 100px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.info-side { display: flex; flex-direction: column; justify-content: space-between; }
.book-title { margin-top: 0; font-size: 24px; color: #303133; }
.price-bar { background-color: #fef0f0; padding: 12px; border-radius: 6px; margin: 10px 0; }
.price-label { color: #f56c6c; font-size: 14px; margin-right: 10px; }
.price-num { color: #f56c6c; font-size: 26px; font-weight: bold; }
.meta-list p { margin: 6px 0; font-size: 14px; color: #606266; }
.description-box { margin-top: 15px; background: #f4f4f5; padding: 12px; border-radius: 6px; }
.description-box h4 { margin: 0 0 6px 0; color: #303133; }
.description-box p { margin: 0; font-size: 14px; color: #606266; line-height: 1.6; }
.action-bar { margin-top: 20px; display: flex; gap: 15px; }
.comment-section { margin-top: 40px; }
.comment-input-box { margin-bottom: 25px; }
.submit-comment-btn { display: flex; justify-content: flex-end; margin-top: 10px; }
.comment-item { border-bottom: 1px solid #ebeef5; padding: 15px 0; }
.comment-user-info { display: flex; gap: 15px; font-size: 13px; margin-bottom: 6px; }
.comment-user-info .username { font-weight: bold; color: #409eff; }
.comment-user-info .time { color: #909399; }
.comment-content { font-size: 14px; color: #303133; }
.no-comment { text-align: center; color: #909399; padding: 20px 0; }
</style>