# Cursor IDE Rules

## Overview

This directory contains the configuration files for Cursor IDE rules applied to the Productivity Software project. These rules enforce consistent coding standards, development workflows, and best practices across the team.

## Directory Structure

- `.cursor/rules.json` - Main configuration file that references all rule categories
- `.cursor/rules/` - Directory containing individual rule category files:
  - `code_organization.json` - Project structure, file naming, and import standards
  - `development_workflow.json` - Git workflow, code reviews, and environment management
  - `coding_standards.json` - Python, JavaScript/TypeScript, and code quality standards
  - `testing_standards.json` - Test coverage, organization, and workflow standards
  - `tdd_rules.json` - Test-Driven Development practices and requirements
  - `ide_workflows.json` - Cursor-specific workflows for TDD and code proposals
  - `requirements_traceability.json` - Rules for aligning code with formal requirements
  - `request_requirements_alignment.json` - Rules for aligning API endpoints with requirements
  - `request_workflow_alignment.json` - Rules for aligning request lifecycles with requirements
  - `code_requirements_alignment.json` - Rules for ensuring code implementations match requirements
  - `documentation_standards.json` - Code documentation, project documentation, and comments
  - `performance_optimization.json` - Query optimization, frontend performance, and resource management
  - `accessibility_security.json` - WCAG compliance, accessibility testing, and security practices
  - `cursor_specific.json` - Cursor-specific features, shortcuts, and collaboration standards

## Rule Structure

Each rule file follows a consistent structure:

```json
{
  "name": "Rule Category Name",
  "description": "Description of the rule category",
  "rules": [
    {
      "id": "rule-id",
      "name": "Rule Name",
      "description": "Description of the rule",
      "guidelines": [
        "Guideline 1",
        "Guideline 2"
      ],
      "severity": "error|warning|info",
      "configuration": {
        // Rule-specific configuration options
      }
    }
  ]
}
```

## Severity Levels

- `error` - Critical rules that must be followed; violations block code commits
- `warning` - Important rules that should be followed; violations generate warnings
- `info` - Helpful guidelines that are recommended but not enforced

## Usage

1. **Viewing Rules**: Open any rule file to view the specific guidelines
2. **Disabling Rules**: Add `cursor-disable rule-id` comments to temporarily disable specific rules
3. **Configuring Rules**: Edit the configuration section of specific rules to adjust their behavior
4. **Adding Rules**: Create new rule files in the `.cursor/rules/` directory and reference them in `rules.json`

## Test-Driven Development (TDD)

The project follows a strict Test-Driven Development approach:

1. **Tests First**: Write test cases before implementing any functionality
2. **Red-Green-Refactor**: Start with failing tests, implement code to make them pass, then refactor
3. **Coverage Requirements**: Maintain high test coverage for all code, especially core functionality
4. **Test Isolation**: Ensure tests are independent and can run in any order

Cursor will enforce these TDD practices through:
- Requiring test files before implementation files
- Ensuring all code has corresponding tests
- Enforcing minimum test coverage thresholds
- Detecting test dependencies and isolation issues

## Cursor IDE Workflows

Cursor's unique capabilities are leveraged to reinforce Test-Driven Development:

1. **Test-First Workflow**: The IDE enforces writing test files before implementation files
2. **Code Proposal Validation**: AI-generated code is only accepted if it passes tests
3. **Continuous Testing**: Automatic test runs on save ensure immediate feedback
4. **AI-Assisted Testing**: Use Cursor's AI to suggest test cases and improvements
5. **Split-Pane Layout**: Optimized editor layout for viewing tests and implementation side by side

For code implementation:
- Write test cases first with expected functionality
- Use Cursor's AI to propose multiple implementation options
- Run tests against each proposal
- Only accept code that passes all tests
- Request refinements for failing implementations
- Document the chosen implementation

## Requirements Traceability

The project enforces strict alignment between code and formal requirements documentation:

1. **Requirement References**: All code must reference the specific requirements it implements
2. **Verification**: Tests must verify requirements are correctly implemented
3. **Commit Traceability**: Commit messages must reference relevant requirements
4. **Implementation Alignment**: Code must strictly follow requirements specifications
5. **Change Impact**: Requirement changes must be tracked in code

Implementation practices:
- Use `@requirement` tags to link code to requirement documents
- Name tests to reflect the requirements they verify
- Reference requirement IDs in commit messages as `[REQ-XXX]`
- Document deviations from requirements with explicit justification
- Track requirement versions and updates in code comments

## Request Requirements Alignment

The project enforces strict alignment between API endpoints/requests and requirements:

1. **API Endpoint Alignment**: Endpoints must match specifications in requirements
2. **Request Validation**: Validation must enforce all rules defined in requirements
3. **Schema Conformance**: Request/response structures must follow requirement schemas
4. **Error Handling**: Error responses must adhere to requirements documentation
5. **HTTP Client Implementation**: Client code must align with API requirements

Implementation practices:
- Use `@api-requirement` tags to link endpoints to requirement specifications
- Validate request parameters according to requirements
- Ensure response structures match documented formats
- Implement all specified error scenarios
- Reference error codes defined in requirements

## Request Workflow Alignment

The project enforces alignment between request processing workflows and requirements:

1. **Request Lifecycle**: Request processing flow must follow the sequence defined in requirements
2. **Processing Rules**: Business rules for request processing must implement requirements exactly
3. **Security Measures**: Security checks for requests must follow security requirements
4. **Cross-Service Requests**: Requests between services must adhere to integration requirements
5. **Performance Requirements**: Request processing must meet performance specifications

Implementation practices:
- Document request flow states and transitions according to requirements
- Implement timeout and retry policies as specified in requirements
- Follow validation sequencing from requirements documentation
- Apply rate limiting and throttling as specified
- Implement circuit breaking and fallback mechanisms according to requirements
- Ensure request processing meets performance metrics

## Code Requirements Alignment

The project enforces comprehensive alignment between code implementations and requirements:

1. **Implementation Alignment**: Code must implement the exact functionality specified in requirements
2. **Algorithm Conformance**: Algorithms and business logic must match requirement specifications
3. **Data Model Alignment**: Database schemas and models must follow requirements documentation
4. **UI/UX Conformance**: User interfaces must match design specifications in requirements
5. **System Integration**: Integration interfaces must align with requirements
6. **Requirement Changes**: Code updates must track and reflect changes in requirements

Implementation practices:
- Document implementation decisions that relate to requirements
- Implement business logic exactly as specified in requirements
- Ensure database schemas match data models in requirements
- Build UI components according to design specifications
- Include references to requirements in all major code components
- Track and document the impact of requirement changes on code

## Integration

These rules are automatically applied in the Cursor IDE when working with this project. The IDE will highlight rule violations directly in the editor, provide suggestions for fixes, and prevent committing code that violates critical rules.

## Customization

To customize these rules for your specific needs:

1. Edit the severity levels in individual rule definitions
2. Modify the configuration options to adjust rule behavior
3. Enable or disable entire rule categories in the main `rules.json` file
4. Add project-specific rules as needed

## Additional Resources

- [Cursor IDE Documentation](https://cursor.sh/docs)
- [Project-Specific Guidelines](../documentation/Cursor_Rules.md)

## Cursor Development Rules

This directory contains configuration files that define rules and standards for our development process, integrated with the Cursor IDE.

### Rules Overview

These rules aim to maintain high quality and consistency in our codebase by:

1. **Code Organization** - Enforcing consistent file structure and organization
2. **Development Workflow** - Ensuring proper Git workflow and CI/CD integration
3. **Coding Standards** - Maintaining code style and quality standards
4. **Testing Standards** - Enforcing test coverage and testing practices
5. **Test-Driven Development** - Guidelines for TDD process
6. **IDE Workflows** - Best practices for using Cursor features
7. **Requirements Traceability** - Ensuring code aligns with formal requirements
8. **Request Requirements Alignment** - Ensuring API endpoints align with requirements 
9. **Code Requirements Alignment** - Ensuring code implementations match requirements
10. **Request Workflow Alignment** - Ensuring request processing workflows follow requirements
11. **Documentation Standards** - Maintaining documentation quality
12. **Performance Optimization** - Guidelines for performance considerations
13. **Accessibility & Security** - Standards for accessibility and security
14. **Cursor-Specific Features** - Specialized rules for Cursor IDE features

### Test-Driven Development Rules

The Test-Driven Development (TDD) rules ensure that proper test-driven practices are followed in our development process. These rules enforce:

- **Test Coverage**: Ensuring new code has corresponding test files with adequate coverage
- **Test-First Approach**: Writing tests before implementation (Red-Green-Refactor cycle)
- **Test Structure**: Proper naming and organization of test files, classes, and methods
- **Test Independence**: Ensuring tests don't rely on each other's state
- **Test Requirements Traceability**: Linking tests back to requirements documentation
- **Mocking Dependencies**: Proper isolation of the system under test
- **Performance Testing**: Validating response times for critical functionality

To use these rules effectively:
1. Write your tests first for any new feature or functionality
2. Ensure tests properly reference the requirements they validate
3. Follow proper naming conventions for test classes and methods
4. Categorize tests appropriately as unit or integration tests
5. Maintain a minimum of 80% code coverage for new features

### Request Workflow Alignment

The Request Workflow Alignment rules ensure that request processing flows adhere to the sequences, state transitions, and processing rules defined in the formal requirements.

These rules verify:

- **Request Lifecycle Compliance**: Request workflows must follow the precise sequence defined in requirements
- **State Machine Implementation**: State transitions for requests must exactly match the state machine defined in requirements
- **Business Rule Implementation**: Business rules for request processing must implement requirements exactly
- **Security Measures**: Authentication, authorization, and other security measures must be implemented as specified
- **Performance Requirements**: Request processing must meet performance metrics defined in requirements

**Implementation Practices**:

- Document request flow states and transitions explicitly
- Include requirement references in state transition code
- Implement timeout and retry policies as specified in requirements
- Use circuit breakers for external service calls as defined in requirements
- Ensure request processing meets documented performance metrics

### Usage

Cursor will automatically enforce these rules during development. Rules can be individually enabled or disabled in the `rules.json` configuration file.

### Adding New Rules

To add new rules:

1. Create a new rule file in the `rules/` directory
2. Add the rule to the `rules.json` file
3. Document the rule in this README

### Disabling Rules Inline

To disable a rule for a specific section of code, use:

```typescript
// cursor-disable rule-id
code that would normally trigger the rule
// cursor-enable rule-id
``` 