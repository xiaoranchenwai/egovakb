# MCP回调鉴权接口文档

## 概述

MCP回调鉴权接口用于处理从MCP平台转发的请求。在egovakb平台调用MCP平台的API时，MCP平台需要验证用户的身份和权限，此时MCP平台会回调此接口获取用户信息和权限。

## 流程说明

1. egovakb平台向MCP平台发起请求，在请求头中携带egovakb平台的认证信息（Token）
2. MCP平台收到请求后，将认证信息回调至egovakb平台的鉴权接口
3. egovakb平台验证认证信息，返回用户身份和权限信息
4. MCP平台根据返回的用户身份和权限信息，判断用户是否有权限访问请求的资源

## 接口详情

### 请求方式

- URL路径: `/api/user/mcp/callback/auth`
- HTTP方法: POST
- 请求头:
  - `Authorization`: 原始Token
  - `MCP-Callback`: 任意值（用于标识这是一个MCP回调请求）

### 响应内容

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "用户ID",
    "username": "用户名",
    "email": "用户邮箱",
    "role": "用户角色",
    "permissions": ["权限1", "权限2", ...]
  }
}
```

失败响应：

```json
{
  "code": 错误码,
  "message": "错误信息"
}
```

## 使用示例

### 1. MCP平台发起回调请求

```
POST /api/user/mcp/callback/auth HTTP/1.1
Host: egovakb.example.com
Authorization: <原始Token>
MCP-Callback: true
Content-Type: application/json
```

### 2. egovakb平台处理请求并响应

egovakb平台验证Token，如果有效，则返回用户信息和权限；如果无效，则返回错误信息。

## 注意事项

1. MCP平台在回调时必须携带原始的Authorization头信息
2. MCP平台必须添加`MCP-Callback`头，以便egovakb平台识别这是MCP回调请求
3. 接口仅支持已登录用户的Token，不支持API Key等其他认证方式 