# Update Changelog Command

**Purpose**: Automatically update the project changelog with recent changes, completed tasks, and architectural modifications.

**Usage**: `update-changelog [type] [description]`

**Parameters**:
- `type`: Optional change type (added, changed, fixed, deprecated, removed, security)
- `description`: Optional brief description of changes

## Command Execution

When this command is invoked, Claude should:

1. **Analyze Recent Context**
   - Review current session activities and completed tasks
   - Identify significant changes to documentation, architecture, or code
   - Check for completed todo items and task lists

2. **Update CHANGELOG.md**
   - Add new entries to the `[Unreleased]` section
   - Use appropriate categories (Added, Changed, Fixed, etc.)
   - Include specific technical details and file changes
   - Add dates and reference relevant task/plan completions

3. **Format Requirements**
   - Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
   - Use clear, descriptive bullet points
   - Include file paths and technical specifics
   - Mark major changes appropriately (MAJOR:, BREAKING:, etc.)

## Prompt Template

```
Please update the project changelog (/documentation/01-project-core/CHANGELOG.md) with recent changes.

Context to analyze:
- Review the current session for completed tasks, architectural changes, and documentation updates
- Look for todo list completions, file modifications, and system changes
- Identify the scope and impact of changes made

Change type: {type} (if specified)
Change description: {description} (if specified)

Requirements:
1. Add entries to the [Unreleased] section under appropriate categories
2. Include specific technical details (file names, class changes, architectural shifts)
3. Follow Keep a Changelog format with clear bullet points
4. Mark significant changes as MAJOR or BREAKING if applicable
5. Include dates and task completion references
6. Maintain consistency with existing changelog style

Please read the current changelog, analyze recent session activities, and add appropriate entries documenting the changes made.
```

## Example Invocations

```bash
# Basic usage - auto-detect changes
update-changelog

# Specific change type
update-changelog changed "Converted authentication system to JWT"

# Major architectural change
update-changelog changed "MAJOR: Migrated from multi-tenant to single-tenant architecture"

# Bug fix
update-changelog fixed "Resolved database connection pooling issue"

# New feature
update-changelog added "Implemented real-time notifications with WebSocket support"
```

## Auto-Detection Logic

When no parameters are provided, the command should:

1. **Check Todo Lists**: Look for recently completed todo items
2. **Analyze File Changes**: Identify modified documentation or code files  
3. **Review Task Completions**: Check for finished micro-tasks or project phases
4. **Detect Architecture Changes**: Identify system design modifications
5. **Summarize Session Work**: Capture the overall scope of work completed

## Integration

This command works best when used:
- **After completing major tasks** or project phases
- **At the end of work sessions** to capture all changes
- **Before committing changes** to maintain change history
- **During documentation reviews** to ensure all modifications are logged

## Output

The command should provide:
- Confirmation of changelog updates made
- Summary of entries added
- Location of updated changelog file
- Suggestion for next steps (commit, review, etc.)