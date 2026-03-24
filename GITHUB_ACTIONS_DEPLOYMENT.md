# GitHub Actions 部署指南

## 部署步骤

### 1. 推送项目到 GitHub

```bash
git add .
git commit -m "feat: add GitHub Actions workflow for daily regime report"
git push origin main
```

### 2. 配置 Secrets

进入 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**，添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|-----------|------|------|
| `TS_TOKEN` | Tushare API Token | `xxxxxxxxxxxxxxxx` |
| `EMAIL_SENDER` | 发件人邮箱（QQ/企业邮箱） | `your-email@qq.com` |
| `EMAIL_PASS` | 邮箱授权码（非密码） | `abcdefghijklmnop` |
| `EMAIL_RECEIVERS` | 收件人列表，逗号分隔 | `user1@qq.com,user2@qq.com` |
| `SMTP_SERVER` | SMTP 服务器地址 | `smtp.qq.com` |
| `SMTP_PORT` | SMTP 端口 | `465` |
| `SMTP_TIMEOUT` | SMTP 超时时间（秒） | `30` |
| `MAIL_RETRY_COUNT` | 邮件发送失败重试次数 | `3` |
| `MAIL_RETRY_DELAY_SECONDS` | 重试间隔（秒） | `5` |

### 3. 调整运行时间

编辑 `.github/workflows/daily-regime-report.yml`，修改 `cron` 表达式：

```yaml
schedule:
  - cron: '0 2 * * *'  # 北京时间 10:00（UTC 2:00）
```

**Cron 格式**：`分 小时 日 月 星期`
- `0 2 * * *` → 每天 02:00 UTC（北京时间 10:00）
- `0 10 * * *` → 每天 10:00 UTC（北京时间 18:00）
- `0 15 * * 1-5` → 工作日 15:00 UTC

### 4. 手动测试

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Daily Regime Report** 工作流
4. 点击 **Run workflow** 手动触发

## 工作流说明

- **触发方式**：
  - ✅ 定时执行：每天北京时间 10:00
  - ✅ 手动触发：Actions 页面点击运行

- **执行步骤**：
  1. 检出最新代码
  2. 安装 Python 3.10 和依赖
  3. 运行 Regime 报告任务
  4. 自动提交更新的数据文件（CSV、日志）
  5. 保留日志和报告为 Artifacts

## 常见问题

### Q: 邮件配置获取
- **QQ邮箱**：[开启SMTP](https://service.mail.qq.com/detail/0/75)，获取**授权码**（非密码）
- **企业邮箱**：联系邮箱管理员获取 SMTP 信息

### Q: Email_pass 是密码还是授权码？
**必须是授权码**，不是邮箱登录密码。

### Q: CSV 数据无法更新
确保 GitHub Actions 有提交权限：
1. 检查仓库是否为 Public（Private 需要特殊配置）
2. 检查 workflow 文件中的 `git push` 步骤

### Q: 脚本执行失败怎么办？
1. 进入 Actions 页面查看执行日志
2. 检查 Secrets 配置是否正确
3. 检查网络问题（tushare/邮件服务）

## 监控和调试

- **查看日志**：Actions 页面 → 选择工作流 → 点击运行记录 → 查看日志
- **下载输出**：Actions 页面 → 点击运行记录 → 页面下方 Artifacts 进行下载
- **禁用工作流**：Actions 页面 → 工作流文件 → 点击三点菜单 → Disable workflow

## 升级和维护

更新 `requirements.txt` 后，工作流会自动使用最新依赖。

如需修改执行逻辑，编辑 `main.py` 并推送代码，工作流会自动使用新版本。
