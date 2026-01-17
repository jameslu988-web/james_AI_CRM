import { AuthProvider } from 'react-admin'

const apiUrl = 'http://127.0.0.1:8001/api'

export const authProvider: AuthProvider = {
  login: async ({ username, password }) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const request = new Request(`${apiUrl}/auth/login`, {
      method: 'POST',
      body: formData,
    })

    try {
      const response = await fetch(request)
      if (response.status < 200 || response.status >= 300) {
        throw new Error('登录失败')
      }

      const auth = await response.json()
      
      // 保存令牌和用户信息
      localStorage.setItem('token', auth.access_token)
      localStorage.setItem('user', JSON.stringify(auth.user))
      localStorage.setItem('permissions', JSON.stringify(auth.user.roles))

      return Promise.resolve()
    } catch (error) {
      return Promise.reject(error)
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('permissions')
    return Promise.resolve()
  },

  checkAuth: () => {
    return localStorage.getItem('token') ? Promise.resolve() : Promise.reject()
  },

  checkError: (error) => {
    const status = error.status
    if (status === 401 || status === 403) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      return Promise.reject()
    }
    return Promise.resolve()
  },

  getIdentity: () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return Promise.resolve({
        id: user.id,
        fullName: user.full_name,
        avatar: user.avatar,
      })
    } catch (error) {
      return Promise.reject(error)
    }
  },

  getPermissions: () => {
    try {
      const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
      return Promise.resolve(permissions)
    } catch (error) {
      return Promise.reject(error)
    }
  },
}
