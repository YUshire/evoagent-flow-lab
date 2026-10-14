# EvoAgent PR Review — #1

**Repository:** `YUshire/evoagent-flow-lab`  
**Risk:** `high`  
**Reviewer:** `agentic-reviewer`

Reviewed 2 file(s); found 3 actionable issue(s). Overall risk: high.

## Execution facts

- Mode: requested `agentic`, effective `agentic`
- Model calls: `7`; tool calls: `5`
- Tokens: input `21825`, output `3177`, total `25002`
- Token cost: `$0.00000000`; latency: `15592 ms`
- Context compression: `6` view(s), estimated reduction `0.0%`; recalled memories `0`

## LLM Agent collaboration

- Protocol: `lead-workers`
- Actual roles: `lead, security, correctness-reliability, critic`
- Candidate findings: `0`; critic decisions: `3`

## Findings

### 1. 🚨 Arbitrary code execution via eval() on untrusted request input in parse_request_value

`fixtures/request_handler.py:3` · **CRITICAL** · `SEC-EVAL`

parse_request_value passes its parameter `raw` directly to the built-in eval() with no validation, sanitization, or sandboxing. The function is documented as parsing an 'untrusted JSON request value', and the network-boundary risk signal plus the test suite (which feeds raw string payloads such as "42", "[1, 2]", '"hello"') confirm `raw` is externally controllable request data. Because eval() executes arbitrary Python expressions, an attacker who controls the request value can achieve arbitrary code execution in the server process (e.g. __import__('os').system(...)), leading to full host compromise. The correct primitive for parsing JSON is json.loads, which is safe. No mitigation exists in the surrounding code: the function body is a single eval call, there is no allowlist, no ast.literal_eval, and no input validation. Required evidence addressed: (1) eval call site confirmed at fixtures/request_handler.py:3; (2) `raw` is externally controllable per the docstring and network-boundary signal; (3) exploitability is direct and impact is RCE (CWE-95); (4) no validation or sandboxing present.

**Evidence**

```text
return eval(raw)
```

**Evidence references:** `symbol:aae41f42957e7d6e`

**Suggested fix:** Replace eval(raw) with a safe parser: `import json; return json.loads(raw)`. If only Python literals are intended, use `ast.literal_eval(raw)`. Never pass untrusted input to eval/exec.

**Suggested test:** Add a test asserting malicious payloads are not executed, e.g. `with self.assertRaises(Exception): parse_request_value("__import__('os').system('id')")`, and assert parse_request_value("42") == 42 via json.loads.

### 2. 🔴 Tests do not cover malicious expressions or boundary inputs for eval-based parser

`fixtures/tests/test_request_handler.py:4` · **HIGH** · `SEC-EVAL`

The test suite only covers benign inputs (integer, list, string). It never asserts that code-executing expressions are rejected, nor does it cover boundary/edge inputs (empty string, whitespace, malformed JSON, true/false/null, nested structures, oversized input). Because eval() is used, the absence of malicious-input tests means the injection vulnerability is entirely unguarded by the test suite, and the tests give false confidence that parsing is safe.

**Evidence**

```text
def test_integer(self): self.assertEqual(parse_request_value("42"), 42)
```

**Evidence references:** none

**Suggested fix:** Add negative tests for code-execution payloads (e.g. __import__, open, os.system) asserting they raise or are rejected, plus boundary tests for empty/malformed input and JSON literals true/false/null.

**Suggested test:** self.assertRaises(Exception, parse_request_value, "__import__('os').system('id')"); self.assertRaises(Exception, parse_request_value, ""); self.assertEqual(parse_request_value('true'), True)

### 3. 🟠 Unhandled exceptions and unexpected return types from eval-based parsing

`fixtures/request_handler.py:3` · **MEDIUM** · `SEC-EVAL`

eval(raw) raises SyntaxError/NameError/TypeError for malformed or non-literal input and can return arbitrary Python objects (functions, modules, class instances) rather than JSON-compatible types. Callers expecting a JSON value receive unexpected types or uncaught exceptions, creating reliability and type-safety failures. The tests do not exercise any error path, so this behavior is unverified.

**Evidence**

```text
return eval(raw)
```

**Evidence references:** none

**Suggested fix:** Use json.loads and wrap it to raise a well-defined ValueError/ParseError on invalid input, guaranteeing JSON-compatible return types.

**Suggested test:** self.assertRaises(ValueError, parse_request_value, "not json"); assert isinstance(parse_request_value('{"a": 1}'), dict)

