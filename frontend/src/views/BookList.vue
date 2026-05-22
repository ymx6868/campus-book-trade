<template>
  <div class="book-list-container">
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索书名..."
        size="large"
        clearable
        @keyup.enter="handleSearch"
        @clear="handleSearch"
        style="width: 400px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" size="large" @click="handleSearch">
        搜索
      </el-button>
    </div>

    <div v-loading="loading">
      <div v-if="books.length === 0 && !loading" class="empty">
        <el-empty description="暂无置闲书籍" />
      </div>

      <div v-else class="book-grid">
        <el-card
          v-for="book in books"
          :key="book.id"
          class="book-card"
          shadow="hover"
          @click="goDetail(book.id)"
        >
          <div class="book-cover">📖</div>
          <div class="book-info">
            <h3 class="book-title">{{ book.title }}</h3>
            <p class="book-author" v-if="book.author">
              作者：{{ book.author }}
            </p>
            <div class="book-meta">
              <el-tag :type="getConditionType(book.condition)" size="small">
                {{ getConditionLabel(book.condition) }}
              </el-tag>
              <el-tag v-if="book.status === 'sold'" type="info" size="small">
                已售出
              </el-tag>
              <el-tag v-else-if="book.status === 'on_sale'" type="success" size="small">
                在售
              </el-tag>
            </div>
            <div class="book-price">
              ¥{{ book.price }}
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { getBooks } from '../api/book'

const router = useRouter()
const books = ref([])
const loading = ref(false)
const searchKeyword = ref('')

const loadBooks = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    const resp = await getBooks(params)
    books.value = resp.books || resp || []
  } catch (error) {
    console.error('加载书籍失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadBooks()
}

const goDetail = (id) => {
  router.push(`/books/${id}`)
}

const getConditionType = (condition) => {
  const map = {
    'new': 'danger',
    'like_new': 'success',
    'good': 'primary',
    'fair': 'warning',
    'poor': 'info'
  }
  return map[condition] || 'info'
}

const getConditionLabel = (condition) => {
  const map = {
    'new': '全新',
    'like_new': '九成新',
    'good': '八成新',
    'fair': '七成新',
    'poor': '较旧'
  }
  return map[condition] || condition
}

onMounted(() => {
  loadBooks()
})
</script>

<style scoped>
.book-list-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.search-bar { display: flex; gap: 10px; margin-bottom: 30px; justify-content: center; }
.empty { margin: 60px 0; }
.book-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.book-card { cursor: pointer; transition: transform 0.2s; text-align: left; }
.book-card:hover { transform: translateY(-4px); }
.book-cover { height: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 60px; border-radius: 4px; margin-bottom: 12px; }
.book-info { padding: 4px 0; }
.book-title { font-size: 16px; margin: 0 0 8px; color: #303133; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.book-author { font-size: 12px; color: #909399; margin: 0 0 8px; }
.book-meta { display: flex; gap: 6px; margin-bottom: 10px; }
.book-price { font-size: 20px; font-weight: bold; color: #f56c6c; }
</style>