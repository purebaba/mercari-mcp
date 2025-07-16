# Mercari MCP 服务器

一个用于搜索Mercari商品的MCP（Model Context Protocol）智能体工具。

## 功能特性

- 🔍 **关键词搜索**：根据关键词搜索Mercari商品
- 📋 **商品详情**：获取特定商品的详细信息
- 🏷️ **分类搜索**：按商品分类进行搜索
- 💰 **价格筛选**：支持价格范围过滤
- 📦 **状态筛选**：根据商品状态筛选
- 📊 **排序选项**：支持多种排序方式
- 🔄 **分页浏览**：支持分页查看搜索结果

## 依赖项

- Python 3.8+
- MCP SDK
- mercapi
- pydantic
- httpx

## 安装

1. 克隆项目：
```bash
git clone <repository-url>
cd mercari-mcp
```

2. 安装依赖：
```bash
pip install -e .
```

或者使用虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # 在Windows上使用: .venv\Scripts\activate
pip install -e .
```

## 使用方法

### 作为MCP服务器运行

#### 1. stdio模式（标准输入输出）

```bash
python -m mercari_mcp.server
```

#### 2. SSE模式（Server-Sent Events）

```bash
python scripts/run_sse_server.py
```

或者指定端口和主机：

```bash
python scripts/run_sse_server.py --host 127.0.0.1 --port 8000
```

SSE模式提供以下端点：
- 🏠 服务器地址: http://127.0.0.1:8000
- 📡 SSE端点: http://127.0.0.1:8000/sse
- 🛠️ 工具列表: http://127.0.0.1:8000/tools
- 🔧 调用工具: POST http://127.0.0.1:8000/tools/{tool_name}
- 🏥 健康检查: http://127.0.0.1:8000/health

### 工具列表

#### 1. search_mercari_items
搜索Mercari商品

**参数：**
- `keyword` (必需): 搜索关键词
- `category_id` (可选): 分类ID
- `brand_id` (可选): 品牌ID
- `price_min` (可选): 最低价格
- `price_max` (可选): 最高价格
- `condition` (可选): 商品状态 (new, like_new, good, fair, poor)
- `sort` (可选): 排序方式 (created_time, price, popular)
- `order` (可选): 排序顺序 (asc, desc)
- `page` (可选): 页码
- `limit` (可选): 每页数量

**示例：**
```json
{
  "keyword": "iPhone",
  "price_min": 10000,
  "price_max": 50000,
  "condition": "like_new",
  "sort": "price",
  "order": "asc"
}
```

#### 2. get_mercari_item_detail
获取商品详情

**参数：**
- `item_id` (必需): 商品ID

**示例：**
```json
{
  "item_id": "m12345678"
}
```

#### 3. search_mercari_by_category
按分类搜索商品

**参数：**
- `category_name` (必需): 分类名称
- `price_min` (可选): 最低价格
- `price_max` (可选): 最高价格
- `condition` (可选): 商品状态
- `sort` (可选): 排序方式
- `page` (可选): 页码
- `limit` (可选): 每页数量

**示例：**
```json
{
  "category_name": "电子产品",
  "price_min": 5000,
  "price_max": 30000
}
```

## 配置

### MCP客户端配置

#### stdio模式配置

在您的MCP客户端配置中添加以下内容：

```json
{
  "mcpServers": {
    "mercari-mcp": {
      "command": "python",
      "args": ["-m", "mercari_mcp.server"]
    }
  }
}
```

#### SSE模式配置

在您的MCP客户端配置中添加以下内容：

```json
{
  "mcpServers": {
    "mercari-mcp-sse": {
      "url": "http://127.0.0.1:8000/sse",
      "description": "Mercari商品搜索MCP服务器（SSE模式）",
      "transport": "sse"
    }
  }
}
```

### 环境变量

目前暂无特殊环境变量需要设置。

## 开发

### 项目结构

```
mercari-mcp/
├── src/
│   └── mercari_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP服务器主文件
│       └── mercapi_client.py  # Mercapi客户端包装器
├── pyproject.toml
├── README.md
└── requirements.txt
```

### 开发环境设置

1. 安装开发依赖：
```bash
pip install -e ".[dev]"
```

2. 运行测试：
```bash
pytest
```

3. 代码格式化：
```bash
black src/
isort src/
```

4. 类型检查：
```bash
mypy src/
```

### 测试

#### 测试stdio模式
```bash
python scripts/test_mcp.py
```

#### 测试SSE模式
首先启动SSE服务器：
```bash
python scripts/run_sse_server.py
```

然后在另一个终端运行测试：
```bash
python scripts/test_sse_server.py
```

## 故障排除

### 常见问题

1. **模块导入错误**
   - 确保已正确安装所有依赖
   - 检查Python路径和虚拟环境

2. **API调用失败**
   - 检查网络连接
   - 确认mercapi库是否正确安装

3. **MCP连接问题**
   - 检查MCP客户端配置
   - 确认服务器正在运行

### 调试

启用调试日志：
```bash
export PYTHONPATH=src
python -m mercari_mcp.server --log-level DEBUG
```

## 许可证

MIT License

## 贡献

欢迎提交问题和合并请求！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 更新日志

### v0.1.0
- 初始版本
- 基本的商品搜索功能
- 商品详情获取功能
- 分类搜索功能 