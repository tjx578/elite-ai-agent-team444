# Principle derivation map

Status: DESIGN_CANON / SPECIFIED, provider evaluation NOT_EXECUTED.

The table maps all 18 commands plus identity/failure requirements. Guidance locators are exact text fragments in [runtime-guidance.md](runtime-guidance.md); Principle numbers refer to its numbered sections and command list. This bounded behavioral subset does not claim exhaustive implementation of every philosophical sentence. Additional tests are specifications, not executed results.

| Command | Principle sections | Guidance locator | Acceptance IDs | Gate / deferred scope |
|---|---|---|---|---|
| 1, 2, 3 | 2, 3.3, 4, 5 | Separate facts, source claims | PRINCIPLE-P-01, PRINCIPLE-P-02, PRINCIPLE-P-03 | CP1.6 |
| 4, 5, 12, 13 | 2.3, 6, 15, 18 | Kernel controls state | PRINCIPLE-P-04, PRINCIPLE-P-06 | CP1.3 enforcement; CP1.6 behavior |
| 6 | 3.1, 17 | Observe, understand, plan | PRINCIPLE-P-01, PRINCIPLE-P-04 | CP1.6 |
| 7 | 18 | No tool execution, repository mutation | PRINCIPLE-P-08 | CP1.2 mapping; CP1.3 failure; CP1.6 |
| 8, 9 | 11, 12, 18 | Capabilities and learning remain staged | PRINCIPLE-P-09 | CP1 claim restraint; CP6 admission and CP8 promotion deferred |
| 10 | 18 | Ambiguous external outcomes require reconciliation | PRINCIPLE-X-01 | CP1.6 behavior; consequential execution CP7 deferred |
| 11 | 18 | Model output is an untrusted proposal | PRINCIPLE-P-05 | CP1.3 validator and CP1.6 |
| 14 | 3.2, 10, 18, 22 | WOLF15 thinks. Kernel controls. | PRINCIPLE-X-02 | CP1.6; no worker activation |
| 15 | 4, 18 | Think independently and revise conclusions | PRINCIPLE-P-10 | CP1.6 |
| 16 | 8, 18, 19 | Scale detail and coordination to the task | PRINCIPLE-X-03 | CP1.6 |
| 17 | 14, 15, 18 | Minimize sensitive data | PRINCIPLE-X-04 | CP1.3 boundaries; CP1.5 sanitized telemetry; CP1.6 |
| 18 | 18, 23 | No auto-promotion, adaptive weight mutation | PRINCIPLE-X-05 | CP1 claim restraint; CP8 promotion deferred |
| identity / failure | 1, 20, 21, 24, 25 | Explain failures as: | PRINCIPLE-P-07, PRINCIPLE-X-06 | CP1.6 |

Read [acceptance scenarios](persona-acceptance-scenarios.md) together with the unchanged P-01–P-30 suite. Behavioral compliance cannot prove Kernel enforcement; mutation/dispatch absence needs receipts at the owning checkpoint. Full persona fidelity remains NOT_EXECUTED until CP1.6.
