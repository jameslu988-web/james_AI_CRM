import React, { useState, useEffect } from 'react'
import { Box, Card, CardContent, Typography, CircularProgress, Chip, Grid, alpha } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import PeopleIcon from '@mui/icons-material/People'
import ShowChartIcon from '@mui/icons-material/ShowChart'
import CancelIcon from '@mui/icons-material/Cancel'
import { getApiUrl } from './config/api'

interface FunnelStage {
  stage: string
  name: string
  color: string
  count: number
  percentage: number
  conversion_rate: number
}

interface FunnelData {
  funnel: FunnelStage[]
  total_customers: number
  lost_customers: number
  overall_conversion_rate: number
  stage_count: number
}

export const SalesFunnel = () => {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<FunnelData | null>(null)

  useEffect(() => {
    fetchFunnelData()
  }, [])

  const fetchFunnelData = async () => {
    try {
      setLoading(true)
      const response = await fetch(getApiUrl('crm', '/funnel-data'))
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('获取漏斗数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress size={60} />
      </Box>
    )
  }

  if (!data) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <Typography color="text.secondary" variant="h6">无法加载漏斗数据</Typography>
      </Box>
    )
  }

  // 反转数据顺序，让成交客户在顶部
  const reversedFunnel = [...data.funnel].reverse()

  return (
    <Box 
      sx={{ 
        position: 'fixed',
        top: 64,
        left: 240,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        p: 0,
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* 内容区域 */}
      <Box sx={{ pt: 0, px: 2, pb: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* 顶部标题 */}
      <Box sx={{ mt: 2, mb: 3 }}>
        <Typography 
          variant="h4" 
          sx={{ 
            color: 'white',
            fontWeight: 700,
            textShadow: '0 2px 4px rgba(0,0,0,0.2)',
            display: 'flex',
            alignItems: 'center',
            gap: 2
          }}
        >
          <ShowChartIcon sx={{ fontSize: 40 }} />
          销售漏斗分析
        </Typography>
      </Box>

      {/* 统计卡片 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card 
            sx={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.18)',
              backdropFilter: 'blur(10px)'
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box 
                  sx={{ 
                    width: 56,
                    height: 56,
                    borderRadius: '16px',
                    background: 'rgba(255,255,255,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <PeopleIcon sx={{ fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5 }}>
                    客户总数
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {data.total_customers}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card 
            sx={{ 
              background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
              color: 'white',
              boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.18)',
              backdropFilter: 'blur(10px)'
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box 
                  sx={{ 
                    width: 56,
                    height: 56,
                    borderRadius: '16px',
                    background: 'rgba(255,255,255,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <TrendingUpIcon sx={{ fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5 }}>
                    整体转化率
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {data.overall_conversion_rate}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card 
            sx={{ 
              background: 'linear-gradient(135deg, #ee0979 0%, #ff6a00 100%)',
              color: 'white',
              boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.18)',
              backdropFilter: 'blur(10px)'
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box 
                  sx={{ 
                    width: 56,
                    height: 56,
                    borderRadius: '16px',
                    background: 'rgba(255,255,255,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <CancelIcon sx={{ fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5 }}>
                    流失客户
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {data.lost_customers}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 漏斗图区域 */}
      <Box sx={{ flex: 1, display: 'flex', gap: 2, minHeight: 0, overflow: 'hidden' }}>
        {/* 左侧：漏斗图 */}
        <Card 
          sx={{ 
            flex: 1,
            background: 'rgba(255,255,255,0.95)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
            border: '1px solid rgba(255,255,255,0.18)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
        >
          <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 3, overflow: 'hidden' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1a237e' }}>
              销售漏斗分布
            </Typography>
            
            <Box sx={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={reversedFunnel}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 120, bottom: 10 }}
                >
                  <XAxis type="number" stroke="#666" />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    width={100}
                    tick={{ fontSize: 13, fill: '#333' }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload as FunnelStage
                        return (
                          <Box
                            sx={{
                              backgroundColor: 'white',
                              border: '1px solid #e0e0e0',
                              borderRadius: 2,
                              p: 2,
                              boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                            }}
                          >
                            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                              {data.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              客户数：<strong>{data.count}</strong>
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              占比：<strong>{data.percentage}%</strong>
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              转化率：<strong>{data.conversion_rate}%</strong>
                            </Typography>
                          </Box>
                        )
                      }
                      return null
                    }}
                  />
                  <Bar 
                    dataKey="count" 
                    radius={[0, 12, 12, 0]}
                  >
                    {reversedFunnel.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                    <LabelList
                      dataKey="count"
                      position="right"
                      formatter={(value: any) => `${value}人`}
                      style={{ fontSize: 13, fontWeight: 600, fill: '#333' }}
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>

        {/* 右侧：转化率指标 */}
        <Card 
          sx={{ 
            width: 380,
            background: 'rgba(255,255,255,0.95)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
            border: '1px solid rgba(255,255,255,0.18)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
        >
          <CardContent sx={{ p: 3, pb: 2, flexShrink: 0 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1a237e' }}>
              阶段转化率
            </Typography>
          </CardContent>
          
          <Box sx={{ 
            flex: 1,
            px: 3,
            pb: 3,
            overflow: 'auto',
            '&::-webkit-scrollbar': {
              width: '6px'
            },
            '&::-webkit-scrollbar-track': {
              background: 'rgba(0,0,0,0.05)',
              borderRadius: '3px'
            },
            '&::-webkit-scrollbar-thumb': {
              background: 'rgba(0,0,0,0.2)',
              borderRadius: '3px',
              '&:hover': {
                background: 'rgba(0,0,0,0.3)'
              }
            }
          }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {data.funnel.slice(1).map((stage, index) => {
                const prevStage = data.funnel[index]
                const isGood = stage.conversion_rate >= 50
                
                return (
                  <Box
                    key={stage.stage}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: isGood 
                        ? 'linear-gradient(135deg, #11998e15 0%, #38ef7d15 100%)'
                        : 'linear-gradient(135deg, #ee097915 0%, #ff6a0015 100%)',
                      border: `2px solid ${isGood ? '#11998e' : '#ee0979'}`,
                      transition: 'all 0.3s',
                      '&:hover': {
                        transform: 'translateX(4px)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                      }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                        {prevStage.name} → {stage.name}
                      </Typography>
                      {isGood ? (
                        <TrendingUpIcon sx={{ fontSize: 18, color: '#11998e' }} />
                      ) : (
                        <TrendingDownIcon sx={{ fontSize: 18, color: '#ee0979' }} />
                      )}
                    </Box>
                    <Typography
                      variant="h4"
                      sx={{ 
                        fontWeight: 700,
                        color: isGood ? '#11998e' : '#ee0979'
                      }}
                    >
                      {stage.conversion_rate}%
                    </Typography>
                    <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                      <Chip 
                        label={`${prevStage.count}人`}
                        size="small"
                        sx={{ 
                          fontSize: 11,
                          height: 20,
                          bgcolor: alpha(prevStage.color, 0.2),
                          color: prevStage.color,
                          fontWeight: 600
                        }}
                      />
                      <Typography variant="caption" sx={{ alignSelf: 'center' }}>→</Typography>
                      <Chip 
                        label={`${stage.count}人`}
                        size="small"
                        sx={{ 
                          fontSize: 11,
                          height: 20,
                          bgcolor: alpha(stage.color, 0.2),
                          color: stage.color,
                          fontWeight: 600
                        }}
                      />
                    </Box>
                  </Box>
                )
              })}
            </Box>
          </Box>
        </Card>
      </Box>
      </Box>
    </Box>
  )
}
