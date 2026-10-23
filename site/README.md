# 产品站点使用说明

## 本地预览

```powershell
cd C:\Users\Lenovo\pro2\new_day\site
py -m http.server 8080
```

浏览器打开 `http://127.0.0.1:8080`。

## 部署（免费方案）

完整的 GitHub Pages 步骤（含手机号/Token 安全说明）见根目录 `DEPLOY_GITHUB_PAGES.md`。

任选其一：

1. **GitHub Pages 网页上传**：新建仓库，把 `site/` 里的内容上传到仓库根目录，Settings → Pages → Deploy from a branch → main / root。
2. **GitHub Pages + Actions**：推送整个仓库，Settings → Pages → Source 选 GitHub Actions；`.github/workflows/pages.yml` 会自动发布 `site/`。
3. **Cloudflare Pages**：新建项目，上传 `site/` 目录，构建命令留空。
4. **Netlify**：拖拽 `site/` 目录到 Netlify Drop。

部署后把域名填到知乎/公众号/闲鱼简介里（如果平台允许）。

## 需要替换的内容

- 品牌名“车链出海情报”：可全局替换为你的品牌。
- 闲鱼店铺名：当前写的是“车链出海情报”，上架后改成你的实际店铺名。
- 知乎/公众号名称：改成你的实际账号。
- 示例来源链接：保留即可，都是公开来源；如失效，替换成新的公开链接。

## 样本文件

`site/assets/` 下是当前样本：

- `sample-australia.pdf` / `.xlsx`
- `sample-brazil.pdf` / `.xlsx`

每月更新数据后，重新生成样本并覆盖这些文件。样本已脱敏，不含个人信息。

## 合规检查

- 页面明确“标准包不含联系方式”。
- 页面明确“不承诺成交、不构成投资建议”。
- 不收集表单、不埋点、不存个人信息。
- 如来源方要求删除，按 `sales/templates/delivery.md` 的流程处理。

## 设计说明

- 深色背景 + 金色强调，和商品封面一致。
- 首屏先给样本，再给定价；降低信任门槛。
- 移动端 390px 宽度下可正常阅读，表格横向滚动。
- 无外部字体/JS 依赖，加载快、易部署。
