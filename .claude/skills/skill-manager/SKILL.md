---
name: skill-manager
description: Efficient management and deployment of Claude Code skills and marketplace. Automates marketplace initialization, skill updates, Git workflows, version management, and release notes with proper Git conventions.
---

# Skill Manager

Complete automation for Claude Code skills and marketplace management. Handles initialization, updates, Git deployment, versioning, and release management with proper Git conventions.

## When to Use This Skill

Use this skill when:
- Setting up a new Claude Code marketplace
- Adding new skills to existing marketplace
- Updating skill metadata or versions
- Publishing skills to Git repository
- Managing semantic versioning
- Generating release notes and changelogs
- Validating marketplace configuration

## Core Workflows

### Workflow 1: Initialize Marketplace

**Trigger Condition**: Only run when `.claude-plugin/marketplace.json` does NOT exist.

**Purpose**: Set up a new Claude Code marketplace from scratch.

**Steps**:

1. **Check for existing marketplace**
   ```bash
   # If this file exists, skip initialization
   test -f .claude-plugin/marketplace.json
   ```

2. **Gather marketplace information** (via AskUserQuestion):
   - Marketplace name (e.g., "my-skills")
   - Display name (e.g., "My Skills Marketplace")
   - Owner name
   - Owner URL (GitHub profile)
   - Description

3. **Create marketplace.json**
   - Use template: `templates/marketplace.json.template`
   - Fill in gathered information
   - Set initial version: 1.0.0
   - Create empty plugins array

4. **Initialize Git repository** (if not already initialized):
   ```bash
   git init
   git remote add origin <repository-url>
   ```

5. **Create initial README** with marketplace installation instructions

6. **Create .gitignore** (if not exists):
   ```
   __pycache__/
   *.pyc
   .DS_Store
   node_modules/
   ```

7. **Report completion**:
   ```
   ✅ Marketplace initialized successfully!

   📦 Marketplace: <name>
   📍 Location: .claude-plugin/marketplace.json
   🔗 Repository: <url>

   Next steps:
   - Add skills with: /skill-manager add-skill
   - Publish with: /skill-manager publish
   ```

---

### Workflow 2: Add New Skill to Marketplace

**Purpose**: Add a new skill with proper plugin.json and marketplace registration.

**Steps**:

1. **Gather skill information** (via AskUserQuestion):
   - Skill name (folder name, e.g., "my-new-skill")
   - Display name (e.g., "My New Skill")
   - Description (1-2 sentences)
   - Category (select from: Project Initialization, AI Integration, Documentation, Prompt Tools, Development Tools, UI/UX Development, Other)
   - Keywords (comma-separated, e.g., "automation, workflow, productivity")
   - Version (default: 1.0.0)

2. **Check if skill folder exists**:
   ```bash
   test -d <skill-name>
   ```
   - If NOT exists: Suggest creating with `/skill-creator` first
   - If exists: Continue

3. **Check if SKILL.md exists**:
   ```bash
   test -f <skill-name>/SKILL.md
   ```
   - If NOT exists: Error and exit
   - If exists: Continue

4. **Create plugin.json**:
   - Create `.claude-plugin` directory in skill folder
   - Use template: `templates/plugin.json.template`
   - Fill in gathered information
   - Extract author from marketplace owner

5. **Update marketplace.json**:
   - Read existing `.claude-plugin/marketplace.json`
   - Add new plugin entry to `plugins` array:
     ```json
     {
       "name": "<skill-name>",
       "source": "./<skill-name>",
       "description": "<description>",
       "version": "<version>",
       "category": "<category>",
       "keywords": ["<keyword1>", "<keyword2>"]
     }
     ```
   - Sort plugins alphabetically by name
   - Write updated marketplace.json

6. **Report completion**:
   ```
   ✅ Skill added to marketplace!

   📦 Skill: <skill-name>
   📂 Location: <skill-name>/.claude-plugin/plugin.json
   📋 Category: <category>

   Next step: Publish with /skill-manager publish
   ```

---

### Workflow 3: Update Skill Metadata

**Purpose**: Update existing skill's version, description, keywords, etc.

**Steps**:

1. **Select skill to update** (via AskUserQuestion):
   - List all skills from marketplace.json
   - User selects one

2. **Show current metadata**:
   - Display current plugin.json content
   - Display current marketplace.json entry

3. **Ask what to update** (via AskUserQuestion):
   - [ ] Version (current: X.X.X)
   - [ ] Description
   - [ ] Keywords
   - [ ] Category
   - [ ] Display name

4. **Gather new values** for selected fields

5. **Update plugin.json** in skill folder

6. **Update marketplace.json** entry

7. **Report completion** with diff showing changes

---

### Workflow 4: Update Marketplace Metadata

**Purpose**: Update marketplace-level information (name, owner, description).

**Steps**:

1. **Show current marketplace metadata**:
   - Read `.claude-plugin/marketplace.json`
   - Display: name, displayName, owner, description, version

2. **Ask what to update** (via AskUserQuestion):
   - [ ] Display name
   - [ ] Owner name
   - [ ] Owner URL
   - [ ] Description
   - [ ] Homepage URL

3. **Gather new values** for selected fields

4. **Update marketplace.json**

5. **Report completion** with diff

---

### Workflow 5: Publish to Git (Version Management + Deployment)

**Purpose**: Automate Git workflow with semantic versioning, conventional commits, and release notes.

**Integration**: Works harmoniously with Git best practices and can integrate with `/sc:git` command.

**Steps**:

1. **Check Git status**:
   ```bash
   git status --porcelain
   ```
   - If no changes: "Nothing to publish"
   - If changes exist: Continue

2. **Determine version bump type** (via AskUserQuestion):
   - **patch** (1.0.0 → 1.0.1): Bug fixes, minor updates
   - **minor** (1.0.0 → 1.1.0): New features, backward-compatible
   - **major** (1.0.0 → 2.0.0): Breaking changes
   - **custom**: User specifies exact version

3. **Calculate new version**:
   - Read current version from marketplace.json
   - Apply semantic versioning rules
   - Update marketplace.json version
   - Update all plugin.json versions (optional - ask user)

4. **Generate changelog entry**:
   - Analyze Git diff to identify changes
   - Categorize changes:
     - `feat:` → New features
     - `fix:` → Bug fixes
     - `docs:` → Documentation
     - `refactor:` → Refactoring
     - `chore:` → Maintenance
   - Create CHANGELOG.md entry (or append if exists):
     ```markdown
     ## [X.X.X] - YYYY-MM-DD

     ### Added
     - New skill: skill-name

     ### Changed
     - Updated skill-name: description

     ### Fixed
     - Fixed bug in skill-name
     ```

5. **Generate commit message** (Conventional Commits):
   ```
   <type>(<scope>): <subject>

   <body>

   🤖 Generated with Claude Code

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

   Example types:
   - `feat`: New skill or feature
   - `fix`: Bug fix
   - `docs`: Documentation update
   - `chore`: Maintenance tasks
   - `refactor`: Code refactoring
   - `release`: Version release

6. **Git operations**:
   ```bash
   # Add all changes
   git add .

   # Commit with generated message
   git commit -m "<commit-message>"

   # Create Git tag for version
   git tag -a v<version> -m "Release v<version>"

   # Push to remote
   git push origin master
   git push origin v<version>
   ```

7. **Report completion**:
   ```
   ✅ Published successfully!

   📦 Version: <old-version> → <new-version>
   🏷️  Tag: v<new-version>
   📝 Changelog: Updated
   🔗 Repository: <url>

   Commit: <commit-hash>
   Message: <commit-message>
   ```

---

### Workflow 6: Validate Marketplace

**Purpose**: Comprehensive validation of marketplace and all skills.

**Steps**:

1. **Validate marketplace.json**:
   - ✅ File exists
   - ✅ Valid JSON format
   - ✅ Required fields present (name, owner, plugins)
   - ✅ Version follows semver (X.X.X)
   - ✅ All plugin entries have required fields

2. **Validate each skill**:
   - ✅ Skill folder exists
   - ✅ SKILL.md exists
   - ✅ SKILL.md has valid YAML frontmatter
   - ✅ `.claude-plugin/plugin.json` exists
   - ✅ plugin.json has required fields
   - ✅ Version in plugin.json matches marketplace.json
   - ✅ Keywords are meaningful (not empty/generic)

3. **Validate Git repository**:
   - ✅ Git initialized
   - ✅ Remote origin configured
   - ✅ No uncommitted changes (warning if exists)

4. **Report validation results**:
   ```
   ✅ Marketplace Validation: PASSED

   Marketplace: ✅ Valid
   Skills: ✅ 11/11 passed
   Git: ✅ Configured

   Or if errors:

   ❌ Marketplace Validation: FAILED

   Errors:
   - skill-name: Missing plugin.json
   - another-skill: Invalid version format

   Warnings:
   - 3 uncommitted changes
   ```

---

## Helper Functions

### Version Management

**Semantic Versioning Rules**:
- **MAJOR**: Breaking changes (X.0.0)
- **MINOR**: New features, backward-compatible (0.X.0)
- **PATCH**: Bug fixes, minor updates (0.0.X)

**Version Increment Logic**:
```python
def increment_version(current: str, bump_type: str) -> str:
    major, minor, patch = map(int, current.split('.'))

    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        return current  # custom version provided by user
```

### Conventional Commits

**Format**: `<type>(<scope>): <subject>`

**Types**:
- `feat`: New feature or skill
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing updates
- `chore`: Maintenance tasks
- `release`: Version release

**Examples**:
```
feat(nextjs15-init): Add dashboard domain support
fix(web-to-markdown): Fix Playwright fallback issue
docs(README): Update installation instructions
chore(marketplace): Bump version to 1.2.0
release: Version 1.2.0
```

### Changelog Generation

**Format**: Keep a Changelog (https://keepachangelog.com)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-01-10

### Added
- New skill: skill-manager for marketplace management
- Support for semantic versioning

### Changed
- Updated README with marketplace installation instructions

### Fixed
- Fixed validation errors in plugin.json files

## [1.1.0] - 2025-01-05
...
```

---

## Integration with Existing Commands

### Git Command Integration

This skill works harmoniously with `/sc:git` command:

**Scenario 1: Quick Publish**
```bash
# Use skill-manager for full automation
/skill-manager publish
```

**Scenario 2: Manual Git with skill-manager versioning**
```bash
# Update versions with skill-manager
/skill-manager update-marketplace

# Use /sc:git for custom commit
/sc:git commit -m "Custom message"
```

### Skill Creator Integration

**Workflow**: Create → Add → Publish
```bash
# 1. Create new skill
/skill-creator my-new-skill

# 2. Add to marketplace
/skill-manager add-skill

# 3. Publish
/skill-manager publish --type minor
```

---

## Error Handling

### Common Errors

**Error 1**: Marketplace already initialized
```
❌ Error: Marketplace already exists at .claude-plugin/marketplace.json

Use /skill-manager update-marketplace to modify it.
```

**Error 2**: Skill folder not found
```
❌ Error: Skill folder "skill-name" does not exist.

Create it first with /skill-creator or manually.
```

**Error 3**: Git not initialized
```
❌ Error: Git repository not initialized.

Run: git init
Then: git remote add origin <url>
```

**Error 4**: Uncommitted changes during publish
```
⚠️  Warning: You have uncommitted changes.

Proceed with publish? (Y/n)
```

**Error 5**: Invalid version format
```
❌ Error: Version must follow semver format (X.X.X)

Example: 1.0.0, 2.1.3, 0.5.2
```

---

## Best Practices

### 1. Version Management
- Use `patch` for bug fixes and minor updates
- Use `minor` for new skills or features
- Use `major` for breaking changes or major restructuring
- Always update CHANGELOG.md

### 2. Git Workflow
- Validate before publishing
- Write meaningful commit messages
- Create tags for releases
- Keep commits atomic (one logical change per commit)

### 3. Marketplace Organization
- Group skills by category
- Use descriptive keywords
- Keep descriptions concise (1-2 sentences)
- Maintain consistent naming conventions

### 4. Documentation
- Update README after adding skills
- Keep CHANGELOG.md current
- Include installation instructions
- Document breaking changes

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `init` | Initialize new marketplace |
| `add-skill` | Add skill to marketplace |
| `update-skill` | Update skill metadata |
| `update-marketplace` | Update marketplace metadata |
| `publish` | Git deployment with versioning |
| `validate` | Validate marketplace configuration |

---

## Examples

### Example 1: Setting up a new marketplace

```
User: Initialize marketplace
Skill: /skill-manager init

[Asks for marketplace info]
User: Name: awesome-skills
User: Owner: John Doe
User: URL: https://github.com/johndoe

Skill: ✅ Marketplace initialized!
```

### Example 2: Adding a new skill

```
User: Add new skill
Skill: /skill-manager add-skill

[Asks for skill info]
User: Name: api-generator
User: Category: Development Tools
User: Keywords: api, openapi, swagger

Skill: ✅ Skill added to marketplace!
```

### Example 3: Publishing with version bump

```
User: Publish changes
Skill: /skill-manager publish

[Asks for version type]
User: minor

Skill:
- Current version: 1.0.0
- New version: 1.1.0
- Changelog updated
- Git committed and pushed
- Tag created: v1.1.0

✅ Published successfully!
```

---

## Notes

- This skill uses Python scripts in `scripts/` directory
- Templates are in `templates/` directory
- Reference documentation in `references/` directory
- All operations are idempotent (safe to run multiple times)
- Git operations can be reviewed before execution
- Compatible with GitHub, GitLab, and other Git hosting services
