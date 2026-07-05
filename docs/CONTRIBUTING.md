# Contributing Guide

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Follow development setup in SETUP_GUIDE.md

## Code Standards

### Python Backend

- Follow PEP 8
- Use type hints
- Keep functions small and focused
- Write docstrings for public functions
- Run linter: `pylint backend`
- Format code: `black backend`

### React Frontend

- Use functional components with hooks
- Follow React best practices
- Use Redux for state management
- Add PropTypes or TypeScript
- Run linter: `npm run lint`
- Format code: `npm run format`

## Git Workflow

### Branch Naming

- Features: `feature/description`
- Bug fixes: `fix/description`
- Documentation: `docs/description`

### Commit Messages

```
type(scope): Brief description

Detailed explanation if needed.
References #123
```

Types: feat, fix, docs, style, refactor, test, chore

### Pull Requests

1. Describe changes clearly
2. Link related issues
3. Ensure all tests pass
4. Request code review
5. Address feedback

## Testing

### Python Tests

```bash
pytest tests/
pytest tests/unit/ -v
pytest tests/integration/
```

### Frontend Tests

```bash
npm test
npm test -- --coverage
```

### Coverage Requirements

- Aim for 80%+ coverage
- All critical paths must be tested

## Documentation

- Update API docs for endpoint changes
- Document new configuration options
- Update architecture docs for major changes
- Add docstrings to new functions

## Reporting Issues

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error logs or screenshots

## Code Review Process

1. Automated checks must pass (linting, tests)
2. At least one approval required
3. Address feedback and re-request review
4. Squash commits before merge
5. Merge to main branch

## Release Process

1. Update version in appropriate files
2. Update CHANGELOG
3. Create git tag
4. Create GitHub release
5. Deploy to production

## Questions?

- Check existing issues and discussions
- Review documentation
- Create a new issue for bugs/features
- Join discussion channels
