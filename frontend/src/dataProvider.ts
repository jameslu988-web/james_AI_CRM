import simpleRestProvider from 'ra-data-simple-rest'
import { fetchUtils } from 'react-admin'
import { EMAIL_API_BASE } from './config/api'

const apiUrl = EMAIL_API_BASE

// 自定义httpClient，在每个请求中添加JWT令牌
const httpClient = (url: string, options: any = {}) => {
  if (!options.headers) {
    options.headers = new Headers({ Accept: 'application/json' })
  }
  
  // 添加JWT令牌
  const token = localStorage.getItem('token')
  if (token) {
    options.headers.set('Authorization', `Bearer ${token}`)
  }
  
  return fetchUtils.fetchJson(url, options)
}

// 使用自定义httpClient创建dataProvider
const baseDataProvider = simpleRestProvider(apiUrl, httpClient)

// 扩展dataProvider以支持特殊资源
export const dataProvider = {
  ...baseDataProvider,
  
  // 覆盖getList方法
  getList: (resource: string, params: any) => {
    // 邮件资源特殊处理
    const emailResources = ['inbox', 'sent', 'drafts', 'email_history']
    if (emailResources.includes(resource)) {
      const { page, perPage } = params.pagination
      const { field, order } = params.sort
      
      const query: any = {
        _start: (page - 1) * perPage,
        _end: page * perPage,
        _sort: field,
        _order: order,
      }
      
      // 添加筛选参数（排除空值）
      if (params.filter) {
        Object.keys(params.filter).forEach(key => {
          const value = params.filter[key]
          if (value !== undefined && value !== null && value !== '') {
            query[key] = value
          }
        })
      }
      
      const url = `${apiUrl}/email_history?${new URLSearchParams(query).toString()}`
      
      return httpClient(url).then(({ headers, json }) => {
        const contentRange = headers.get('content-range')
        const total = contentRange ? parseInt(contentRange.split('/').pop() || '0', 10) : json.length
        
        return {
          data: json,
          total: total,
        }
      })
    }
    
    // 向量知识库特殊处理
    if (resource === 'vector_knowledge') {
      const { page, perPage } = params.pagination
      const query: any = {
        skip: (page - 1) * perPage,
        limit: perPage,
      }
      
      if (params.filter?.category) {
        query.category = params.filter.category
      }
      
      const url = `${apiUrl}/knowledge/documents?${new URLSearchParams(query).toString()}`
      
      return httpClient(url).then(({ json }) => ({
        data: json.data,
        total: json.total,
      }))
    }
    
    // 提示词模板特殊处理
    if (resource === 'prompt_templates') {
      const { page, perPage } = params.pagination
      const query: any = {}
      
      if (params.filter?.template_type) {
        query.template_type = params.filter.template_type
      }
      if (params.filter?.is_active !== undefined && params.filter.is_active !== '') {
        query.is_active = params.filter.is_active === 'true' || params.filter.is_active === true
      }
      
      const queryString = Object.keys(query).length > 0 
        ? `?${new URLSearchParams(query).toString()}`
        : ''
      
      const url = `${apiUrl}/prompt-templates${queryString}`
      
      return httpClient(url).then(({ json }) => {
        const dataWithIds = json.map((item: any) => ({
          ...item,
          id: item.id || item.template_id
        }))
        
        const start = (page - 1) * perPage
        const end = start + perPage
        const paginatedData = dataWithIds.slice(start, end)
        
        return {
          data: paginatedData,
          total: dataWithIds.length
        }
      })
    }
    
    // 其他资源使用默认处理
    return baseDataProvider.getList(resource, params)
  },
  
  // 覆盖delete方法，处理向量知识库和提示词模板的删除
  delete: (resource: string, params: any) => {
    if (resource === 'vector_knowledge') {
      return httpClient(`${apiUrl}/knowledge/documents/${params.id}`, {
        method: 'DELETE',
      }).then(({ json }) => ({ data: { id: params.id } }))
    }
    
    if (resource === 'prompt_templates') {
      return httpClient(`${apiUrl}/prompt-templates/${params.id}`, {
        method: 'DELETE',
      }).then(({ json }) => ({ data: { id: params.id } }))
    }
    
    return baseDataProvider.delete(resource, params)
  },
  
  // 覆盖getOne方法
  getOne: (resource: string, params: any) => {
    if (resource === 'prompt_templates') {
      return httpClient(`${apiUrl}/prompt-templates/${params.id}`).then(({ json }) => ({
        data: { ...json, id: json.id }
      }))
    }
    
    return baseDataProvider.getOne(resource, params)
  },
  
  // 覆盖update方法
  update: (resource: string, params: any) => {
    if (resource === 'prompt_templates') {
      return httpClient(`${apiUrl}/prompt-templates/${params.id}`, {
        method: 'PUT',
        body: JSON.stringify(params.data),
      }).then(({ json }) => ({ data: { ...json, id: json.id } }))
    }
    
    return baseDataProvider.update(resource, params)
  },
  
  // 覆盖create方法
  create: (resource: string, params: any) => {
    if (resource === 'prompt_templates') {
      return httpClient(`${apiUrl}/prompt-templates`, {
        method: 'POST',
        body: JSON.stringify(params.data),
      }).then(({ json }) => ({ data: { ...json, id: json.id } }))
    }
    
    return baseDataProvider.create(resource, params)
  },
}
