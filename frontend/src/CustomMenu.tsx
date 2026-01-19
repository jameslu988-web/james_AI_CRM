import { Menu } from 'react-admin'
import { Box, Collapse, ListItemButton, ListItemIcon, ListItemText } from '@mui/material'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PeopleIcon from '@mui/icons-material/People'
import SettingsIcon from '@mui/icons-material/Settings'
import ListIcon from '@mui/icons-material/List'
import EmailIcon from '@mui/icons-material/Email'
import CreateIcon from '@mui/icons-material/Create'
import DraftsIcon from '@mui/icons-material/Drafts'
import SendIcon from '@mui/icons-material/Send'
import HistoryIcon from '@mui/icons-material/History'
import DrawIcon from '@mui/icons-material/Draw'
import SettingsApplicationsIcon from '@mui/icons-material/SettingsApplications'
import ExpandLess from '@mui/icons-material/ExpandLess'
import ExpandMore from '@mui/icons-material/ExpandMore'
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart'
import AssignmentIcon from '@mui/icons-material/Assignment'
import CampaignIcon from '@mui/icons-material/Campaign'
import DeleteIcon from '@mui/icons-material/Delete'
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks'
import HelpIcon from '@mui/icons-material/Help'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter'
import StorageIcon from '@mui/icons-material/Storage'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import FilterAltIcon from '@mui/icons-material/FilterAlt'

export const CustomMenu = () => {
  const navigate = useNavigate()
  const [openCustomers, setOpenCustomers] = useState(true)
  const [openEmails, setOpenEmails] = useState(true)
  const [openKnowledge, setOpenKnowledge] = useState(true)

  // 处理客户管理模块点击
  const handleCustomersClick = () => {
    setOpenCustomers(!openCustomers)
    // 如果是展开操作，跳转到客户列表
    if (!openCustomers) {
      navigate('/customers')
    }
  }

  // 处理邮件管理模块点击
  const handleEmailsClick = () => {
    setOpenEmails(!openEmails)
    // 如果是展开操作，跳转到收件箱
    if (!openEmails) {
      navigate('/inbox')
    }
  }

  // 处理知识库模块点击
  const handleKnowledgeClick = () => {
    setOpenKnowledge(!openKnowledge)
    if (!openKnowledge) {
      navigate('/products')
    }
  }

  return (
    <Menu>
      {/* 发现客户 */}
      <Menu.ResourceItem name="leads" />
      
      {/* 客户管理 - 折叠菜单 */}
      <ListItemButton onClick={handleCustomersClick}>
        <ListItemIcon>
          <PeopleIcon />
        </ListItemIcon>
        <ListItemText primary="客户管理" />
        {openCustomers ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>
      <Collapse in={openCustomers} timeout="auto" unmountOnExit>
        <Box sx={{ pl: 4 }}>
          <Menu.Item
            to="/customers"
            primaryText="客户列表"
            leftIcon={<ListIcon />}
          />
          <Menu.Item
            to="/sales-funnel"
            primaryText="销售漏斗"
            leftIcon={<FilterAltIcon />}
          />
          <Menu.Item
            to="/customer-settings"
            primaryText="客户设置"
            leftIcon={<SettingsIcon />}
          />
        </Box>
      </Collapse>
      
      {/* 邮件管理 - 折叠菜单 */}
      <ListItemButton onClick={handleEmailsClick}>
        <ListItemIcon>
          <EmailIcon />
        </ListItemIcon>
        <ListItemText primary="邮件管理" />
        {openEmails ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>
      <Collapse in={openEmails} timeout="auto" unmountOnExit>
        <Box sx={{ pl: 4 }}>
          <Menu.Item
            to="/inbox"
            primaryText="收件箱"
            leftIcon={<HistoryIcon />}
          />
          <Menu.Item
            to="/email_history/create"
            primaryText="写邮件"
            leftIcon={<CreateIcon />}
          />
          <Menu.Item
            to="/drafts"
            primaryText="草稿箱"
            leftIcon={<DraftsIcon />}
          />
          <Menu.Item
            to="/sent"
            primaryText="已发送"
            leftIcon={<SendIcon />}
          />
          <Menu.Item
            to="/email_trash"
            primaryText="回收站"
            leftIcon={<DeleteIcon />}
          />
          <Menu.Item
            to="/signatures"
            primaryText="邮件签名"
            leftIcon={<DrawIcon />}
          />
        </Box>
      </Collapse>
      
      {/* 订单管理 */}
      <Menu.ResourceItem name="orders" />
      
      {/* 知识库管理 - 折叠菜单 */}
      <ListItemButton onClick={handleKnowledgeClick}>
        <ListItemIcon>
          <LibraryBooksIcon />
        </ListItemIcon>
        <ListItemText primary="知识库" />
        {openKnowledge ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>
      <Collapse in={openKnowledge} timeout="auto" unmountOnExit>
        <Box sx={{ pl: 4 }}>
          <Menu.Item
            to="/products"
            primaryText="产品库"
            leftIcon={<ShoppingCartIcon />}
          />
          <Menu.Item
            to="/knowledge_faqs"
            primaryText="FAQ库"
            leftIcon={<HelpIcon />}
          />
          <Menu.Item
            to="/pricing_rules"
            primaryText="价格规则"
            leftIcon={<AttachMoneyIcon />}
          />
          <Menu.Item
            to="/case_studies"
            primaryText="案例库"
            leftIcon={<BusinessCenterIcon />}
          />
          <Menu.Item
            to="/vector_knowledge"
            primaryText="向量知识库"
            leftIcon={<StorageIcon />}
          />
          <Menu.Item
            to="/prompt_templates"
            primaryText="AI提示词模板"
            leftIcon={<SmartToyIcon />}
          />
        </Box>
      </Collapse>
      
      {/* 系统配置 */}
      <Menu.Item
        to="/system-settings"
        primaryText="系统配置"
        leftIcon={<SettingsApplicationsIcon />}
      />
    </Menu>
  )
}
