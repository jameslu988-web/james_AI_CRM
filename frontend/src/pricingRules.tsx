import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm, BooleanInput, NumberInput, BooleanField, NumberField } from 'react-admin'

const pricingRuleFilters = [
  <TextInput key="search" label="搜索规则名称" source="search" alwaysOn />, 
  <SelectInput key="rule_type" label="规则类型" source="rule_type" choices={[
    { id: 'quantity_discount', name: '数量折扣' },
    { id: 'material_surcharge', name: '材质加价' },
    { id: 'customization_fee', name: '定制费用' },
    { id: 'seasonal_adjustment', name: '季节调整' },
  ]} />
]

export const PricingRuleList = (props: any) => (
  <List {...props} perPage={20} filters={pricingRuleFilters}>
    <Datagrid rowClick="edit">
      <TextField source="rule_name" label="规则名称" />
      <TextField source="rule_type" label="规则类型" />
      <NumberField source="priority" label="优先级" />
      <BooleanField source="is_active" label="启用" />
    </Datagrid>
  </List>
)

export const PricingRuleCreate = (props: any) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="rule_name" label="规则名称" required fullWidth />
      
      <SelectInput source="rule_type" label="规则类型" required choices={[
        { id: 'quantity_discount', name: '数量折扣' },
        { id: 'material_surcharge', name: '材质加价' },
        { id: 'customization_fee', name: '定制费用' },
        { id: 'seasonal_adjustment', name: '季节调整' },
      ]} />
      
      <TextInput source="description" label="规则描述" multiline fullWidth rows={3} />
      
      <TextInput 
        source="conditions" 
        label="触发条件(JSON)" 
        multiline 
        fullWidth 
        rows={4}
        placeholder='{"min_quantity": 1000, "max_quantity": 5000, "product_categories": ["平角内裤"]}'
        helperText="定义规则生效的条件"
      />
      
      <TextInput 
        source="pricing_logic" 
        label="定价逻辑(JSON)" 
        multiline 
        fullWidth 
        rows={4}
        placeholder='{"discount_rate": 0.1, "fixed_discount": 0.5, "price_multiplier": 1.2}'
        helperText="定义价格计算方式"
      />
      
      <NumberInput source="priority" label="优先级" defaultValue={0} helperText="数字越大优先级越高,多规则冲突时使用" />
      <BooleanInput source="is_active" label="启用" />
      
      <TextInput source="valid_from" label="生效开始日期" type="date" />
      <TextInput source="valid_until" label="生效结束日期" type="date" />
      
      <TextInput source="notes" label="内部备注" multiline fullWidth />
    </SimpleForm>
  </Create>
)

export const PricingRuleEdit = (props: any) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="rule_name" label="规则名称" required fullWidth />
      
      <SelectInput source="rule_type" label="规则类型" required choices={[
        { id: 'quantity_discount', name: '数量折扣' },
        { id: 'material_surcharge', name: '材质加价' },
        { id: 'customization_fee', name: '定制费用' },
        { id: 'seasonal_adjustment', name: '季节调整' },
      ]} />
      
      <TextInput source="description" label="规则描述" multiline fullWidth rows={3} />
      
      <TextInput 
        source="conditions" 
        label="触发条件(JSON)" 
        multiline 
        fullWidth 
        rows={4}
        helperText="定义规则生效的条件"
      />
      
      <TextInput 
        source="pricing_logic" 
        label="定价逻辑(JSON)" 
        multiline 
        fullWidth 
        rows={4}
        helperText="定义价格计算方式"
      />
      
      <NumberInput source="priority" label="优先级" helperText="数字越大优先级越高,多规则冲突时使用" />
      <BooleanInput source="is_active" label="启用" />
      
      <TextInput source="valid_from" label="生效开始日期" type="date" />
      <TextInput source="valid_until" label="生效结束日期" type="date" />
      
      <TextInput source="notes" label="内部备注" multiline fullWidth />
    </SimpleForm>
  </Edit>
)
