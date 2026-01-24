/**
 * API 配置中心
 * 
 * 所有后端API的URL配置统一在此管理
 * 修改端口或域名时，只需修改此文件即可
 */

// API基础URL配置
const API_BASE_URLS = {
  // 邮件系统后端 (端口 8001) - 🔥 统一使用8001端口
  // 🔥 使用window.location.hostname自动适配localhost和局域网IP
  email: `http://${window.location.hostname}:8001/api`,
  
  // CRM系统后端 (端口 8001) - 所有API都在同一个FastAPI应用中
  crm: `http://${window.location.hostname}:8001/api`,
} as const

/**
 * 获取完整的API URL
 * @param service 服务类型 ('email' | 'crm')
 * @param path API路径 (以 / 开头)
 * @returns 完整的API URL
 * 
 * @example
 * getApiUrl('email', '/email_history') 
 * // 返回: 'http://127.0.0.1:8001/api/email_history'
 */
export const getApiUrl = (service: keyof typeof API_BASE_URLS, path: string): string => {
  const baseUrl = API_BASE_URLS[service]
  // 确保 path 以 / 开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${baseUrl}${normalizedPath}`
}

/**
 * 直接导出基础URL（用于 dataProvider 等需要基础URL的场景）
 */
export const EMAIL_API_BASE = API_BASE_URLS.email
export const CRM_API_BASE = API_BASE_URLS.crm

/**
 * API 服务映射（方便理解）
 * 
 * email (8001): 
 *   - /email_history - 邮件历史
 *   - /email_accounts - 邮件账户
 *   - /prompt-templates - 提示词模板
 *   - /quick-replies - 快速回复
 *   - /ai/analyze-email - AI邮件分析
 * 
 * crm (8002):
 *   - /customers - 客户管理
 *   - /custom_fields - 自定义字段
 *   - /leads - 线索管理
 */
