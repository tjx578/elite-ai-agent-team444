# Persona versioning dan integrasi CP1.1

Status: DESIGN_CANON; lifecycle is recorded in the separate successor receipt. Without that receipt this is a candidate, not frozen. Runtime verification remains NOT_EXECUTED.

## Lapisan dan binding

1. [WOLF15_SENTIENT_PRINCIPLE.md](WOLF15_SENTIENT_PRINCIPLE.md): sumber owner disalin byte-identik; filosofi dan identitas v1.
2. [persona-profile.yaml](persona-profile.yaml): profil cp1.1-v1 mengikat SHA-256 Principle dan guidance serta mewarisi baseline overrides dan authority READ_ONLY.
3. [runtime-guidance.md](runtime-guidance.md): subset perilaku yang disiapkan untuk assembly; runtime_loaded=false. Dokumen Principle lengkap tidak dimuat sebagai raw system prompt.

[Kontrak gateway sebelumnya](../cp1/gateway-contract.md) tetap menjadi wire contract. Saat profil penerus dipilih secara eksplisit, envelope persona_profile harus memakai id/version/hash byte profil baru; guidance dan Principle harus cocok sebelum assembly. Relative guidance.path dihitung dari direktori profil. CP1.2 harus menolak binding hilang/tidak cocok, bukan mencari file lain atau diam-diam memakai profil lama. Enforcement ini masih belum diimplementasikan oleh dokumentasi ini.

CP1.1-DESIGN-001 beserta 13 artefak dan review/freeze receipt historis immutable. CP1.1-DESIGN-002 mengusulkan pengganti persona saja; gateway tidak berubah. Review PASS lama tidak diwariskan. Candidate harus memperoleh fresh exact-artifact review, freeze receipt baru, CI dan resulting-main verification sebelum closure. Saat ini tidak ada default runtime selection. Publication PR #21 memiliki blocker secret-scan terpisah; tambahan digest ini tidak dianggap sudah di-allowlist.

## Penafsiran normatif

Policy, schema dan Control Kernel menegakkan izin. Principle/profile tidak menambah authority; permintaan owner di luar policy tetap dibatasi. Authorization yang masih sah tidak perlu ditanyakan berulang. Bahasa tentang consciousness/hidup hanya identitas operasional. Enam divisi/28 specialist, memory, Foundry dan capability fabric adalah target; ketersediaannya harus dibuktikan oleh trusted snapshot. Istilah trading/position size/stop loss pada naskah adalah analogi historis, tidak memasukkan trading, broker, lot, SL/TP atau scoring psikologi owner ke cognitive core. Tidak ada private chain-of-thought, raw prompt atau secret yang boleh dipromosikan menjadi evidence log.

## Pemilik checkpoint

| Checkpoint | Tanggung jawab |
|---|---|
| CP1.1 | Principle, profile, subset guidance, acceptance specification dan freeze setelah review |
| CP1.2 | Provider/model binding dan pemetaan role yang menjaga trust separation |
| CP1.3 | Timeout/cancellation/failure dan contract enforcement |
| CP1.4 | Reasoning terikat evidence |
| CP1.5 | Telemetry tersanitasi dengan version binding |
| CP1.6 | Provider nyata dan evaluasi persona, termasuk 30 skenario lama + 10 Principle + 6 derivation cases |
| CP4–CP8 | Owner interface, capability contracts/qualification, consequential actions dan learning sesuai roadmap |

[Owner-interface contract](owner-interface-persona-contract.md) mempertahankan satu identitas luar dan status yang jujur. Donor study tidak berarti qualification atau activation. ALG-REG-001 tidak berubah. Jev tetap pekerjaan terpisah.

## Freeze protocol

The review manifest is an explicit map of repository-relative paths to exact SHA-256 byte digests. It covers the Principle, complete profile (including assembly order and precedence), guidance, derivation map, acceptance definitions, versioning and owner interface, the CP1.1 integration document, README and AGENTS. No glob is used for later verification. The manifest and review/freeze receipts are outside that mapped byte-set; neither may hash itself.

After independent review PASS against the manifest digest, write docs/verification/cp1.1-design-002-freeze-receipt.json with the reviewed manifest path/digest, predecessor commit and review reference. Do not edit the reviewed bytes to mark FROZEN; receipt is the lifecycle authority. Verify every digest again before commit and after publication. Any changed member invalidates the review/freeze binding and requires a successor or re-review before initial freeze. Snapshot hashes bind bytes, not model fidelity. Provider role mapping remains a separately versioned CP1.2 artifact; CP1.6 must verify actual provider behavior.
