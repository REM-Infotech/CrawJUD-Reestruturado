# Pull Request Guidelines

> Portuguese version available [here](./doc/PR_GUIDELINES.md)

## General Best Practices

- Keep PRs small and focused on a single feature/fix
- Use clear and descriptive titles
- Include detailed description of changes
- Reference related issues using #issue_number
- Ensure all tests pass before submitting
- Keep commit history clean and organized

## Formatting and Style

- Follow project's code standards
- Include comments when necessary
- Remove commented code and debug logs
- Update documentation when relevant

## Review Process

1. Request review from at least one project maintainer
2. Respond to comments constructively
3. Make requested changes in new commits
4. Squash commits after approval

## Workflow Limits

The project workflows have the following limits:

- Maximum PR size: 300 changed files
- Line change limit: 1000 lines
- Maximum test execution time: 15 minutes

### When Limits Are Exceeded

If your PR exceeds any of the above limits:

1. **PR Size**
   - Split PR into multiple smaller PRs
   - Focus each PR on a specific feature
   - Create a tracking issue to coordinate related PRs

2. **Line Limit**
   - Review for duplicate code that can be refactored
   - Consider creating shared libraries for common code
   - Split changes into smaller PRs

3. **Execution Time**
   - Check for tests that can be optimized
   - Consider moving long tests to a separate suite
   - Consult team to evaluate infrastructure adjustment needs

## Final Checklist

- [ ] PR has clear title and description
- [ ] Code follows project standards
- [ ] Tests have been added/updated
- [ ] Documentation has been updated
- [ ] PR is within established limits
- [ ] Reviewers have been assigned
