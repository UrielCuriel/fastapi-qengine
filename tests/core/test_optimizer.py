from fastapi_qengine.core.config import OptimizerConfig
from fastapi_qengine.core.optimizer import ASTOptimizer
from fastapi_qengine.core.types import (
    ASTNode,
    ComparisonOperator,
    FieldCondition,
    FilterAST,
    LogicalCondition,
    LogicalOperator,
    OrderNode,
)


class TestASTOptimizer:
    def test_init_with_default_config(self):
        optimizer = ASTOptimizer()
        assert optimizer.config is not None
        assert isinstance(optimizer.config, OptimizerConfig)

    def test_init_with_custom_config(self):
        config = OptimizerConfig(enabled=False)
        optimizer = ASTOptimizer(config)
        assert optimizer.config == config

    def test_optimize_disabled(self):
        config = OptimizerConfig(enabled=False)
        optimizer = ASTOptimizer(config)

        ast = FilterAST(where=FieldCondition(field="name", operator=ComparisonOperator.EQ, value="test"))

        result = optimizer.optimize(ast)
        assert result is ast  # Should return the same instance when disabled

    def test_optimize_empty_ast(self):
        optimizer = ASTOptimizer()
        ast = FilterAST()

        result = optimizer.optimize(ast)
        assert result is not ast  # Should be a copy
        assert result.where is None
        assert result.order == []
        assert result.fields is None

    def test_optimize_node_field_condition(self):
        optimizer = ASTOptimizer()
        field_condition = FieldCondition(field="price", operator=ComparisonOperator.GT, value=10)

        result = optimizer._optimize_node(field_condition)
        # Field conditions are currently returned as-is
        assert result == field_condition

    def test_optimize_logical_condition_empty(self):
        optimizer = ASTOptimizer()
        logical_condition = LogicalCondition(operator=LogicalOperator.AND, conditions=[])

        result = optimizer._optimize_node(logical_condition)
        assert result is None  # Empty logical conditions are removed

    def test_optimize_logical_condition_single_child(self):
        optimizer = ASTOptimizer()
        field_condition = FieldCondition(field="price", operator=ComparisonOperator.GT, value=10)
        logical_condition = LogicalCondition(operator=LogicalOperator.AND, conditions=[field_condition])

        result = optimizer._optimize_node(logical_condition)
        assert result == field_condition  # Logical condition with single child is flattened

    def test_simplify_logical_operators(self):
        optimizer = ASTOptimizer()

        # Create a nested AND condition
        inner_and = LogicalCondition(
            operator=LogicalOperator.AND,
            conditions=[
                FieldCondition(field="price", operator=ComparisonOperator.GT, value=10),
                FieldCondition(field="stock", operator=ComparisonOperator.GT, value=0),
            ],
        )

        outer_condition = LogicalCondition(
            operator=LogicalOperator.AND,
            conditions=[inner_and, FieldCondition(field="active", operator=ComparisonOperator.EQ, value=True)],
        )

        result = optimizer._optimize_node(outer_condition)

        # Should flatten the nested AND into a single AND with 3 conditions
        assert isinstance(result, LogicalCondition)
        assert result.operator == LogicalOperator.AND
        assert len(result.conditions) == 3

    def test_remove_redundant_conditions(self):
        optimizer = ASTOptimizer(OptimizerConfig(remove_redundant_conditions=True))
        # Create conditions with a duplicate
        conditions: list[ASTNode] = [
            FieldCondition(field="price", operator=ComparisonOperator.GT, value=10),
            FieldCondition(field="price", operator=ComparisonOperator.GT, value=10),  # Duplicate
            FieldCondition(field="stock", operator=ComparisonOperator.GT, value=0),
        ]

        logical_condition = LogicalCondition(operator=LogicalOperator.AND, conditions=conditions)

        result = optimizer._optimize_node(logical_condition)

        # Should have removed the duplicate condition
        assert isinstance(result, LogicalCondition)
        assert len(result.conditions) == 2

    def test_optimize_order_nodes(self):
        optimizer = ASTOptimizer()

        # Create order with duplicates
        order_nodes = [
            OrderNode(field="name", ascending=True),
            OrderNode(field="price", ascending=False),
            OrderNode(field="name", ascending=False),  # Duplicate field
        ]

        ast = FilterAST(order=order_nodes)
        result = optimizer.optimize(ast)

        # Should keep only the first occurrence of each field
        assert result.order is not None
        assert len(result.order) == 2
        assert result.order[0].field == "name"
        assert result.order[1].field == "price"

    def test_nodes_equal_field_conditions(self):
        optimizer = ASTOptimizer()

        node1 = FieldCondition(field="price", operator=ComparisonOperator.GT, value=10)
        node2 = FieldCondition(field="price", operator=ComparisonOperator.GT, value=10)
        node3 = FieldCondition(field="price", operator=ComparisonOperator.GT, value=20)

        assert optimizer._nodes_equal(node1, node2) is True
        assert optimizer._nodes_equal(node1, node3) is False

    def test_nodes_equal_logical_conditions(self):
        optimizer = ASTOptimizer()

        node1 = LogicalCondition(
            operator=LogicalOperator.AND,
            conditions=[
                FieldCondition(field="price", operator=ComparisonOperator.GT, value=10),
                FieldCondition(field="stock", operator=ComparisonOperator.GT, value=0),
            ],
        )

        # Same conditions but different order (AND is commutative)
        node2 = LogicalCondition(
            operator=LogicalOperator.AND,
            conditions=[
                FieldCondition(field="stock", operator=ComparisonOperator.GT, value=0),
                FieldCondition(field="price", operator=ComparisonOperator.GT, value=10),
            ],
        )

        # Different operator
        node3 = LogicalCondition(
            operator=LogicalOperator.OR,
            conditions=[
                FieldCondition(field="price", operator=ComparisonOperator.GT, value=10),
                FieldCondition(field="stock", operator=ComparisonOperator.GT, value=0),
            ],
        )

        assert optimizer._nodes_equal(node1, node2) is True  # Should be equal despite order
        assert optimizer._nodes_equal(node1, node3) is False  # Different operator

    def test_get_condition_key(self):
        optimizer = ASTOptimizer()

        field_condition = FieldCondition(field="price", operator=ComparisonOperator.GT, value=10)
        key = optimizer._get_condition_key(field_condition)
        assert isinstance(key, str)
        assert "field:price:$gt:10" in key

        logical_condition = LogicalCondition(operator=LogicalOperator.AND, conditions=[field_condition])
        key = optimizer._get_condition_key(logical_condition)
        assert isinstance(key, str)
        assert "logical:$and" in key

    def test_multiple_optimization_passes(self):
        # Test that multiple optimization passes work correctly
        config = OptimizerConfig(max_optimization_passes=3)
        optimizer = ASTOptimizer(config)

        # Create a nested condition that requires multiple passes to fully optimize
        condition1 = FieldCondition(field="price", operator=ComparisonOperator.GT, value=10)
        inner_and = LogicalCondition(operator=LogicalOperator.AND, conditions=[condition1])
        middle_and = LogicalCondition(operator=LogicalOperator.AND, conditions=[inner_and])
        outer_and = LogicalCondition(operator=LogicalOperator.AND, conditions=[middle_and])

        ast = FilterAST(where=outer_and)
        result = optimizer.optimize(ast)

        # After optimization, should be flattened to just the original field condition
        assert result.where == condition1

    def test_combine_range_conditions_disabled(self):
        config = OptimizerConfig(combine_range_conditions=False)
        optimizer = ASTOptimizer(config)

        conditions: list[ASTNode] = [
            FieldCondition(field="price", operator=ComparisonOperator.GT, value=10),
            FieldCondition(field="price", operator=ComparisonOperator.LT, value=100),
        ]

        result = optimizer._combine_range_conditions(conditions)
        # When disabled, should return the original list
        assert result == conditions
