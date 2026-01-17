import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm, BooleanInput, NumberInput, BooleanField, NumberField } from 'react-admin'

const faqFilters = [
  <TextInput key="search" label="搜索问题/答案" source="search" alwaysOn />, 
  <SelectInput key="category" label="分类" source="category" choices={[
    { id: '产品相关', name: '产品相关' },
    { id: '价格与报价', name: '价格与报价' },
    { id: '定制服务', name: '定制服务' },
    { id: '样品相关', name: '样品相关' },
    { id: '订单与生产', name: '订单与生产' },
    { id: '物流与运输', name: '物流与运输' },
    { id: '付款与结算', name: '付款与结算' },
    { id: '售后服务', name: '售后服务' },
  ]} />,
  <SelectInput key="language" label="语言" source="language" choices={[
    { id: 'en', name: 'English' },
    { id: 'zh', name: '中文' },
    { id: 'both', name: '双语' },
  ]} />
]

export const FAQList = (props: any) => (
  <List {...props} perPage={20} filters={faqFilters}>
    <Datagrid rowClick="edit">
      <TextField source="question_en" label="问题(英文)" />
      <TextField source="category" label="分类" />
      <TextField source="language" label="语言" />
      <NumberField source="usage_count" label="使用次数" />
      <NumberField source="priority" label="优先级" />
      <BooleanField source="is_active" label="启用" />
    </Datagrid>
  </List>
)

export const FAQCreate = (props: any) => (
  <Create {...props}>
    <SimpleForm>
      <SelectInput source="category" label="分类" required choices={[
        { id: '产品相关', name: '产品相关' },
        { id: '价格与报价', name: '价格与报价' },
        { id: '定制服务', name: '定制服务' },
        { id: '样品相关', name: '样品相关' },
        { id: '订单与生产', name: '订单与生产' },
        { id: '物流与运输', name: '物流与运输' },
        { id: '付款与结算', name: '付款与结算' },
        { id: '售后服务', name: '售后服务' },
      ]} />
      
      <SelectInput source="language" label="语言" required choices={[
        { id: 'en', name: 'English' },
        { id: 'zh', name: '中文' },
        { id: 'both', name: '双语' },
      ]} />
      
      <TextInput source="question_en" label="问题(英文)" required fullWidth multiline rows={2} />
      <TextInput source="answer_en" label="答案(英文)" required fullWidth multiline rows={4} />
      
      <TextInput source="question_zh" label="问题(中文)" fullWidth multiline rows={2} />
      <TextInput source="answer_zh" label="答案(中文)" fullWidth multiline rows={4} />
      
      <TextInput source="keywords" label="关键词(JSON数组)" fullWidth placeholder='["MOQ", "minimum order", "起订量"]' helperText="用于检索匹配" />
      
      <NumberInput source="priority" label="优先级" defaultValue={0} helperText="数字越大优先级越高" />
      <BooleanInput source="is_active" label="启用" />
      
      <TextInput source="related_products" label="关联产品SKU(JSON数组)" fullWidth placeholder='["SKU001", "SKU002"]' />
      <TextInput source="notes" label="内部备注" multiline fullWidth />
    </SimpleForm>
  </Create>
)

export const FAQEdit = (props: any) => (
  <Edit {...props}>
    <SimpleForm>
      <SelectInput source="category" label="分类" required choices={[
        { id: '产品相关', name: '产品相关' },
        { id: '价格与报价', name: '价格与报价' },
        { id: '定制服务', name: '定制服务' },
        { id: '样品相关', name: '样品相关' },
        { id: '订单与生产', name: '订单与生产' },
        { id: '物流与运输', name: '物流与运输' },
        { id: '付款与结算', name: '付款与结算' },
        { id: '售后服务', name: '售后服务' },
      ]} />
      
      <SelectInput source="language" label="语言" required choices={[
        { id: 'en', name: 'English' },
        { id: 'zh', name: '中文' },
        { id: 'both', name: '双语' },
      ]} />
      
      <TextInput source="question_en" label="问题(英文)" required fullWidth multiline rows={2} />
      <TextInput source="answer_en" label="答案(英文)" required fullWidth multiline rows={4} />
      
      <TextInput source="question_zh" label="问题(中文)" fullWidth multiline rows={2} />
      <TextInput source="answer_zh" label="答案(中文)" fullWidth multiline rows={4} />
      
      <TextInput source="keywords" label="关键词(JSON数组)" fullWidth helperText="用于检索匹配" />
      
      <NumberInput source="priority" label="优先级" helperText="数字越大优先级越高" />
      <NumberInput source="usage_count" label="使用次数" disabled />
      <BooleanInput source="is_active" label="启用" />
      
      <TextInput source="related_products" label="关联产品SKU(JSON数组)" fullWidth />
      <TextInput source="notes" label="内部备注" multiline fullWidth />
    </SimpleForm>
  </Edit>
)
