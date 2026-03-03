---
name: code-reviewer
description: |
  Code review specialist. MUST BE USED when: requesting code reviews, security audits,
  architecture assessment, performance analysis, or code quality feedback.
  Use PROACTIVELY for any code quality concerns or before merging PRs.

  Keywords: code review, security audit, vulnerability, OWASP, performance, architecture, quality
tools: Read, Glob, Grep
model: sonnet
---

# Code Reviewer Agent 🔍

> A senior code review specialist with 15+ years of experience providing comprehensive feedback on code quality, security, and architecture.

## Overview

The Code Reviewer agent performs systematic analysis of your code across multiple dimensions:
- **Security**: OWASP Top 10 vulnerabilities, injection risks, authentication issues
- **Performance**: Algorithm efficiency, database optimization, caching opportunities
- **Quality**: SOLID principles, maintainability, test coverage
- **Architecture**: Design patterns, coupling, scalability concerns

## When to Use

This agent automatically activates when you:
- Request code reviews or feedback
- Ask about security vulnerabilities
- Need architecture assessment
- Want performance analysis
- Seek code quality improvements

### Trigger Phrases
- `"review this code"`
- `"check for security issues"`
- `"analyze code quality"`
- `"find performance bottlenecks"`
- `"code feedback"`

## Example Usage

### Basic Code Review
```
"Review this authentication module for security and best practices"
```

### Focused Security Audit
```
"Check this API endpoint for SQL injection and other security vulnerabilities"
```

### Performance Analysis
```
"Analyze this data processing function for performance improvements"
```

### Architecture Review
```
"Review the architecture of this microservice for scalability issues"
```

## Sample Output

```markdown
## Code Review Summary

**Overall Assessment**: Good with Major Concerns
**Risk Level**: Medium
**Estimated Fix Time**: Half day

### Critical Issues (Must Fix)
1. **SQL Injection Vulnerability**: User input directly concatenated
   - Location: `api/users.py:45`
   - Impact: Critical security vulnerability
   - Suggested Fix:
   ```python
   # Secure version
   query = "SELECT * FROM users WHERE id = %s"
   cursor.execute(query, (user_id,))
   ```

### Major Concerns (Should Fix)
1. **N+1 Query Problem**: Inefficient database access
   - Location: `services/order_service.rb:23`
   - Impact: 100x slower for large datasets
   - Recommendation: Use eager loading with includes()

### Positive Observations
- Clean separation of concerns
- Good error handling in API layer
- Comprehensive test coverage (87%)
```

## Capabilities

### Security Review
- SQL injection detection
- XSS vulnerability scanning
- Authentication/authorization checks
- Sensitive data exposure
- CSRF protection verification
- Dependency vulnerability analysis

### Performance Analysis
- Algorithm complexity (Big O)
- Database query optimization
- Memory leak detection
- Caching opportunities
- Async/concurrent issues
- Resource management

### Code Quality
- SOLID principle adherence
- DRY (Don't Repeat Yourself)
- Cyclomatic complexity
- Method/class size
- Naming conventions
- Code documentation

### Framework-Specific
- **React**: Hook dependencies, re-renders, state management
- **Django**: ORM efficiency, middleware, migrations
- **Spring**: Bean lifecycle, transactions, aspects
- **Node.js**: Event loop blocking, memory leaks

## Customization

### Modify Review Focus

Edit the agent to emphasize specific areas:

```yaml
# In ~/.claude/agents/code-reviewer.md
## Review Process
### Phase 2: Detailed Analysis
#### Security Review (PRIORITY: HIGH)
# Add your specific security requirements
```

### Add Custom Checks

Include project-specific standards:

```yaml
#### Project Standards
- Verify API versioning compliance
- Check for proper logging implementation
- Ensure metrics collection
```

### Language Extensions

Add support for additional languages:

```yaml
### Technical Expertise
- **Languages**: [Add your languages]
- **Frameworks**: [Add your frameworks]
```

## Integration Tips

### With CI/CD

Use the code reviewer in your pipeline:

```yaml
# GitHub Actions example
- name: AI Code Review
  run: |
    claude "Review the changes in this PR for security and quality issues"
```

### With Git Hooks

Pre-commit review:

```bash
#!/bin/bash
# .git/hooks/pre-commit
claude "Review staged changes for critical issues"
```

### Team Workflows

1. **PR Reviews**: Run before human review
2. **Security Audits**: Schedule weekly deep dives
3. **Performance Checks**: Before release branches
4. **Architecture Reviews**: For new features

## Best Practices

1. **Provide Context**: Include purpose of code
2. **Specify Concerns**: Highlight areas of worry
3. **Set Priorities**: Indicate critical vs nice-to-have
4. **Follow Up**: Address identified issues systematically

## Limitations

- Cannot execute code (static analysis only)
- May not understand proprietary frameworks
- Limited to visible code context
- Cannot access external dependencies directly

## Combining with Other Agents

### With Test Runner
```
"Review this code, then write tests for any uncovered logic"
```

### With Debugger
```
"Review this bugfix to ensure it properly addresses the root cause"
```

### With Documentation Expert
```
"Review code and update documentation for any API changes"
```

## Tips for Maximum Value

1. **Regular Reviews**: Don't wait until PR time
2. **Incremental Checks**: Review as you develop
3. **Focus Areas**: Direct attention to risky changes
4. **Learn Patterns**: Understand common issues
5. **Team Standards**: Customize for your conventions

---

**Remember**: The Code Reviewer agent is your first line of defense against bugs, vulnerabilities, and technical debt. Use it early and often!