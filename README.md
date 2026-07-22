# AI 监课系统

AI-powered classroom monitoring system for psychology education companies.

## 项目背景

心理学行业教育培训公司，安排外聘老师进行小班制网上直播授课。过去由课程运营人员以官方身份旁听考核老师（出勤、教纲执行、软件操作、学生互动等），称为"监课"。随着业务扩张，运营人手不足，需用 AI 自动完成监课流程。

## 核心目标

通过网络直播平台的 API/回调获取成员进出、逐字稿、评论区明细，结合企业内部教纲和咨询师授课行为手册，自动计算以下维度的分数：

- 老师出勤情况
- 老师授课专业度
- 课堂活跃度
- 软件使用熟练度

最终输出每场课的综合评分，形成后台看板，并对低分场次通过飞书机器人实时通知对应运营群。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11, FastAPI |
| 数据库 | PostgreSQL (SQLAlchemy 2.0 + Alembic) |
| 飞书集成 | 飞书机器人 Webhook |
| 缓存/队列 | Redis + Celery |
| 部署 | Docker Compose |
| 看板前端 | HTML/CSS/JS (dashboard.html) |

## 目录结构

```
ai-monitor-app/
├── alembic/              # 数据库迁移
├── app/
│   ├── api/v1/           # FastAPI 路由
│   │   ├── live_sessions.py
│   │   ├── evaluations.py
│   │   ├── alerts.py
│   │   ├── alert_configs.py
│   │   ├── member_events.py
│   │   ├── transcripts.py
│   │   ├── comments.py
│   │   └── operators.py
│   ├── core/             # 配置与数据库
│   │   ├── config.py
│   │   └── database.py
│   ├── models/           # SQLAlchemy 模型
│   │   ├── live_session.py
│   │   ├── member_event.py
│   │   ├── transcript.py
│   │   ├── comment.py
│   │   ├── syllabus.py
│   │   ├── behavior_rule.py
│   │   ├── evaluation_result.py
│   │   ├── alert.py
│   │   ├── alert_config.py
│   │   └── operator.py
│   ├── schemas/          # Pydantic 模型
│   ├── services/         # 业务逻辑
│   │   ├── attendance_scorer.py
│   │   ├── professionalism_scorer.py
│   │   ├── engagement_scorer.py
│   │   ├── software_scorer.py
│   │   ├── evaluation_engine.py
│   │   └── feishu_notifier.py
│   ├── tasks/            # Celery 异步任务
│   ├── main.py           # FastAPI 入口
│   └── dashboard.html    # 后台看板页面
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 数据模型

| 表名 | 说明 |
|------|------|
| `live_sessions` | 直播场次 |
| `member_events` | 成员进出记录 |
| `transcripts` | 逐字稿 |
| `comments` | 评论 |
| `syllabus` | 教纲大纲 |
| `behavior_rules` | 行为规范 |
| `evaluation_results` | 评分结果 |
| `alerts` | 预警记录 |
| `alert_configs` | 预警配置 |
| `operators` | 运营人员 |

## 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 出勤 | 20% | 迟到/早退扣分 |
| 专业度 | 40% | 知识点覆盖 + 违规词检测 |
| 活跃度 | 20% | 学生评论/发言/提问 |
| 熟练度 | 20% | 屏幕共享/拉人上麦/异常事件 |

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/yuzequan/Ai_Project.git
cd Ai_Project/ai-monitor-app

# 2. 启动开发环境
docker-compose up -d

# 3. 执行数据库迁移
alembic upgrade head

# 4. 启动服务
uvicorn app.main:app --reload --port 8000

# 5. 打开看板
# http://localhost:8000/app/dashboard.html
```

## API 概览

| 端点 | 说明 |
|------|------|
| `GET /api/v1/live-sessions` | 直播场次列表 |
| `GET /api/v1/live-sessions/{id}` | 场次详情 |
| `POST /api/v1/evaluations/{id}/run` | 手动触发评分 |
| `GET /api/v1/evaluations/stats` | 评分统计 |
| `GET /api/v1/alerts` | 预警记录 |
| `POST /api/v1/alert-configs` | 创建预警配置 |
| `GET /api/v1/operators` | 运营人员管理 |

## 飞书集成

1. 在 `alert_configs` 表中配置飞书群 webhook 地址
2. 设置 `FEISHU_WEBHOOK` 环境变量
3. 评分低于阈值时自动发送飞书消息卡片

## License

MIT
