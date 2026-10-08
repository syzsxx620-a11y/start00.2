# ExportMall — 外贸电商平台（初版）

一个用 Python / Django 构建的外贸（跨境出口）电商平台初版。面向海外买家：多币种显示、国际运费、商品目录、购物车、下单、订单追踪，以及后台管理。

## 技术栈

- **Python 3.12** / **Django 5.x**
- **SQLite**（初版零配置，生产可切换 PostgreSQL）
- Django 自带 Admin 作为后台管理
- Pillow（商品图片处理）

## 功能清单（初版）

| 模块 | 说明 |
| --- | --- |
| 商品目录 | 分类、商品（SKU/价格/库存/描述/多图）、搜索、排序 |
| 多币种 | USD / EUR / CNY / GBP，汇率可在后台编辑，前台一键切换 |
| 购物车 | 基于会话的购物车，增删改数量 |
| 下单结算 | 国际收货地址（含国家/州/邮编），国际运费（满额包邮） |
| 订单管理 | 下单扣库存、订单号、订单状态、后台处理（发货/送达） |
| 订单追踪 | 顾客用「订单号 + 邮箱」自助查询订单 |
| 后台管理 | Django Admin 管理商品/分类/汇率/订单 |

## 快速开始

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
# Windows 激活：
.venv\Scripts\activate
pip install -r requirements.txt

# 2. 生成数据库表
python manage.py migrate

# 3. 导入演示数据（币种、分类、示例商品）
python manage.py seed_demo

# 4. 创建后台管理员账号
python manage.py createsuperuser

# 5. 启动开发服务器
python manage.py runserver
```

访问：
- 前台商城：http://127.0.0.1:8000/
- 后台管理：http://127.0.0.1:8000/admin/

## 关键说明

- **基础货币为 USD**：商品价格、订单金额都以 USD 记录；前台按所选货币显示（`products.Currency` 汇率可后台修改）。
- **运费**：`config/settings.py` 中 `SHIPPING_FLAT_RATE_USD`（默认 $20）与 `FREE_SHIPPING_THRESHOLD_USD`（满 $200 包邮）可调整。
- **商品图片**：演示商品不带图片（前端显示占位图），可在后台为商品上传图片。

## 目录结构

```
project002/
├── config/          # 项目配置（settings/urls/wsgi/asgi）
├── apps/
│   ├── core/        # 首页、多币种切换、模板标签
│   ├── products/    # 商品、分类、汇率
│   ├── cart/        # 购物车
│   └── orders/      # 订单、结算、追踪
├── templates/       # 前端模板
├── static/          # 静态资源（CSS）
└── manage.py
```

## 下一步建议（生产化方向）

- 用户注册/登录（Django auth），订单历史绑定账号
- PostgreSQL 替代 SQLite；缓存、静态文件走 CDN
- 支付接入（Stripe / PayPal / 信用卡），订单回调
- 多语言（i18n + 翻译文件），物流 API（运费计算、面单、追踪）
- 税率/关税估算、B2B 批发询价、多仓库库存
- 邮件通知（下单/发货）、HTTPS 与密钥安全配置
