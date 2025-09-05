---
title: 'core.validator'
description: 'Validator for filter inputs and AST nodes.'
navigation:
    title: 'core.validator'
    icon: 'i-codicon-library'
---

Validator for filter inputs and AST nodes.

## FilterValidator
::reference-header
---
description: >
    Validates filter inputs and AST nodes.
lang: 'python'
type: 'class'
navigation:
    title: 'FilterValidator'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class FilterValidator()
```

Validates filter inputs and AST nodes.

### add_validation_rule
::reference-header
---
description: >
    Add a custom validation rule.
lang: 'python'
type: 'method'
navigation:
    title: 'add_validation_rule'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def add_validation_rule(rule: ValidationRule) -> None
```

Add a custom validation rule.

### validate_filter_input
::reference-header
---
description: >
    Validate a FilterInput object for security and structural correctness.
lang: 'python'
type: 'method'
navigation:
    title: 'validate_filter_input'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def validate_filter_input(filter_input: FilterInput) -> None
```

Validate a FilterInput object for security and structural correctness.
This method performs comprehensive validation of all components within a FilterInput
object, including where clauses, order clauses, and fields clauses. It prioritizes
security violations over general validation errors.

**Arguments**:

- `filter_input` _FilterInput_ - The filter input object to validate containing
  optional where, order, and fields clauses.

**Raises**:

- `SecurityError` - If any security policy violations are detected in any clause.
  This exception takes priority over ValidationError and includes all
  security issues found across all clauses.
- `ValidationError` - If structural or syntax validation fails for any clause.
  Only raised if no security errors are present.

**Notes**:

  - Security errors are collected and raised together with priority over
  validation errors
  - All clauses are validated even if earlier ones fail, to provide
  comprehensive error reporting
  - None values for optional clauses (where, order, fields) are safely ignored

### _validate_all_clauses
::reference-header
---
description: >
    Validate all clauses in the filter input and collect errors.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_all_clauses'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_all_clauses(filter_input: FilterInput, errors: List[str],
                          security_errors: List[str]) -> None
```

Validate all clauses in the filter input and collect errors.

### _validate_clause
::reference-header
---
description: >
    Validate a single clause and collect any errors.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_clause'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_clause(clause_value: Any, validation_method: Callable[[Any],
                                                                    None],
                     errors: List[str], security_errors: List[str]) -> None
```

Validate a single clause and collect any errors.

### _raise_collected_errors
::reference-header
---
description: >
    Raise collected errors, prioritizing security errors.
lang: 'python'
type: 'method'
navigation:
    title: '_raise_collected_errors'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _raise_collected_errors(errors: List[str],
                            security_errors: List[str]) -> None
```

Raise collected errors, prioritizing security errors.

### validate_ast_node
::reference-header
---
description: >
    Validate an AST node and return list of error messages.
lang: 'python'
type: 'method'
navigation:
    title: 'validate_ast_node'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def validate_ast_node(node: ASTNode) -> List[str]
```

Validate an AST node and return list of error messages.

### _validate_where_clause
::reference-header
---
description: >
    Validate where clause structure and security.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_where_clause'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_where_clause(where: Dict[str, Any], depth: int = 0) -> None
```

Validate where clause structure and security.

### _validate_operator
::reference-header
---
description: >
    Validate operator usage.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_operator(operator: str, value: Any, depth: int) -> None
```

Validate operator usage.

### _validate_logical_operator
::reference-header
---
description: >
    Validate logical operator values.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_logical_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_logical_operator(operator: str, value: Any, depth: int) -> None
```

Validate logical operator values.

### _validate_array_operator
::reference-header
---
description: >
    Validate array operators like $in, $nin.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_array_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_array_operator(operator: str, value: Any) -> None
```

Validate array operators like $in, $nin.

### _validate_regex_operator
::reference-header
---
description: >
    Validate regex operator.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_regex_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_regex_operator(operator: str, value: Any) -> None
```

Validate regex operator.

### _validate_exists_operator
::reference-header
---
description: >
    Validate exists operator.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_exists_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_exists_operator(operator: str, value: Any) -> None
```

Validate exists operator.

### _validate_size_operator
::reference-header
---
description: >
    Validate size operator.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_size_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_size_operator(operator: str, value: Any) -> None
```

Validate size operator.

### _validate_field_access
::reference-header
---
description: >
    Validate field access according to security policy.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_field_access'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_field_access(field_name: str) -> None
```

Validate field access according to security policy.

### _validate_field_condition_value
::reference-header
---
description: >
    Validate field condition value.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_field_condition_value'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_field_condition_value(field: str, value: Any,
                                    depth: int) -> None
```

Validate field condition value.

### _validate_order_clause
::reference-header
---
description: >
    Validate order clause.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_order_clause'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_order_clause(order: str) -> None
```

Validate order clause.

### _validate_fields_clause
::reference-header
---
description: >
    Validate fields clause.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_fields_clause'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_fields_clause(fields: Dict[str, int]) -> None
```

Validate fields clause.

### _validate_field_condition
::reference-header
---
description: >
    Validate a field condition node.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_field_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_field_condition(node: FieldCondition) -> List[str]
```

Validate a field condition node.

### _validate_logical_condition
::reference-header
---
description: >
    Validate a logical condition node.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_logical_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_logical_condition(node: LogicalCondition) -> List[str]
```

Validate a logical condition node.

### _validate_order_node
::reference-header
---
description: >
    Validate an order node.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_order_node'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_order_node(node: OrderNode) -> List[str]
```

Validate an order node.

### _validate_fields_node
::reference-header
---
description: >
    Validate a fields node.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_fields_node'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_fields_node(node: FieldsNode) -> List[str]
```

Validate a fields node.

### _get_operator_enum
::reference-header
---
description: >
    Get ComparisonOperator enum for string operator.
lang: 'python'
type: 'method'
navigation:
    title: '_get_operator_enum'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _get_operator_enum(operator: str) -> Optional[ComparisonOperator]
```

Get ComparisonOperator enum for string operator.

