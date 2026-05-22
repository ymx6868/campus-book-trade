<template>
  <div class="publish-container">
    <el-card class="publish-card">
      <template #header>
        <div class="card-header">
          <h2>✍️ 发布置闲二手书籍</h2>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" size="large">
        <el-form-item label="书籍名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入完整、规范的书籍名称" />
        </el-form-item>

        <el-form-item label="书籍作者" prop="author">
          <el-input v-model="form.author" placeholder="请输入书籍作者" />
        </el-form-item>

        <el-form-item label="期望售价" prop="price">
          <el-input-number v-model="form.price" :precision="2" :step="1" :min="0.01" style="width: 180px" />
          <span style="margin-left: 10px; color: #909399; font-size: 13px;">元</span>
        </el-form-item>

        <el-form-item label="品相成色" prop="condition">
          <el-select v-model="form.condition" placeholder="请选择新旧程度" style="width: 180px">
            <el-option label="全新" value="new" />
            <el-option label="九成新" value="like_new" />
            <el-option label="八成新" value="good" />
            <el-option label="七成新" value="fair" />
            <el-option label="较旧" value="poor" />
          </el-select>
        </el-form-item>

        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="写一下书本细节（如：有没有做过笔记、在哪里面交等），有助于更快卖出哦~"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handlePublish">确认上架发布</el-button>
          <el-button @click="router.push('/')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createBook } from '../api/book'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  title: '',
  author: '',
  price: 10.00,
  condition: 'good',
  description: ''
})

const rules = {
  title: [
    { required: true, message: '书名是必填项', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入售卖价格', trigger: 'blur' }
  ],
  condition: [
    { required: true, message: '请选择新旧标签', trigger: 'change' }
  ]
}

const handlePublish = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await createBook(form)
      ElMessage.success('恭喜你，书籍上架成功！')
      router.push('/')
    } catch (e) {
      console.error(e)
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.publish-container { max-width: 700px; margin: 40px auto; padding: 0 20px; text-align: left; }
.publish-card { border-radius: 8px; }
.card-header h2 { margin: 0; font-size: 20px; color: #303133; }
</style>