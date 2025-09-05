# AI Agent Instructions for fastapi-qengine

## Project Overview
fastapi-qengine is an advanced query engine for FastAPI, inspired by Loopback 4's filtering system. It allows building complex queries directly from URLs with a flexible syntax, providing a more powerful and less configuration-intensive alternative to libraries like `fastapi-filter`.

### Key Features
- Flexible filter syntax supporting nested JSON in URL parameters and complete JSON string format
- Advanced query operators (`$gt`, `$gte`, `$in`, `$nin`, `$lt`, `$lte`, `$ne`, etc.)
- Logical combinations with `$and` and `$or`
- Field selection (projection) with `fields` parameter
- Dynamic sorting with `order` parameter
- Integration with Beanie/PyMongo (with plans for other ORMs)

## Architecture

The library focuses exclusively on query generation, delegating pagination to specialized libraries like `fastapi-pagination`.

Main components:
- `QueryEngine`: Processes the `filter` parameter from requests and converts it to Beanie queries
- Filter parsing system that supports both URL parameter format and stringified JSON format

## Development Workflow

### Setup
1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Testing
The testing approach for this project isn't explicitly defined in the current files. When implementing tests, focus on validating:
- URL parameter parsing
- JSON string parsing
- Conversion to Beanie/PyMongo queries
- Proper handling of operators and logical combinations

## Conventions & Patterns

### Query Syntax
The library supports two formats for passing filters:

1. **Nested URL Parameters**: (For simple queries)
   - Example: `/products?filter[where][price][$gt]=50`

2. **Stringified JSON**: (For complex queries with logical operators)
   - Example: `filter={"where":{"$or":[{"category":"electronics"},{"price":{"$lt":20}}]}}`

### Filter Structure
The filter object accepts these keys (inspired by Loopback):
- `where`: Defines search conditions using PyMongo operator syntax
- `order`: String for sorting results (prefix `-` for descending order)
- `fields`: Object specifying which fields to include in results

## Integration Points
- **FastAPI**: Uses FastAPI's dependency injection system
- **Beanie/PyMongo**: Currently targets Beanie's query system
- **fastapi-pagination**: Recommended for pagination integration

## Recommended Coding Approaches
When implementing features for this library:
1. Maintain compatibility with both filter formats (nested and JSON string)
2. Follow PyMongo query syntax conventions
3. Keep the library focused on query generation without incorporating pagination logic
4. Ensure backwards compatibility with Loopback 4's filter specification where possible
