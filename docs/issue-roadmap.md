## test(core): add end-to-end coverage for agent loops
Add integration tests that exercise the full agent loop against local fixtures.
Cover tool calls, answer parsing, failures, and multi-step crawl behavior.
The goal is to catch regressions in the actual crawl flow, not just isolated helpers.
Acceptance should include at least one happy-path crawl, one malformed-model-output case, and one tool-failure case.

## chore(observability): add structured logging across the loop
Add readable logging for model responses, tool calls, parse decisions, and loop state.
Make it easy to trace what the agent saw, did, and why it stopped.
Prefer concise but structured output so the crawl can be debugged from a terminal session or captured log.
The logging should make it obvious which tool ran, what input it received, and what result was returned.

## feat(tools): add a bash tool for shell command execution
Add a shell tool so the agent can inspect arbitrary repositories and run simple commands.
Keep the interface small and focused on code crawling workflows.
This is the main escape hatch for exploring unfamiliar repositories beyond file listing and file reading.
The tool should support safe, bounded command execution and return stdout, stderr, and exit status clearly.

## feat(tools): add a final report writing tool
Add a tool that writes a structured summary of the crawl at the end of a run.
The report should capture findings, file coverage, and open questions.
The intent is to produce a clean end-of-run artifact that can be shared or reviewed without replaying the full crawl.
The output should be structured enough to compare runs across models or codebases.

## feat(ui): build the first agent progress interface
Create the first UI layer for watching the crawl in real time.
Show current action, tool calls, progress, and findings in a readable way.
The UI should make the agent feel alive without becoming heavy or difficult to launch.
Start with a simple, stable surface that can show the current step, recent tool output, and final summary.

## feat(ui): evaluate tui and web ui implementation options
Compare a Python TUI, a TypeScript TUI, and a web UI for the agent interface.
Pick the lightest architecture that still gives a good live experience.
This issue is about choosing the front-end architecture before committing to a larger UI investment.
The result should document tradeoffs around launch speed, implementation complexity, and streaming support.

## feat(modeling): add rlm-based harness integration
Add an alternate harness path for RLM-driven runs.
Use it to compare baseline behavior against RLM behavior on the same crawling tasks.
This should stay isolated from the baseline harness so experiments do not destabilize the main path.
The point is to measure whether RLM changes tool use, search depth, or report quality.

## perf(tools): optimize existing file tools
Improve the current file exploration tools for speed and reliability.
Reduce overhead so the agent can crawl larger repos faster.
Focus on the file crawler primitives first because they are the highest-frequency operations.
This may include better path handling, less redundant IO, and cleaner return types.

## test(models): run full-loop evaluations across multiple models
Run the same crawl against multiple models and compare quality, latency, and tool use.
Use the results to guide model selection for the agent.
The point is to establish a repeatable benchmark for the agent across candidate models.
The evaluation should compare coverage, tool efficiency, and final report usefulness.

## refactor(tools): split tools into dedicated modules with docs
Move each tool into its own file under `tools/`.
Add clear documentation for purpose, inputs, outputs, and edge cases.
This is about making the tool layer explicit and easy to extend as the agent grows.
The goal is for each tool file to be understandable on its own without a lot of shared abstraction.

## feat(core): improve parsing and tool-call handling
Make tool-call parsing more robust across different model output shapes.
Handle missing args, malformed payloads, and mixed answer/tool responses cleanly.
This issue should harden the agent against the kinds of output drift that happen across models.
The parser should fail clearly when the response is unusable and recover gracefully when only small fields are missing.

## chore(repo): add repo-level workflow and command docs
Document the intended crawl flow, tool order, and how to run the agent locally.
Keep it short and practical so the repo is easy to pick up.
This should make it clear how to launch the agent, how to interpret the output, and where the main extension points live.
It is meant to reduce onboarding friction for anyone reading or extending the repo.
