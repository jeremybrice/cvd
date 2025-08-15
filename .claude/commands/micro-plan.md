---
name: micro-plan
description: Generate detailed execution plans with micro-tasks (5 min each) that maintain zero context loss throughout implementation
---

# Micro-Plan Execution Command

You are creating a comprehensive execution plan that breaks down complex tasks into 5-minute micro-tasks with full context preservation.

## Command Variations

### Generate Implementation Plan
When asked to "create plan for [feature/task]":
1. Analyze requirements and existing codebase
2. Identify all dependencies and constraints
3. Break down into 5-minute executable chunks
4. Create detailed todo list with verification steps
5. Establish checkpoints for progress review

### Refactor Existing Code Plan
When asked to "plan refactoring of [component]":
1. Map current code structure and dependencies
2. Identify refactoring targets and patterns
3. Create incremental transformation steps
4. Define rollback strategies for each change
5. Specify testing at each milestone

### Debug Investigation Plan
When asked to "plan debugging for [issue]":
1. Document symptoms and error patterns
2. Create hypothesis-driven investigation steps
3. Design isolated test scenarios
4. Plan systematic elimination process
5. Include logging and monitoring additions

## Implementation Steps

1. **Context Analysis Phase**
```bash
# Gather project structure
find . -type f -name "*.py" -o -name "*.js" | head -20
# Check recent modifications
git log --oneline -10
# Identify related components
grep -r "PATTERN" --include="*.py" .
```

2. **Task Decomposition**
```markdown
## Todo List Structure
- [ ] Task 1: Search for existing implementations (5 min)
  - Context: Need baseline understanding
  - Action: grep -r "function_name" ./src
  - Verify: Found 3+ reference implementations
  
- [ ] Task 2: Read primary module (5 min)
  - Context: Understanding current structure
  - Action: Read src/module.py lines 1-100
  - Verify: Identified main classes and methods
```

3. **Checkpoint Creation**
- Every 3-5 tasks: Review progress
- Document findings in comment block
- Update remaining tasks based on discoveries
- Verify no context has been lost

4. **Risk Identification**
- List potential blockers
- Create fallback approaches
- Include diagnostic commands
- Plan for common failure modes

## Context Files to Load
- Project README for conventions
- Main application entry point
- Test files for validation approach
- Configuration files for environment

## Success Metrics
- All micro-tasks completable in 5 minutes
- Zero context loss between tasks
- Clear verification for each step
- Checkpoints prevent drift from objectives

## Task Template

```markdown
- [ ] [Verb] [Specific Action] (5 min)
  - Context: [Why needed, what depends on this]
  - Action: [Exact commands/code to write]
  - Verify: [How to confirm success]
  - Output: [What to record for next tasks]
```

## Execution Guidelines

### Maintaining Context
- Include file paths in every task
- Reference line numbers when applicable
- Note function/variable names explicitly
- Carry forward findings to dependent tasks

### Time Management
- 5 minutes maximum per task
- If task exceeds limit, split it
- Include buffer tasks for complexity
- Plan for 15-minute checkpoint reviews

### Documentation Trail
- Record actual vs estimated time
- Note unexpected discoveries
- Update plan based on findings
- Maintain running context document