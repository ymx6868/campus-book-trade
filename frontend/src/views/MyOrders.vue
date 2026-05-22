<template>
  <div class="orders-container">
    <h2>📦 交易订单中心</h2>
    
    <el-tabs v-model="activeTab" @tab-change="handleTabChange" type="border-card" class="order-tabs">
      <el-tab-pane label="🛒 我买到的书籍" name="buyer">
        <el-table v-loading="loading" :data="orders" style="width: 100%">
          <el-table-column label="书籍" width="220">
            <template #default="scope">
              <strong>📖 {{ scope.row.book?.title || '未知书籍' }}</strong>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="120">
            <template #default="scope">
              <span class="price-text">¥{{ scope.row.amount }}</span>
            </template>
          </el-table-column>
          <el-table-column label="交易单号" prop="id" width="100" />
          <el-table-column label="下单时间" width="180">
            <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="交易状态">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusLabel(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="💰 我卖出的书籍" name="seller">
        <el-table v-loading="loading" :data="orders" style="width: 100%">
          <el-table-column label="被购书籍" width="220">
            <template #default="scope">
              <strong>📖 {{ scope.row.book?.title || '未知书籍' }}</strong>
            </template>
          </el-table-column>
          <el-table-column label="应收款" width="120">
            <template #default="scope">
              <span class="price-text">¥{{ scope.row.amount }}</span>
            </template>
          </el-table-column>
          <el-table-column label="订单时间" width="180">
            <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="订单状态" width="130">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusLabel(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button
                v-if="scope.row.status === 'pending'"
                type="success"
                size="small"
                @click="changeStatus(scope.row.id, 'completed')"
              >
                确认交付
              </el-button>
              <span v-else style="color: #909399; font-size: 13px;">完成</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getOrders, updateOrderStatus } from '../api/order'

const activeTab = ref('buyer')
const orders = ref([])
const loading = ref(false)

const loadOrders = async () => {
  loading.value = true
  try {
    const resp = await getOrders({ role: activeTab.value })
    orders.value = resp.orders || resp || []
  } catch (e) {
    console.error('加载订单失败:', e)
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  orders.value = []
  loadOrders()
}

const changeStatus = async (orderId, targetStatus) => {
  try {
    await updateOrderStatus(orderId, targetStatus)
    ElMessage.success('状态更新成功！')
    loadOrders()
  } catch (e) {
    console.error(e)
  }
}

const getStatusType = (s) => {
  return { 'pending': 'warning', 'completed': 'success', 'cancelled': 'info' }[s] || 'primary'
}
const getStatusLabel = (s) => {
  return { 'pending': '待面交', 'completed': '交易已完成', 'cancelled': '已取消' }[s] || s
}
const formatDate = (str) => {
  if (!str) return ''
  return new Date(str).toLocaleString()
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-container { max-width: 1100px; margin: 30px auto; padding: 0 20px; text-align: left; }
.orders-container h2 { color: #303133; margin-bottom: 20px; }
.order-tabs { box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05); }
.price-text { color: #f56c6c; font-weight: bold; }
</style>