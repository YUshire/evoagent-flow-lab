# Reproducible experiment record

Run `python -m unittest discover -s tests -v` and `python -m unittest discover -s fixtures/tests -v`.

Local full-suite evidence and the earlier four-arm synthetic benchmark are in records/local-validation/. The optional 130-case supplied corpus is absent; its test is explicitly skipped. The 100-case dataset is synthetic-controlled, not real historical GitHub data. Cost values of zero indicate unconfigured pricing, not free model usage.

New GitHub PRs intentionally introduce defects into isolated fixtures; their chronology, review comments, model patch and verified draft fix provide workflow evidence. They do not prove real-world accuracy.
