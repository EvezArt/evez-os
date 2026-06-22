---
name: automation-workflow-builder
description: 自动化工作流构建器，设计并执行跨平台自动化流程，支持触发器、条件判断、多步骤操作。
metadata:
  openclaw:
    requires:
      bins:
        - exec
        - read
        - write
        - web_fetch
---

# 自动化工作流构建器 v1.0.0

设计并执行自动化工作流，替代重复性人工操作。

## 功能特性

### 1. 触发器系统
- 定时触发（Cron）
- 文件变化触发
- API webhook 触发
- 手动触发

### 2. 条件判断
- IF/ELSE 逻辑
- 多条件组合
- 数据过滤

### 3. 操作节点
- 文件操作（读/写/移动/复制）
- 网络请求（GET/POST）
- 数据处理（转换/格式化）
- 命令执行
- 通知发送

### 4. 工作流模板
- 数据同步
- 内容发布
- 报告生成
- 监控告警

## 快速使用示例

```javascript
// 示例 1：定时抓取 + 处理 + 保存
const workflow = {
  trigger: { type: "cron", schedule: "0 */6 * * *" },
  steps: [
    { action: "fetch", url: "https://api.example.com/data" },
    { action: "transform", script: "process(data)" },
    { action: "save", path: "./output/data.json" }
  ]
}

// 示例 2：文件监控 + 自动处理
const workflow = {
  trigger: { type: "watch", path: "./inbox" },
  steps: [
    { action: "read", file: "${trigger.file}" },
    { action: "process", type: "convert" },
    { action: "move", to: "./processed" }
  ]
}

// 示例 3：多步骤数据同步
const workflow = {
  trigger: { type: "manual" },
  steps: [
    { action: "fetch", url: "source-api", output: "data1" },
    { action: "fetch", url: "another-api", output: "data2" },
    { action: "merge", inputs: ["data1", "data2"] },
    { action: "upload", destination: "cloud-storage" }
  ]
}
```

## 预置工作流模板

### 模板 1：竞品价格监控
```
触发：每天 9:00
步骤：
1. 抓取竞品网站价格
2. 与本地数据对比
3. 如有变化，发送通知
4. 保存历史记录
```

### 模板 2：内容自动发布
```
触发：新文件添加到./drafts
步骤：
1. 读取草稿内容
2. 格式化/优化
3. 发布到目标平台
4. 记录发布日志
```

### 模板 3：数据报告生成
```
触发：每周一 8:00
步骤：
1. 从多个 API 拉取数据
2. 合并、计算指标
3. 生成图表/表格
4. 导出 PDF/Excel
5. 发送邮件/消息
```

## 使用场景

1. **电商运营** - 价格监控、库存同步、订单处理
2. **内容创作** - 素材收集、格式转换、多平台发布
3. **数据分析** - 数据抓取、清洗、报告生成
4. **客户服务** - 自动回复、工单处理、反馈收集
5. **项目管理** - 进度跟踪、状态同步、提醒通知

## 定制开发

需要定制化自动化工作流、企业级集成方案？

📧 联系：careytian-ai@github

---

## 许可证

MIT-0
