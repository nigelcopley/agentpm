#!/bin/bash
# Create Phase 1 Implementation Tasks for Work Item #147
# Enhanced Initialization System - Adaptive Questionnaire Engine

set -e  # Exit on error

echo "Creating Phase 1 Implementation Tasks for Work Item #147"
echo "=========================================================="
echo ""

# Task 1: Implement AdaptiveQuestionnaireEngine class
echo "Creating Task 1: Implement AdaptiveQuestionnaireEngine class..."
apm task create "Implement AdaptiveQuestionnaireEngine class" \
  --work-item-id 147 \
  --type implementation \
  --effort 4.0 \
  --description "Create adaptive question generation based on detection results. Engine analyzes DetectionResult and generates context-aware questions. Implement question filtering based on confidence scores and technology complexity."

echo "✓ Task 1 created"
echo ""

# Task 2: Implement smart defaults generation
echo "Creating Task 2: Implement smart defaults generation..."
apm task create "Implement smart defaults generation" \
  --work-item-id 147 \
  --type implementation \
  --effort 3.5 \
  --description "Generate intelligent defaults from detection results. Adapt defaults based on framework types (Django, React, Flask, etc.). Include complexity-based defaults for enterprise projects."

echo "✓ Task 2 created"
echo ""

# Task 3: Integrate adaptive questionnaire with init command
echo "Creating Task 3: Integrate adaptive questionnaire with init command..."
apm task create "Integrate adaptive questionnaire with init command" \
  --work-item-id 147 \
  --type implementation \
  --effort 3.0 \
  --description "Replace static questionnaire with adaptive engine in apm init command. Update CLI to use AdaptiveQuestionnaireEngine. Maintain backward compatibility with --skip-questionnaire flag."

echo "✓ Task 3 created"
echo ""

# Task 4: Test adaptive questionnaire engine
echo "Creating Task 4: Test adaptive questionnaire engine..."
apm task create "Test adaptive questionnaire engine" \
  --work-item-id 147 \
  --type testing \
  --effort 6.0 \
  --description "Comprehensive test suite for adaptive questionnaire. Coverage >90%, test all frameworks (Django, React, Flask, etc.), edge cases, smart defaults generation. Include integration tests with detection system."

echo "✓ Task 4 created"
echo ""

# Task 5: Document adaptive questionnaire system
echo "Creating Task 5: Document adaptive questionnaire system..."
apm task create "Document adaptive questionnaire system" \
  --work-item-id 147 \
  --type documentation \
  --effort 3.0 \
  --description "User and developer documentation for adaptive questionnaire. Include user guide for questionnaire workflow, developer guide for extending with new frameworks, examples for common scenarios."

echo "✓ Task 5 created"
echo ""

echo "=========================================================="
echo "✅ All 5 Phase 1 tasks created successfully!"
echo ""
echo "Next steps:"
echo "  1. Review tasks: apm task list --work-item-id 147"
echo "  2. Assign tasks to agents"
echo "  3. Begin implementation: apm task next <task_id>"
echo ""
