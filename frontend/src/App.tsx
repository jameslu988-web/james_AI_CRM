import { Admin, Resource, CustomRoutes } from 'react-admin'
import { Route } from 'react-router-dom'
import { dataProvider } from './dataProvider'
import { authProvider } from './authProvider'
import { Login } from './Login'
import { CustomerList, CustomerCreate, CustomerEdit } from './customers'
import { CustomerSettings } from './customerSettings'
import { LeadList, LeadCreate, LeadEdit } from './leads'
import { OrderList, OrderCreate, OrderEdit } from './orders'
import { EmailList, EmailCreate, EmailShow, InboxList, SentList, DraftsList } from './emails'
import { EmailTrashList } from './emailTrash'
import { FollowupList, FollowupCreate, FollowupEdit } from './followups'
import { TemplateList, TemplateCreate, TemplateEdit } from './templates'
import { CampaignList, CampaignCreate, CampaignEdit } from './campaigns'
import { EmailAccountList, EmailAccountEdit, EmailAccountShow } from './emailAccounts'
import { SignatureList, SignatureCreate, SignatureEdit } from './signatures'
import { SystemSettings } from './systemSettings'
import { ProxySettings } from './proxySettings'
import { CustomLayout } from './CustomLayout'
import { ProductList, ProductCreate, ProductEdit } from './products'
import { FAQList, FAQCreate, FAQEdit } from './faqs'
import { PricingRuleList, PricingRuleCreate, PricingRuleEdit } from './pricingRules'
import { CaseStudyList, CaseStudyCreate, CaseStudyEdit } from './caseStudies'
import { VectorKnowledgeList } from './vectorKnowledge'
import { PromptTemplateList } from './promptTemplates'
import { SalesFunnel } from './SalesFunnel'
import { TagList, TagCreate, TagEdit } from './tags'

export default function App() {
  return (
    <Admin 
      dataProvider={dataProvider} 
      authProvider={authProvider}
      loginPage={Login}
      layout={CustomLayout}
    >
      <Resource name="leads" options={{ label: '发现客户' }} list={LeadList} create={LeadCreate} edit={LeadEdit} />
      <Resource name="customers" options={{ label: '客户管理' }} list={CustomerList} create={CustomerCreate} edit={CustomerEdit} />
      <Resource name="orders" options={{ label: '订单管理' }} list={OrderList} create={OrderCreate} edit={OrderEdit} />
      <Resource name="email_history" options={{ label: '邮件管理' }} list={EmailList} create={EmailCreate} show={EmailShow} />
      {/* 🔥 新增：独立的邮件列表资源 */}
      <Resource name="inbox" options={{ label: '收件箱' }} list={InboxList} />
      <Resource name="sent" options={{ label: '已发送' }} list={SentList} />
      <Resource name="drafts" options={{ label: '草稿箱' }} list={DraftsList} />
      <Resource name="followup_records" options={{ label: '跟进记录' }} list={FollowupList} create={FollowupCreate} edit={FollowupEdit} />
      <Resource name="email_templates" options={{ label: '邮件模板' }} list={TemplateList} create={TemplateCreate} edit={TemplateEdit} />
      <Resource name="email_campaigns" options={{ label: '邮件活动' }} list={CampaignList} create={CampaignCreate} edit={CampaignEdit} />
      <Resource name="email_accounts" options={{ label: '邮箱账户' }} list={EmailAccountList} edit={EmailAccountEdit} show={EmailAccountShow} />
      <Resource name="signatures" options={{ label: '邮件签名' }} list={SignatureList} create={SignatureCreate} edit={SignatureEdit} />
      <Resource name="products" options={{ label: '产品知识库' }} list={ProductList} create={ProductCreate} edit={ProductEdit} />
      <Resource name="knowledge_faqs" options={{ label: 'FAQ知识库' }} list={FAQList} create={FAQCreate} edit={FAQEdit} />
      <Resource name="pricing_rules" options={{ label: '价格规则' }} list={PricingRuleList} create={PricingRuleCreate} edit={PricingRuleEdit} />
      <Resource name="case_studies" options={{ label: '案例库' }} list={CaseStudyList} create={CaseStudyCreate} edit={CaseStudyEdit} />
      <Resource name="vector_knowledge" options={{ label: '向量知识库' }} list={VectorKnowledgeList} />
      <Resource name="prompt_templates" options={{ label: 'AI提示词模板' }} list={PromptTemplateList} />
      <Resource name="tags" options={{ label: '客户标签' }} list={TagList} create={TagCreate} edit={TagEdit} />
      <CustomRoutes>
        <Route path="/customer-settings" element={<CustomerSettings />} />
        <Route path="/system-settings" element={<SystemSettings />} />
        <Route path="/proxy-settings" element={<ProxySettings />} />
        <Route path="/email_trash" element={<EmailTrashList />} />
        <Route path="/sales-funnel" element={<SalesFunnel />} />
      </CustomRoutes>
    </Admin>
  )
}
