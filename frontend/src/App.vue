<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header v-if="showHeader" class="header">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            📚 校园二手书交易平台
          </div>
          <div class="nav-menu">
            <el-button text @click="$router.push('/')">书籍列表</el-button>
            <template v-if="userStore.token">
              <el-button text @click="$router.push('/publish')">发布书籍</el-button>
              <el-button text @click="$router.push('/my-orders')">我的订单</el-button>
              <el-dropdown @command="handleCommand">
                <span class="user-info">
                  👤 {{ userStore.user?.username }}
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button text @click="$router.push('/login')">登录</el-button>
              <el-button type="primary" @click="$router.push('/register')">注册</el-button>
            </template>
          </div>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from './stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 登录/注册页不显示导航栏
const showHeader = computed(() => {
  return !['login', 'register'].includes(route.name)
})

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  color: #409eff;
}

.nav-menu {
  display: flex;
  gap: 15px;
  align-items: center;
}

.user-info {
  cursor: pointer;
  color: #606266;
}
</style>