# Code Patterns: Agent PM

**Project**: Agent PM
**Generated**: 2025-10-27T18:45:32.983274

---

## Architecture Patterns

### Three-Layer Architecture

**Category**: architecture

Models → Adapters → Methods pattern for database operations


---

### Database-First

**Category**: data

All data operations go through database, not files


---

### Template-Based Generation

**Category**: code-generation

Use Jinja2 templates for code generation, not f-strings


---


## Project Conventions

- **Testing**: >90% coverage, AAA pattern, project-relative paths
- **Database**: Three-layer pattern (Models → Adapters → Methods)
- **Templates**: Jinja2 for code generation, not f-strings
- **Documentation**: Use `apm document add` for all docs (DOC-020)
- **Quality**: SOLID principles, type hints, docstrings

---

**Generated**: 2025-10-27T18:45:32.983274
**Source**: APM Database (project metadata)
