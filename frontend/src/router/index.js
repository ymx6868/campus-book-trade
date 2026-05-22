/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/BookList.vue'),
    meta: { title: '书籍列表' }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/books/:id',
    name: 'book-detail',
    component: () => import('../views/BookDetail.vue'),
    meta: { title: '书籍详情' }
  },
  {
    path: '/publish',
    name: 'publish',
    component: () => import('../views/PublishBook.vue'),
    meta: { title: '发布书籍', requireAuth: true }
  },
  {
    path: '/my-orders',
    name: 'my-orders',
    component: () => import('../views/MyOrders.vue'),
    meta: { title: '我的订单', requireAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：需要登录的页面
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title 
    ? `${to.meta.title} - 校园二手书交易平台` 
    : '校园二手书交易平台'

  // 检查是否需要登录
  if (to.meta.requireAuth) {
    const userStore = useUserStore()
    if (!userStore.isLoggedIn()) {
      next({ name: 'login' })
      return
    }
  }
  next()
})

export default router