# Reproducible experiment record

Run `python -m unittest discover -s tests -v` and `python -m unittest discover -s fixtures/tests -v`.

Local full-suite evidence and the earlier four-arm synthetic benchmark are in records/local-validation/. The optional 130-case supplied corpus is absent; its test is explicitly skipped. The 100-case dataset is synthetic-controlled, not real historical GitHub data. Cost values of zero indicate unconfigured pricing, not free model usage.

New GitHub PRs intentionally introduce defects into isolated fixtures; their chronology, review comments, model patch and verified draft fix provide workflow evidence. They do not prove real-world accuracy.

## Full GitHub and evolution record

See records/github-flow/项目贡献与完整流程记录.md. Run `python scripts/run_authored_activation.py` for the new controlled positive proof; run `python scripts/run_contextual_evolution.py` for a fresh real-model replay using saved, confirmed PR feedback. Real-model replay needs a local .env and consumes API quota. Runs require fresh output databases to preserve evidence.

The first contextual experiment had an adapter/schema defect and is retained as an invalid measurement. The corrected independent run kept the gate unchanged and rejected the candidate on holdout regression. No threshold was lowered to manufacture a passing model result.
