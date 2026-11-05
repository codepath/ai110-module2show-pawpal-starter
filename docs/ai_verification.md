# AI110 verification record

Observed November 5, 2026 UTC on Windows, Python 3.13.7. Commands ran from the repository root.

| Check | Actual result |
| --- | --- |
| `python -m compileall -q app.py pawpal_system.py persistence.py ai tests/test_ai_evaluation.py` | Exit 0, no syntax errors |
| `python -m ai.evaluate` | 23 passed in 5.27s, exit 0; mocked API, no live provider calls |
| `python -m pytest -p no:cacheprovider --basetemp=<FRESH_TEMP_DIR>` | 178 passed in 32.06s, exit 0. The personal temp-root path is redacted here. |
| `python -m streamlit run app.py --server.headless true --server.port 8503` | Server started and announced `http://localhost:8503`; stopped after startup check. Automated AppTest cases cover AI controls, but no manual browser review was performed. |
| Mermaid 11.12.0 `mermaid.parse()` on `diagrams/architecture.mmd` | Returned `{ diagramType: 'flowchart-v2', config: {} }` |
| `git diff --check` and `git diff --cached --check` | Exit 0; no whitespace errors. Git reported Windows LF/CRLF conversion warnings. |
| Secret pattern scan of changed code/docs | No Google-style API key found; no key value printed in this record. |

The first full pytest attempt used the pre-existing `.pytest_temp` as `--basetemp` and produced 21 fixture setup errors because Windows denied pytest permission to remove that directory; 154 tests passed in that attempt. Re-running with a fresh temp path passed all 175 then-collected tests. After two more UI cases and one citation case were added, the final full run above passed all 178. The temp-directory failure was environmental, not a test assertion failure.

The [live comparison](ai_live_comparison.json) was run separately with a real Gemini API key in the environment. The initial sandboxed call could not complete; the approved network run recorded one direct answer, one grounded answer, and one planning response. The comparison file contains no credentials. It is one example, not a general accuracy score.
