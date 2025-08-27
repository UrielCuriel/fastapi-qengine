"""
Validator for filter inputs and AST nodes.
"""
from typing import List, Dict, Any, Optional, Set
import re

from .types import (
    FilterInput, ASTNode, FieldCondition, LogicalCondition, OrderNode, FieldsNode,
    ComparisonOperator, LogicalOperator, SecurityPolicy, ValidationRule
)
from .errors import ValidationError, SecurityError
from .config import ValidatorConfig


class FilterValidator:
    """Validates filter inputs and AST nodes."""
    
    def __init__(self, config: Optional[ValidatorConfig] = None, 
                 security_policy: Optional[SecurityPolicy] = None):
        self.config = config or ValidatorConfig()
        self.security_policy = security_policy or SecurityPolicy()
        self.validation_rules: List[ValidationRule] = []
    
    def add_validation_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule."""
        self.validation_rules.append(rule)
    
    def validate_filter_input(self, filter_input: FilterInput) -> None:
        """Validate a FilterInput object."""
        errors = []
        security_errors = []
        
        # Validate where clause
        if filter_input.where is not None:
            try:
                self._validate_where_clause(filter_input.where)
            except SecurityError as e:
                security_errors.append(str(e))
            except ValidationError as e:
                errors.append(str(e))
        
        # Validate order clause
        if filter_input.order is not None:
            try:
                self._validate_order_clause(filter_input.order)
            except SecurityError as e:
                security_errors.append(str(e))
            except ValidationError as e:
                errors.append(str(e))
        
        # Validate fields clause
        if filter_input.fields is not None:
            try:
                self._validate_fields_clause(filter_input.fields)
            except SecurityError as e:
                security_errors.append(str(e))
            except ValidationError as e:
                errors.append(str(e))
        
        # Raise security errors first (they have priority)
        if security_errors:
            raise SecurityError(f"Security policy violation: {'; '.join(security_errors)}")
        
        if errors:
            raise ValidationError(f"Filter validation failed: {'; '.join(errors)}")
    
    def validate_ast_node(self, node: ASTNode) -> List[str]:
        """Validate an AST node and return list of error messages."""
        errors = []
        
        # Built-in validations
        if isinstance(node, FieldCondition):
            errors.extend(self._validate_field_condition(node))
        elif isinstance(node, LogicalCondition):
            errors.extend(self._validate_logical_condition(node))
        elif isinstance(node, OrderNode):
            errors.extend(self._validate_order_node(node))
        elif isinstance(node, FieldsNode):
            errors.extend(self._validate_fields_node(node))
        
        # Apply custom validation rules
        for rule in self.validation_rules:
            errors.extend(rule.validate(node))
        
        return errors
    
    def _validate_where_clause(self, where: Dict[str, Any], depth: int = 0) -> None:
        """Validate where clause structure and security."""
        # Check depth limit
        if depth > self.security_policy.max_depth:
            raise SecurityError(f"Query depth exceeds maximum of {self.security_policy.max_depth}")
        
        if not isinstance(where, dict):
            raise ValidationError("Where clause must be an object")
        
        for key, value in where.items():
            if key.startswith('$'):
                # Logical or comparison operator
                self._validate_operator(key, value, depth)
            else:
                # Field name
                self._validate_field_access(key)
                self._validate_field_condition_value(key, value, depth)
    
    def _validate_operator(self, operator: str, value: Any, depth: int) -> None:
        """Validate operator usage."""
        # Check if operator is allowed
        if self.security_policy.allowed_operators is not None:
            operator_enum = self._get_operator_enum(operator)
            if operator_enum and operator_enum not in self.security_policy.allowed_operators:
                raise SecurityError(f"Operator '{operator}' is not allowed")
        
        # Validate operator-specific rules
        if operator in ['$and', '$or', '$nor']:
            self._validate_logical_operator(operator, value, depth)
        elif operator in ['$in', '$nin']:
            self._validate_array_operator(operator, value)
        elif operator in ['$regex']:
            self._validate_regex_operator(operator, value)
        elif operator in ['$exists']:
            self._validate_exists_operator(operator, value)
        elif operator in ['$size']:
            self._validate_size_operator(operator, value)
        # Add more operator-specific validations as needed
    
    def _validate_logical_operator(self, operator: str, value: Any, depth: int) -> None:
        """Validate logical operator values."""
        if not isinstance(value, list):
            raise ValidationError(f"Operator '{operator}' requires an array value")
        
        if len(value) == 0:
            raise ValidationError(f"Operator '{operator}' cannot have empty array")
        
        # Recursively validate nested conditions
        for item in value:
            self._validate_where_clause(item, depth + 1)
    
    def _validate_array_operator(self, operator: str, value: Any) -> None:
        """Validate array operators like $in, $nin."""
        if not isinstance(value, list):
            raise ValidationError(f"Operator '{operator}' requires an array value")
        
        if len(value) > self.security_policy.max_array_size:
            raise SecurityError(f"Array size exceeds maximum of {self.security_policy.max_array_size}")
    
    def _validate_regex_operator(self, operator: str, value: Any) -> None:
        """Validate regex operator."""
        if not isinstance(value, str):
            raise ValidationError(f"Operator '{operator}' requires a string value")
        
        # Try to compile regex to check for validity
        try:
            re.compile(value)
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern: {e}")
    
    def _validate_exists_operator(self, operator: str, value: Any) -> None:
        """Validate exists operator."""
        if not isinstance(value, bool):
            raise ValidationError(f"Operator '{operator}' requires a boolean value")
    
    def _validate_size_operator(self, operator: str, value: Any) -> None:
        """Validate size operator."""
        if not isinstance(value, int) or value < 0:
            raise ValidationError(f"Operator '{operator}' requires a non-negative integer")
    
    def _validate_field_access(self, field_name: str) -> None:
        """Validate field access according to security policy."""
        # Check blocked fields
        if self.security_policy.blocked_fields and field_name in self.security_policy.blocked_fields:
            raise SecurityError(f"Access to field '{field_name}' is blocked")
        
        # Check allowed fields (if whitelist is defined)
        if self.security_policy.allowed_fields and field_name not in self.security_policy.allowed_fields:
            raise SecurityError(f"Access to field '{field_name}' is not allowed")
        
        # Basic field name validation
        if not isinstance(field_name, str) or not field_name:
            raise ValidationError("Field names must be non-empty strings")
    
    def _validate_field_condition_value(self, field: str, value: Any, depth: int) -> None:
        """Validate field condition value."""
        if isinstance(value, dict):
            # Complex condition with operators
            for op, op_value in value.items():
                self._validate_operator(op, op_value, depth)
        # Simple value conditions are generally allowed
    
    def _validate_order_clause(self, order: str) -> None:
        """Validate order clause."""
        if not isinstance(order, str):
            raise ValidationError("Order clause must be a string")
        
        # Parse order fields
        for field_spec in order.split(','):
            field_spec = field_spec.strip()
            if not field_spec:
                continue
            
            # Extract field name (remove - prefix for descending)
            field_name = field_spec.lstrip('-')
            self._validate_field_access(field_name)
    
    def _validate_fields_clause(self, fields: Dict[str, int]) -> None:
        """Validate fields clause."""
        if not isinstance(fields, dict):
            raise ValidationError("Fields clause must be an object")
        
        for field_name, include in fields.items():
            self._validate_field_access(field_name)
            if include not in [0, 1]:
                raise ValidationError(f"Field inclusion value must be 0 or 1, got {include}")
    
    def _validate_field_condition(self, node: FieldCondition) -> List[str]:
        """Validate a field condition node."""
        errors = []
        
        try:
            self._validate_field_access(node.field)
        except (ValidationError, SecurityError) as e:
            errors.append(str(e))
        
        return errors
    
    def _validate_logical_condition(self, node: LogicalCondition) -> List[str]:
        """Validate a logical condition node."""
        errors = []
        
        if not node.conditions:
            errors.append(f"Logical operator '{node.operator.value}' cannot have empty conditions")
        
        # Recursively validate nested conditions
        for condition in node.conditions:
            errors.extend(self.validate_ast_node(condition))
        
        return errors
    
    def _validate_order_node(self, node: OrderNode) -> List[str]:
        """Validate an order node."""
        errors = []
        
        try:
            self._validate_field_access(node.field)
        except (ValidationError, SecurityError) as e:
            errors.append(str(e))
        
        return errors
    
    def _validate_fields_node(self, node: FieldsNode) -> List[str]:
        """Validate a fields node."""
        errors = []
        
        for field_name in node.fields.keys():
            try:
                self._validate_field_access(field_name)
            except (ValidationError, SecurityError) as e:
                errors.append(str(e))
        
        return errors
    
    def _get_operator_enum(self, operator: str) -> Optional[ComparisonOperator]:
        """Get ComparisonOperator enum for string operator."""
        try:
            return ComparisonOperator(operator)
        except ValueError:
            return None
