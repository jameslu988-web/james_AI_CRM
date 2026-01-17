import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm, NumberInput, NumberField } from 'react-admin'

const caseStudyFilters = [
  <TextInput key="search" label="搜索客户/产品" source="search" alwaysOn />, 
  <SelectInput key="business_stage" label="业务阶段" source="business_stage" choices={[
    { id: '询盘', name: '询盘' },
    { id: '报价', name: '报价' },
    { id: '样品', name: '样品' },
    { id: '订单', name: '订单' },
    { id: '售后', name: '售后' },
  ]} />
]

export const CaseStudyList = (props: any) => (
  <List {...props} perPage={20} filters={caseStudyFilters}>
    <Datagrid rowClick="edit">
      <TextField source="title" label="案例标题" />
      <TextField source="customer_name" label="客户名称" />
      <TextField source="business_stage" label="业务阶段" />
      <NumberField source="order_value" label="订单金额(USD)" />
      <NumberField source="success_score" label="成功评分" />
    </Datagrid>
  </List>
)

export const CaseStudyCreate = (props: any) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="title" label="案例标题" required fullWidth placeholder="如: 美国客户5万件平角内裤定制案例" />
      
      <TextInput source="customer_name" label="客户名称" fullWidth />
      <TextInput source="customer_country" label="客户国家/地区" />
      
      <SelectInput source="business_stage" label="业务阶段" required choices={[
        { id: '询盘', name: '询盘' },
        { id: '报价', name: '报价' },
        { id: '样品', name: '样品' },
        { id: '订单', name: '订单' },
        { id: '售后', name: '售后' },
      ]} />
      
      <TextInput source="product_skus" label="涉及产品SKU(JSON数组)" fullWidth placeholder='["SKU001", "SKU002"]' />
      <NumberInput source="order_quantity" label="订单数量" />
      <NumberInput source="order_value" label="订单金额(USD)" step={0.01} />
      
      <TextInput source="challenge" label="遇到的挑战" multiline fullWidth rows={3} helperText="客户提出了什么难题?" />
      <TextInput source="solution" label="解决方案" multiline fullWidth rows={3} helperText="我们如何解决的?" />
      <TextInput source="result" label="最终结果" multiline fullWidth rows={3} helperText="成交情况、客户反馈等" />
      
      <TextInput source="key_points" label="关键要点(JSON数组)" fullWidth placeholder='["快速响应", "定制方案", "价格优势"]' />
      <TextInput source="email_excerpts" label="邮件摘录(JSON)" multiline fullWidth rows={4} placeholder='{"inquiry": "客户询盘邮件", "quote": "我方报价邮件", "negotiation": "谈判邮件"}' />
      
      <NumberInput source="success_score" label="成功评分(1-10)" defaultValue={8} min={1} max={10} />
      <TextInput source="lessons_learned" label="经验总结" multiline fullWidth rows={3} />
      
      <TextInput source="tags" label="标签(JSON数组)" fullWidth placeholder='["大客户", "重复订单", "转介绍"]' />
      <TextInput source="notes" label="内部备注" multiline fullWidth />
    </SimpleForm>
  </Create>
)

export const CaseStudyEdit = (props: any) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="title" label="案例标题" required fullWidth />
      
      <TextInput source="customer_name" label="客户名称" fullWidth />
      <TextInput source="customer_country" label="客户国家/地区" />
      
      <SelectInput source="business_stage" label="业务阶段" required choices={[
        { id: '询盘', name: '询盘' },
        { id: '报价', name: '报价' },
        { id: '样品', name: '样品' },
        { id: '订单', name: '订单' },
        { id: '售后', name: '售后' },
      ]} />
      
      <TextInput source="product_skus" label="涉及产品SKU(JSON数组)" fullWidth />
      <NumberInput source="order_quantity" label="订单数量" />
      <NumberInput source="order_value" label="订单金额(USD)" step={0.01} />
      
      <TextInput source="challenge" label="遇到的挑战" multiline fullWidth rows={3} />
      <TextInput source="solution" label="解决方案" multiline fullWidth rows={3} />
      <TextInput source="result" label="最终结果" multiline fullWidth rows={3} />
      
      <TextInput source="key_points" label="关键要点(JSON数组)" fullWidth />
      <TextInput source="email_excerpts" label="邮件摘录(JSON)" multiline fullWidth rows={4} />
      
      <NumberInput source="success_score" label="成功评分(1-10)" min={1} max={10} />
      <TextInput source="lessons_learned" label="经验总结" multiline fullWidth rows={3} />
      
      <TextInput source="tags" label="标签(JSON数组)" fullWidth />
      <TextInput source="notes" label="内部备注" multiline fullWidth />
    </SimpleForm>
  </Edit>
)
