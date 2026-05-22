# 📚 校园二手书交易平台

> 软件工程课程作业 - 人人结对编程实践

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey.svg)](https://flask.palletsprojects.com/)

---

## 📖 项目简介

一个面向高校学生的二手教材/书籍交易平台，支持卖家发布闲置书籍、买家浏览下单、用户互相留言沟通。

本项目采用**前后端分离架构**，由两人组成的结对编程小组通过 **Git Flow** 工作流协作开发。

---

## 👥 团队成员

| 角色 | 姓名 | 学号 | GitHub |
|------|------|------|--------|
| 成员A | [于孟祥] | 233428010218 | [@ymx6868](https://github.com/ymx6868) |
| 成员B | [刘钧豪] | 233428010222 | [@ASDFGHJKL8886] |

---

## 🏗️ 技术栈

### 后端
- **Python** 3.10
- **Flask** 3.0 - Web框架
- **SQLAlchemy** 2.0 - ORM
- **SQLite** - 数据库
- **JWT** - 身份认证
- **pytest** - 单元测试

### 前端
- **Vue 3** - 渐进式框架
- **Vite** - 构建工具
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端
- **Vue Router** - 路由管理

---

## 🚀 快速开始

### 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
后端运行在 http://127.0.0.1:5000

启动前端
Bash

cd frontend
npm install
npm run dev
前端运行在 http://127.0.0.1:5173

📁 项目结构
text

campus-book-trade/
├── backend/              # 后端代码（Flask）
│   ├── src/
│   │   ├── models/       # 数据模型
│   │   ├── routes/       # 路由控制器
│   │   ├── services/     # 业务逻辑
│   │   └── utils/        # 工具函数
│   ├── tests/            # 单元测试
│   ├── requirements.txt
│   └── run.py
├── frontend/             # 前端代码（Vue3）
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 通用组件
│   │   ├── api/          # API封装
│   │   └── router/       # 路由配置
│   ├── package.json
│   └── vite.config.js
├── docs/                 # 项目文档
│   ├── 1_结对编程计划.md
│   ├── 2_系统设计文档.md
│   ├── 3_角色互换日志.md
│   └── 4_部署说明.md
├── .gitignore
├── LICENSE
└── README.md
🎯 功能模块
模块	主要功能	负责人
👤 用户模块	注册、登录、JWT认证、个人资料	成员A
📚 书籍模块	发布书籍、浏览搜索、上下架管理	成员B
🛒 订单模块	下单、支付状态、订单流转	成员A
💬 留言模块	评论、回复、消息通知	成员B
🔄 Git 工作流
本项目采用 Feature Branch Workflow：

text

main (主分支)
└── develop (开发分支)
    ├── feature/user-module
    ├── feature/book-module
    ├── feature/order-module
    └── feature/comment-module
规范：

❌ 禁止直接 push 到 main 和 develop
✅ 所有改动必须通过 Pull Request
✅ PR 必须经过另一人 review 后才能合并
✅ Commit 信息遵循 Conventional Commits
详细规范见 结对编程计划。

📊 项目进度
 项目初始化
 Git 仓库与分支策略
 结对编程计划
 需求与系统设计
 后端模块开发
 前端页面开发
 集成测试
 部署与文档
📄 License
本项目基于 MIT License 开源。
