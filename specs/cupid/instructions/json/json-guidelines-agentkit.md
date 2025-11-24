# JSON Schema Guidelines for OpenAI AgentKit

## Overview

This document captures the requirements and best practices for creating JSON schemas that work with OpenAI's AgentKit Agent Builder. These guidelines were learned through building the CUPID game state tracker schema.

**Key Principle:** AgentKit's strict mode has very specific requirements that differ from standard JSON Schema specifications.

---

## Strict Mode Requirements

When using AgentKit's Agent Builder with structured output (strict mode), your schema must follow these rules:

### 1. Top-Level "name" Field (REQUIRED)

Your schema **must** include a top-level `"name"` field with restricted characters:

```json
{
  "name": "YourSchemaName",
  "description": "...",
  "type": "object",
  ...
}
```

**Valid characters for name:**
- Letters: `a-z`, `A-Z`
- Numbers: `0-9`
- Underscores: `_`
- Hyphens: `-`
- Maximum length: 64 characters

**Pattern:** `^[a-zA-Z0-9_-]{1,64}$`

❌ **INVALID:** `"My Schema!"`, `"schema.name"`, `"my:schema"`
✅ **VALID:** `"MySchema"`, `"my_schema"`, `"schema-name-123"`

### 2. No Standard JSON Schema Metadata Fields

Remove these standard JSON Schema fields—they contain invalid characters:

❌ **DO NOT USE:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",  // Contains : and /
  "$id": "my-schema-id",                                 // Contains $
  ...
}
```

✅ **USE INSTEAD:**
```json
{
  "name": "MySchema",
  "description": "Schema description",
  ...
}
```

### 3. All Top-Level Properties Must Be Required

In strict mode, if you have a `"required"` array, it **must** list ALL properties defined in `"properties"`:

❌ **INVALID:**
```json
{
  "type": "object",
  "required": ["field1", "field2"],
  "properties": {
    "field1": {...},
    "field2": {...},
    "field3": {...},  // ← field3 exists but not in required!
    "field4": {...}   // ← field4 exists but not in required!
  }
}
```

✅ **VALID:**
```json
{
  "type": "object",
  "required": ["field1", "field2", "field3", "field4"],
  "properties": {
    "field1": {...},
    "field2": {...},
    "field3": {...},
    "field4": {...}
  }
}
```

**Error Message:** "Schema required parameters list must include all properties when strict is true."

### 4. All Nested Objects Must Have "additionalProperties": false

Every object type (including nested objects and array items) **must** specify `"additionalProperties": false`:

❌ **INVALID:**
```json
{
  "stageHistory": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "stage": {...},
        "score": {...}
      }
      // ← Missing "additionalProperties": false
    }
  }
}
```

✅ **VALID:**
```json
{
  "stageHistory": {
    "type": "array",
    "items": {
      "type": "object",
      "required": ["stage", "score"],
      "properties": {
        "stage": {...},
        "score": {...}
      },
      "additionalProperties": false  // ← REQUIRED
    }
  }
}
```

**Error Message:** "'additionalProperties' is required to be supplied and to be false."

### 5. All Nested Objects Must Have "required" Arrays

Even nested objects need complete `"required"` arrays:

❌ **INVALID:**
```json
{
  "planetaryContext": {
    "type": "object",
    "properties": {
      "sun": {...},
      "moon": {...},
      "venus": {...},
      "mars": {...}
    }
    // ← Missing "required" array
  }
}
```

✅ **VALID:**
```json
{
  "planetaryContext": {
    "type": "object",
    "required": ["sun", "moon", "venus", "mars"],  // ← REQUIRED
    "properties": {
      "sun": {...},
      "moon": {...},
      "venus": {...},
      "mars": {...}
    },
    "additionalProperties": false
  }
}
```

---

## Naming Conventions

### Field Names

Use **camelCase** for all field names (not snake_case):

❌ **INVALID:**
```json
{
  "current_stage": "...",
  "base_compatibility": 69,
  "score_delta": 5
}
```

✅ **VALID:**
```json
{
  "currentStage": "...",
  "baseCompatibility": 69,
  "scoreDelta": 5
}
```

### Enum Values

Enum values can use letters, numbers, and no spaces. Prefer camelCase:

❌ **INVALID:**
```json
"enum": ["scene 1", "scene-two", "SCENE_THREE"]
```

✅ **VALID:**
```json
"enum": ["scene1", "scene2", "scene3"]
```

---

## Field Name Restrictions

All property names must contain only:
- Letters (a-z, A-Z)
- Numbers (0-9)
- Underscores (_) - but prefer avoiding these in favor of camelCase
- Hyphens (-) - but prefer avoiding these in favor of camelCase

❌ **INVALID:** `"field.name"`, `"field:name"`, `"field name"`, `"field@name"`
✅ **VALID:** `"fieldName"`, `"field_name"`, `"field-name"`

**Best practice:** Use camelCase exclusively for consistency.

---

## Common Errors & Solutions

### Error 1: Schema Name Validation

**Error:** "Schema name must only contain letters, numbers, underscores, and hyphens."

**Cause:**
- The `"name"` field contains invalid characters (colons, slashes, dots, spaces)
- OR the `"$schema"` or `"$id"` fields are present

**Solution:**
1. Add valid `"name"` field at top level
2. Remove `"$schema"` and `"$id"` fields

### Error 2: Required Parameters Mismatch

**Error:** "Schema required parameters list must include all properties when strict is true."

**Cause:** The `"required"` array doesn't list all properties in `"properties"`

**Solution:** Add ALL property names to the `"required"` array

### Error 3: Missing additionalProperties

**Error:** "'additionalProperties' is required to be supplied and to be false."

**Cause:** A nested object (or array item object) is missing `"additionalProperties": false`

**Solution:** Add `"additionalProperties": false` to every object type definition

---

## Complete Working Example

See: `cupid-game-state-schema.json` (in this directory)

This schema follows all AgentKit requirements:
- ✅ Top-level `"name"` field
- ✅ No `$schema` or `$id`
- ✅ All properties in `"required"` array
- ✅ All nested objects have `"additionalProperties": false`
- ✅ All nested objects have `"required"` arrays
- ✅ camelCase naming throughout
- ✅ Valid characters only

---

## Validation Checklist

Before uploading your schema to Agent Builder, verify:

- [ ] Top-level `"name"` field present (alphanumeric, underscore, hyphen only)
- [ ] No `"$schema"` or `"$id"` fields
- [ ] `"required"` array includes ALL properties
- [ ] Every nested object has `"additionalProperties": false`
- [ ] Every nested object has a `"required"` array
- [ ] All field names use camelCase
- [ ] All field names contain only valid characters (letters, numbers, underscore, hyphen)
- [ ] All enum values contain only valid characters
- [ ] File is valid JSON (no syntax errors)

---

## AgentKit vs Standard JSON Schema

| Feature | Standard JSON Schema | AgentKit Strict Mode |
|---------|---------------------|---------------------|
| `$schema` field | Required/Recommended | ❌ Not allowed (invalid chars) |
| `$id` field | Optional | ❌ Not allowed (invalid chars) |
| `name` field | Not standard | ✅ Required |
| Optional properties | Supported | ❌ All must be in `required` |
| `additionalProperties` | Optional | ✅ Must be `false` for all objects |
| Partial `required` arrays | Allowed | ❌ Must list all properties |
| Field name chars | Any valid JSON | Only a-z, A-Z, 0-9, _, - |

---

## Resources

- [OpenAI Structured Outputs Docs](https://platform.openai.com/docs/guides/structured-outputs)
- [AgentKit Documentation](https://github.com/openai/openai-agents-python)
- [JSON Schema Validation Patterns](https://portkey.ai/error-library/pattern-mismatch-error-10474)

---

## Summary

**The Golden Rules:**
1. Add `"name"` at top level
2. Remove `"$schema"` and `"$id"`
3. Put ALL properties in `"required"`
4. Add `"additionalProperties": false` to ALL objects
5. Use camelCase everywhere
6. Stick to alphanumeric + underscore + hyphen

Follow these rules and your schema will validate in AgentKit's Agent Builder.

🎯
