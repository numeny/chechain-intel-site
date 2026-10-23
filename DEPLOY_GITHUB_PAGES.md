# 部署到 GitHub Pages

## 先回答：需要手机号吗？

**我不需要你的手机号、密码、验证码、GitHub Token 或 SSH 私钥。** 请不要把这些发到聊天里。

你只需要自己有一个 GitHub 账号。GitHub 在注册、异地登录或开启 2FA 时，可能要求你验证邮箱，偶尔会要求手机验证——那是你和 GitHub 之间的操作，你在 GitHub 页面上完成即可。部署本身不需要手机号。

## 你需要准备什么

- 一个 GitHub 账号（没有就注册：https://github.com/signup）
- 一个仓库名，例如 `chechain-intel-site`（建议 public）
- 本仓库里的 `site/` 目录（已包含产品页、样本、封面、演示数据）
- 可选：自定义域名（不需要也能用 `https://<用户名>.github.io/<仓库名>/`）

## 方式 A：网页上传（最简单，不需要命令行）

适合不想装 Git、不想配 Token 的情况。

1. 登录 GitHub，点右上角 **+ → New repository**。
2. 仓库名填 `chechain-intel-site`，选择 **Public**，不要勾选 “Add a README file”，点 **Create repository**。
3. 在空仓库页面点 **uploading an existing file**。
4. 打开本机的 `C:\Users\Lenovo\pro2\new_day\site\`，把**里面的内容**拖进上传框：
   - `index.html`
   - `styles.css`
   - `script.js`
   - `favicon.svg`
   - `.nojekyll`
   - `assets/`（封面 + 样本 PDF/Excel）
   - `data/`（在线筛选演示数据）
   - `README.md`
   
   **注意：拖 `site` 文件夹里面的内容，不要拖 `site` 文件夹本身。** 否则 Pages 根目录会变成 `/site/`，访问路径不对。
5. 下方 Commit changes 填一句 `deploy site`，点 **Commit changes**。
6. 进入仓库 **Settings → Pages**。
7. **Build and deployment → Source** 选 **Deploy from a branch**。
8. **Branch** 选 `main`，文件夹选 **/ (root)**，点 **Save**。
9. 等 1-2 分钟，刷新 Pages 页面，会显示：
   `https://<你的用户名>.github.io/chechain-intel-site/`
10. 打开链接，检查首页、在线筛选、样本 PDF 下载、手机端显示。

如果仓库名取为 `<你的用户名>.github.io`，访问地址就是 `https://<你的用户名>.github.io/`。

## 方式 B：Git 推送 + GitHub Actions（推荐，后续更新方便）

本仓库已包含 `.github/workflows/pages.yml`，会把 `site/` 自动发布到 Pages。

1. 在 GitHub 新建 public 仓库，例如 `chechain-intel`，不要初始化 README。
2. 在本机终端执行：

```powershell
cd C:\Users\Lenovo\pro2\new_day
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

3. 第一次 push 时，Git Credential Manager 会弹出 GitHub 登录窗口，按提示在浏览器登录/授权即可。**不要把弹出的 Token 发给我。**
4. 打开 GitHub 仓库 **Settings → Pages**。
5. **Build and deployment → Source** 选 **GitHub Actions**。
6. 打开 **Actions** 标签，等待 `Deploy product site to GitHub Pages` 跑完。
7. 在 Actions 的部署记录里点开 `deploy` job，页面会显示 `page_url`，即：
   `https://<你的用户名>.github.io/<仓库名>/`

以后修改 `site/` 后，只要：

```powershell
git add site
git commit -m "update site"
git push
```

Actions 会自动重新部署。

## 方式 C：只上传站点到独立仓库（不用 Actions）

1. 新建 public 仓库，例如 `chechain-intel-site`。
2. 把 `site/` 里的内容复制到一个临时目录，初始化 Git 并推送：

```powershell
cd C:\Users\Lenovo\pro2\new_day
Copy-Item -Recurse site C:\Users\Lenovo\AppData\Local\Temp\chechain-site
cd C:\Users\Lenovo\AppData\Local\Temp\chechain-site
git init -b main
git add .
git commit -m "deploy site"
git remote add origin https://github.com/<你的用户名>/chechain-intel-site.git
git push -u origin main
```

3. GitHub 仓库 **Settings → Pages → Deploy from a branch → main → / (root) → Save**。
4. 等 1-2 分钟访问 `https://<你的用户名>.github.io/chechain-intel-site/`。

## 方式 D：不想用 GitHub

也可以把 `site/` 目录拖到以下免费静态托管：

- **Cloudflare Pages**：Create project → Direct Upload → 上传 `site/` 目录。
- **Netlify Drop**：https://app.netlify.com/drop → 拖拽 `site/` 目录，生成临时网址；登录后可保留。
- **Vercel**：New Project → 导入静态目录。

这些方式同样不需要把手机号给我；账号注册/验证由你完成。

## 部署前检查

- [ ] 只上传 `site/` 的内容，不上传 `deliverables/`、`sales/ops/crm.csv`、客户数据、完整付费数据。
- [ ] `site/assets/` 里的样本是脱敏样本，不含个人信息。
- [ ] `site/data/demo-data.js` 是 40 条演示数据，不是完整库。
- [ ] 页面里的“车链出海情报”可改成你的品牌名。
- [ ] 页面里的闲鱼/知乎/公众号名称，改成你的实际账号。

## 部署后检查

- [ ] 首页能打开，样式正常。
- [ ] “在线筛选”能按国家/品牌/州过滤，点“查看更多”能加载更多。
- [ ] 澳洲/巴西样本 PDF 能下载。
- [ ] 手机宽度下导航、定价、表格正常。
- [ ] 把网址填到知乎/公众号简介、闲鱼商品详情（如果平台允许）。

## 常见问题

**打开是 404**
- Pages 还没启用，或分支/目录选错；回到 Settings → Pages 检查。
- 如果上传了 `site` 文件夹本身，根目录会是 `/site/`，把内容移到仓库根目录再提交。

**页面没有样式**
- `styles.css` 没上传，或路径不对；确认 `styles.css` 在仓库根目录。

**在线筛选是空的**
- `data/demo-data.js` 没上传，或浏览器禁用了 JS；检查文件是否存在。

**样本 PDF 404**
- `assets/` 没上传，或文件名不一致；确认 `assets/sample-australia.pdf`、`assets/sample-brazil.pdf` 存在。

**Actions 失败**
- Settings → Pages → Source 必须选 **GitHub Actions**。
- 仓库必须是 public（私有仓库的 Pages 需要付费计划）。
- 检查 Actions 日志里的权限错误；本仓库已配置 `pages: write` 和 `id-token: write`。

## 安全提醒

- 不要把 GitHub 密码、验证码、PAT、SSH 私钥发给我或任何人。
- 如果必须用 PAT，只给它最小权限（`repo` + `workflow`），用完可撤销。
- GitHub Pages 是公开站点；不要把完整付费数据、客户名单、CRM 放进去。
