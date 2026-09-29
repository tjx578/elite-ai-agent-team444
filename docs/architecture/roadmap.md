# WOLF15 Sentient — Roadmap CP0–CP9

Status: **DERIVED_FROM_ROOT_README / SSOT-2026-09-30.1**. Rincian ini mengikuti [README root](../../README.md#10-roadmap-master-cp0cp9), SSoT sistem pada `main`. Perbarui bagian roadmap README terlebih dahulu, lalu sinkronkan dokumen ini; keduanya tidak boleh menetapkan urutan berbeda.

Baseline pemeriksaan: `07c942cd62ec5e85a521ee47976559a55f35d8b8`, 30 September 2026 WITA. CP0 CLOSED pada `bad73335f518d89356b88cba1cc26730808cd224`; CP1 ACTIVE_NEXT / NOT_IMPLEMENTED. Semua 73 substep dipertahankan, dengan routing donor v1.2 dan syarat qualification yang eksplisit.

<!-- BEGIN DERIVED ROOT ROADMAP -->

**Urutan implementasi tunggal: CP0 → CP1 → CP2 → CP3 → CP4 → CP5 → CP6 → CP7 → CP8 → CP9.** Substep `CPx.y` berada di dalam checkpoint induknya; bukan roadmap tambahan. Riset checkpoint berikutnya boleh berlangsung lebih awal dengan label `FUTURE_CHECKPOINT / DEFER / NO_RUNTIME_ACTIVATION`.

| CP | Nama dan hasil utama | Status pada baseline |
| --- | --- | --- |
| CP0 | Cognitive Foundation | **CLOSED / PASS** pada SHA penerimaan historis |
| CP1 | Real Sentient Reasoning | **ACTIVE_NEXT / NOT_IMPLEMENTED** |
| CP2 | Repository Intelligence | LOCKED |
| CP3 | Production Grade v1 — authenticated durable read-only service | LOCKED |
| CP4 | Personal JARVIS & Read-Only Intelligence | LOCKED |
| CP5 | Capability OS | LOCKED |
| CP6 | Capability Foundry | LOCKED |
| CP7 | Controlled Technology Builder | LOCKED |
| CP8 | Adaptive Intelligence | LOCKED |
| CP9 | Technology Company OS | LOCKED |

### Pemetaan donor master v1.2 ke checkpoint

Register `WOLF15_SENTIENT_MASTER_REPOSITORY_DONOR_REGISTER_v1.2_WEBMCP` dan matriks CSV S06 yang diunggah pemilik pada 30 September 2026 WITA menjadi sumber pembaruan pemetaan donor. [Register canonical](../research/donor-adaptation-register-20260929.md) menyimpan seluruh portfolio, source revisions dan rekonsiliasi; [matriks WebMCP](../research/webmcp-donors/donor-cp-matrix.csv) mempertahankan 11 baris sumber. README ini tetap master **sistem dan urutan checkpoint**; register adalah master **identitas serta pemetaan donor**, tanpa urutan roadmap kedua.

**Makna pemetaan:** CP fungsional menunjukkan komponen penerima suatu prinsip/capability. `qualification_cp=CP6` menunjukkan jalur akuisisi package/code/skill/runtime donor. Angka CP fungsional yang lebih awal tidak memberi izin mengimpor donor sebelum qualification selesai.

| CP | Donor dan kontribusi yang direncanakan | Batas pelaksanaan |
| --- | --- | --- |
| CP0 | Frozen `ALG-REG-001`, fondasi cognitive/contracts/governance | CLOSED pada SHA historis; register repository baru tidak mengubah bytes freeze |
| CP1 | Pydantic AI sebagai donor kontrak provider utama; OpenJarvis/Ruflo untuk provider, timeout dan budget; Transformers untuk kandidat local provider; LiteLLM/DeepAgents sebagai watch candidates | Satu real provider lebih dahulu; WebMCP runtime NONE; paket donor/Transformers tidak otomatis menjadi provider pertama |
| CP2 | Ruflo untuk retrieval/graph patterns, Pydantic AI untuk RepoContext/dedup/context spill, Context7 untuk dokumentasi sesuai versi | Analisis source read-only; WebMCP source boleh dibaca sebagai data, WebMCP runtime NONE |
| CP3 | OpenJarvis, Paperclip, Ruflo untuk task/run/lease/telemetry; Transformers untuk serving lifecycle; Signett untuk idempotency/recovery/receipt semantics | Layanan tetap read-only; pelajari/rebangun pola, jangan mengadopsi runtime donor yang belum qualified |
| CP4 | OpenJarvis/Paperclip/Ruflo; Transformers untuk multimodal/ASR; Context7; D3/Next.js; Deltalytix dan Openlib sebagai referensi UX/library; WebMCP spec, Chrome tools dan React lifecycle | Connector/browser read-only, profil tetap; native slice diuji dalam scope. SDK/skill/runtime S06 menunggu CP6; Openlib upstream belum terikat |
| CP5 | OpenJarvis/Paperclip/Ruflo/Pydantic AI/Transformers, MCP spec; WebMCP spec/types/Chrome tools/React hook, MCP-B/npm packages dan OpenTiny | Registry/resolver/ephemeral descriptors dan skill binding; donor-specific provider, bridge, polyfill atau fallback hanya sesudah qualification. Web authoring skill dari `webmaxru` menunggu CP6 |
| CP6 | OpenJarvis, Paperclip, Ruflo, Pydantic AI, Transformers, seluruh 11 donor S06 dan calon donor berikutnya | Exact source, rights, dependency/security, extraction, overlap, sandbox offline, independent evaluation dan admission terpisah; tidak self-activate |
| CP7 | OpenJarvis/Paperclip/Ruflo; Signett, WebMCPify, WebMCP Kit dan OpenTiny untuk tindakan browser/retrofit/session yang disetujui | Prepare/review/approve/execute/receipt/postcondition; scope session nyata, WXT dan consequential effects memerlukan grant yang sesuai |
| CP8 | OpenJarvis/Paperclip/Ruflo; Pydantic Evals sebagai pola evaluasi; Transformers untuk offline training/fine-tuning candidates; Chrome tools dan WindTunnel untuk evaluasi WebMCP | Verified episodes, fixed workload/baseline, held-out/regression, qualified evaluator dan promotion terpisah; benchmark luar tetap NOT_MEASURED untuk Sentient |
| CP9 | Integrasi hasil CP1–CP8; Paperclip dapat memberi pola tampilan kerja organisasi | Tidak menjadi jalur admission donor baru; end-to-end evidence tetap wajib |

#### Urutan implementasi dan qualification donor

1. **CP1–CP5 membangun fondasi milik Sentient.** Sumber donor dapat memberi pengetahuan, requirement, kontrak dan prinsip yang direbangun sebagai implementasi native; provenance, rights dan acceptance tetap diperiksa. Ini tidak mengaktifkan package/code/skill/runtime dari portfolio donor.
2. **CP6 mengkualifikasi adopsi donor.** Package/library donor, SDK, polyfill, bridge, skill, runtime, serta model artifact yang akan digunakan melewati qualification yang sesuai. Integrasi donor tertentu ke komponen CP1–CP5 dilakukan sebagai perluasan setelah gate CP6, tanpa mengubah urutan atau membuka ulang penerimaan historis CP tersebut.
3. **Kebutuhan awal yang hanya dapat dipenuhi melalui impor donor menghasilkan HOLD pada jalur itu.** Sebelum implementation, diperlukan keputusan/amandemen qualification yang eksplisit; tidak boleh menganggap tabel routing sebagai pengecualian. Pemilihan provider CP1 tetap keputusan tersendiri dan tidak dipaksakan menjadi Pydantic AI atau Transformers oleh register.
4. **Profil CP4 tetap terbatas.** Adapter browser native/read-only milik Sentient dapat diuji pada slice tetap di bawah Kernel. Penggunaan kode/SDK/skill S06 berbeda dari mempelajari spec; pola CP4 tidak mengizinkan pemasangan package donor lebih awal. WebMCP authoring/retrofit yang benar-benar mengubah aplikasi juga tetap masuk CP7.
5. **Offline qualification adalah satu-satunya jalur yang didukung kebijakan sekarang.** Connected/shadow membutuhkan desain, containment, evidence profile dan otorisasi terpisah. Penulisan `shadow required` pada sumber v1.2 dinormalisasi menjadi target bersyarat, tidak dianggap jalur aktif.

Pemisahan ini menjaga urutan CP0–CP9 dan syarat qualification CP6 sekaligus. **Functional ownership bukan admission date.** Data CSV tidak diubah untuk menyamarkan dependensi tersebut.

#### Hugging Face / Transformers dan model artifacts

Donor `tjx578/transformers-sentient@6b07e4510e3f9667f5256656118515bcde306fc4` dipetakan ke CP1/CP3/CP4/CP5/CP6/CP8, dengan upstream yang dilaporkan `huggingface/transformers`. Keberadaan commit telah diperiksa; build, runtime dan rights untuk penggunaan Sentient belum dikualifikasi.

| CP pemilik | Kontrak tambahan pada substep yang sudah ada |
| --- | --- |
| CP1 | Kandidat `LOCAL_TRANSFORMERS_PROVIDER` di `models/providers/`, di belakang `sentient/model_gateway/`; tetap satu-provider-first dan menunggu qualification untuk adopsi donor |
| CP3 | Serving health, load/unload, device/dtype, cache/quantization dan resource telemetry; tidak ada automatic download/load |
| CP4 | ASR, audio, vision dan multimodal sebagai input/output task yang sama dengan voice/text; capability yang tidak tersedia menjadi gap |
| CP5 | Descriptor dan version pinning untuk keluarga `hf.*`, model artifact, tokenizer/processor/config, provider dan environment |
| CP6 | Studi ekstraksi pipeline/interface sebagai donor utama; framework dan setiap model artifact diperiksa terpisah sebelum admission |
| CP8 | Training/fine-tuning offline hanya menghasilkan kandidat; dataset rights, holdout, retention/regression dan metering memerlukan evidence serta izin tersendiri |

Keluarga kandidat meliputi `hf.model-loader`, `hf.text-generation`, `hf.chat`, `hf.embeddings`, `hf.text-classification`, `hf.asr`, `hf.text-to-audio`, `hf.image-classification`, `hf.object-detection`, `hf.image-segmentation`, `hf.multimodal`, `hf.video`, `hf.quantization`, `hf.model-serving`, `hf.training` dan `hf.finetuning`. Ini selector rancangan, bukan API/provider yang telah tersedia. Alias singular `hf.embedding`/umum `hf.image` dari sumber harus dinormalisasi secara eksplisit sebelum menjadi canonical IDs; jangan membuat capability duplikat.

Framework Transformers, model weights, dan Control Kernel adalah tiga objek berbeda. Klaim lisensi framework `Apache-2.0` pada unggahan tidak memberi rights untuk semua model/dataset. Model ID/revision, weight/tokenizer/config digests, dependency/environment, license/permission, resource envelope dan evaluation receipt harus terikat sendiri. `trust_remote_code=false` adalah default rancangan; pengecualian membutuhkan keputusan terpisah. Donor ini tidak mengganti Pydantic AI atau pemilik Kernel.

#### Matriks WebMCP S06

Kolom primary/secondary menunjukkan pemilik fungsi. Seluruh donor tetap `NOT_ADMITTED`; angka CP3–CP5 tidak melewati prerequisite CP6 untuk adopsi package. CP1/CP2 tidak memiliki pekerjaan runtime WebMCP.

| Repository | Fungsi utama | CP utama | CP sekunder | Qualification |
| --- | --- | --- | --- | --- |
| `webmachinelearning/webmcp` | Canonical specification knowledge | CP5 | CP4 | CP6 |
| `webmachinelearning/webmcp-types` | Typed contracts | CP5 | — | CP6 |
| `GoogleChromeLabs/webmcp-tools` | Implementation demos and evaluation | CP5 | CP4, CP8 | CP6 |
| `GoogleChromeLabs/use-webmcp-tool` | React lifecycle in Owner Console | CP4 | CP5 | CP6 |
| `webmaxru/web-ai-agent-skills` | Authoring skill | CP6 | CP5 | CP6 |
| `TueJon/webmcpify` | App retrofit verification and audit | CP6 | CP7 | CP6 |
| `nekuda-ai/webmcp-kit` | Secondary implementation verification and migration skill | CP6 | CP7 | CP6 |
| `signettai/signett` | Secure action idempotency recovery and receipts | CP7 | CP3 | CP6 |
| `WebMCP-org/npm-packages` | Runtime polyfill compatibility and bridge reference | CP5 | — | CP6 |
| `opentiny/webmcp-sdk` | Browser fallback and CDP WXT skills | CP5 | CP7 | CP6 |
| `nekuda-ai/WindTunnel` | Comparative provider evaluation methodology | CP8 | — | CP6 |

Revision/provenance lengkap terdapat di [portfolio](../research/webmcp-donors/portfolio.yaml), [register](../research/donor-adaptation-register-20260929.md), dan [pemeriksaan sumber](../verification/repository-donor-roadmap-20260930.md). Semua 11 SHA S06 serta SHA Transformers telah ditemukan sebagai commit pada repo yang disebut. Keberadaan commit tidak membuktikan build, license compatibility, keamanan, benchmark atau runtime admission.

### Langkah implementasi berikutnya

**CP1.1 tetap langkah berikutnya.** Bekukan kontrak gateway, provider/model/profile, persona serta acceptance scenarios pada exact main terbaru. Gunakan register untuk membandingkan pilihan; tentukan satu real-provider slice dan buktikan cancellation, timeout, structured output, evidence binding serta batas biaya. Tidak ada donor/provider yang dipilih atau diaktifkan oleh perubahan dokumentasi ini. Setelah CP1.1 diterima, lanjutkan CP1.2–CP1.6 sesuai gate yang sama.

### Gate bersama dan completion receipt

Sebelum implementasi CP berikutnya: CP sebelumnya sudah CLOSED dengan receipt exact resulting-main; base SHA, kontrak, pemilik tanggung jawab, scope, prasyarat, serta acceptance task ditetapkan. Satu PR adalah increment yang dapat direview; merge satu PR tidak otomatis menutup satu CP.

`HOLD` berlaku bila revision tidak dapat diikat, ownership/authority ambigu, kontrak tidak kompatibel, rights/security donor belum selesai, bukti wajib hilang, required check gagal, review kritis belum selesai, scope melompat CP, atau operasi berikutnya melampaui izin. Riset/dokumentasi yang tidak mengaktifkan runtime tetap dapat berjalan sesuai scope.

Receipt penutupan minimal memuat: CP/substep, objective/scope/exclusions, base SHA, branch/head SHA, PR dan resulting-main SHA, artifact/config/schema versions, command dan hasil test, URL serta identity/check conclusion CI, temuan review dan resolusinya, acceptance evidence, keterbatasan, status akhir, keputusan penerimaan, dan next action. Receipt tidak memakai PASS dari SHA lain. Hash receipt tidak dimasukkan ke bytes dirinya sendiri.

**Status pelaksanaan:** `NOT_STARTED`, `IN_PROGRESS`, `HOLD`, `PASS_LOCAL`, `PASS_REMOTE`, `CLOSED`. `ACTIVE_NEXT` berarti prioritas berikutnya; tidak berarti implementasi sudah berjalan. CP0 tidak dibuka ulang oleh addendum dokumentasi. CP1 kelak memakai resulting-main terbaru sebagai base sambil mempertahankan SHA penerimaan CP0.

### CP0 — Cognitive Foundation

Fondasi identitas, typed contracts, kernel deterministik, evidence offline, reasoning seam, governance skill, cognitive observability, trust gates, dan ownership diterima pada `bad73335f518d89356b88cba1cc26730808cd224`.

| Substep historis | Isi |
| --- | --- |
| CP0.1 | SK-01 governance closure |
| CP0.2 | M3-A reasoning contracts |
| CP0.3 | SCRS v0 advisory observability |
| CP0.4 | Canonical architecture alignment |
| CP0.5 | Exact-main acceptance |

Addendum algoritme `ALG-REG-001` sesudah closeout adalah freeze riset/dokumentasi, bukan aktivasi provider, skill, memory, execution, atau REE.

### CP1 — Real Sentient Reasoning

Satu real provider melalui gateway milik WOLF15 menghasilkan proposal bertipe dan mempertahankan Kernel/evidence boundary. Persona dipasang sebagai profil berversi yang dapat dievaluasi, tanpa menambah tool authority.

| Substep | Isi |
| --- | --- |
| CP1.1 | Freeze gateway ownership, request/response schema, persona/prompt profile dan acceptance scenarios |
| CP1.2 | Satu concrete model/provider adapter; model, provider, technical profile dan model artifact dipisahkan; calon LOCAL_TRANSFORMERS_PROVIDER mengikuti prerequisite qualification donor |
| CP1.3 | Cancellation, deadline/timeout, budget, sanitized failure taxonomy |
| CP1.4 | Integrasi reasoning/evidence dan typed proposal; source instructions tetap data |
| CP1.5 | Telemetry model/provider/usage; optional complexity budgeter berdasarkan pengukuran |
| CP1.6 | Exact-main acceptance dengan receipt real provider dan evaluasi persona |

**Acceptance:** valid output diterima; malformed/schema/binding failures ditolak; cancellation menghentikan request; auth/rate-limit/policy/timeout dibedakan; token/context/output/request limits terukur sesuai kontrak; cost yang tidak diketahui tetap `NOT_MEASURED`. Tidak ada silent provider fallback atau hak tool/repo/memory dari output model. Pydantic AI direct/provider/profile adalah pola donor selektif, bukan pengganti orchestrator.

### CP2 — Repository Intelligence

Membaca repo dan sumber teknis yang diizinkan pada exact revision untuk menghasilkan audit/analisis bersumber, tanpa hak tulis.

| Substep | Isi |
| --- | --- |
| CP2.1 | Snapshot contract, repository identity, revision/digest dan SourceRef |
| CP2.2 | Read adapter dengan batas akses yang ditegakkan |
| CP2.3 | Bounded source/context assembler, semantic chunking, output spill/handles |
| CP2.4 | Tree/source map, AST/import/dependency graph yang relevan, analisis arsitektur dan capability candidates |
| CP2.5 | Provenance, freshness, conflict, unsupported claims, no-write dan replay tests |
| CP2.6 | Exact-main acceptance |

**Acceptance:** setiap temuan material menunjuk file/bytes/revision; source terlalu besar tidak diam-diam memenuhi konteks; stale/missing/conflicting evidence terlihat; README/AGENTS/donor comments tidak mengubah policy. Branch name saja tidak menjadi identitas runtime. Tidak ada worktree, shell executor, atau mutasi repo pada CP ini.

### CP3 — Production Grade v1

Membentuk layanan kognitif **read-only** yang authenticated, durable, observable, dan recoverable sebelum kemampuan pribadi atau mutasi ditambahkan.

| Substep | Isi |
| --- | --- |
| CP3.1 | Auth dan owner/caller identity |
| CP3.2 | Durable task/run/events, idempotency, transaction/outbox, lease/fencing bila diperlukan |
| CP3.3 | Structured log, trace, metrics, sanitized audit/receipt |
| CP3.4 | Secret isolation, resource/data limits, dependency-aware readiness; kontrak serving/model lifecycle/device/dtype/quantization bila provider terpilih memerlukannya |
| CP3.5 | Restart/cancellation/recovery, fault injection, rollback |
| CP3.6 | Staging/live read-only acceptance sesuai otorisasi operasi |
| CP3.7 | Resulting-main acceptance |

**Acceptance:** duplicate submission menghasilkan run canonical atau replay eksplisit; restart tidak mengubah task truth; auth denial tanpa efek; readiness turun saat required dependency gagal; telemetry tidak membocorkan credential/payload pribadi; rollback mengembalikan artifact tepat tanpa menghidupkan kembali izin yang direvoke. CI saja tidak menutup gate operasi.

### CP4 — Personal JARVIS & Read-Only Intelligence

Antarmuka pemilik, voice, sumber personal/media, dan Second Brain read path menjadi alur nyata yang tetap memakai Kernel. Persistent knowledge writes yang diperlukan untuk ingestion adalah operasi penyimpanan internal sesuai policy; konektor eksternal tetap read-only.

| Substep | Isi |
| --- | --- |
| CP4.1 | Owner/personal/media contracts dan privacy scope |
| CP4.2 | Read-only connectors, sync/checkpoint, metadata/caption retrieval; WebMCP discovery dan profil read-only tetap |
| CP4.3 | Knowledge/memory persistence di atas durability CP3, provenance, retensi dan quarantine |
| CP4.4 | Hybrid retrieval, evidence grounding, media segmentation/extraction; gap/discovery handoff hanya deferred |
| CP4.5 | Briefing dan personal routines dengan scheduler/receipt yang sesuai scope |
| CP4.6 | Owner interface, voice/STT/TTS, interruption, browser state dan kontrak input vision/multimodal yang tersedia; kandidat Transformers tetap gated |
| CP4.7 | Privacy, partial failure, media test matrix, stale descriptor/session invalidation |
| CP4.8 | Exact-main acceptance |

**Acceptance:** satu sumber personal nyata, satu media slice nyata, dan satu page tool read-only yang diizinkan terbukti; voice/text melewati path izin yang sama; transcript/connector hilang menghasilkan partial/unknown yang jujur. Admission tetap pada Kernel dengan pendekatan CP4–CP5 dalam bagian browser. Sending, calendar/account writes, purchase, booking, delete, dan repo mutation belum masuk CP4.

### CP5 — Capability OS

Satu plane capability untuk skills, tools, backend MCP, models/providers, dan ephemeral browser tools.

| Substep | Isi |
| --- | --- |
| CP5.1 | Contracts, canonical IDs, ToolDescriptor, CapabilityProvider, role–skill bindings dan gap semantics |
| CP5.2 | Versioned registry generation dan lifecycle capability/provider |
| CP5.3 | Task-scoped resolver, explicit no-provider result, pinned gap classification |
| CP5.4 | Tool/MCP/model/provider integration, model-artifact bindings dan ephemeral WebMCP descriptors; keluarga hf.* serta bridge/fallback donor menunggu qualification |
| CP5.5 | Unified Skills runtime, manifest/loader, pemetaan 28 peran ke package qualified, progressive disclosure dan bounded tool search |
| CP5.6 | Pinning, health, revocation, stale generation, denial, replay dan per-call policy tests |
| CP5.7 | Exact-main acceptance |

**Acceptance:** hanya provider qualified dapat dipilih; generation dipin; revoked/stale providers gagal tertutup; provider hints tidak mengalahkan policy; tool filtering saat listing tidak menggantikan authorization saat call. Tidak ada automatic acquisition atau consequential actions.

### CP6 — Capability Foundry

Discovery donor dan akuisisi capability yang terkontrol menghasilkan kandidat yang dapat direview.

| Substep | Isi |
| --- | --- |
| CP6.1 | Donor manifest, provenance, media-origin discovery request dan exact revision; portfolio v1.2 mencakup Transformers serta seluruh 11 donor S06 |
| CP6.2 | Rights/license, dependency, security dan data-egress gates |
| CP6.3 | Architecture reconstruction serta ekstraksi knowledge/principle/workflow; pisahkan knowledge-only, reuse, update/new skill dan provider gap |
| CP6.4 | Contract-based overlap/dedup/conflict |
| CP6.5 | Isolated packaging, mount/network/resource limits dan sandbox |
| CP6.6 | Independent offline evaluation terhadap baseline; shadow qualification hanya setelah desain, containment dan evidence path tersendiri disetujui |
| CP6.7 | Versioned candidate manifest, parent/source lineage dan consumer roles; admission terpisah untuk registry generation baru |
| CP6.8 | Exact-main acceptance |

**Acceptance:** discovery lead diverifikasi independen; source dapat direproduksi; rights/security unknown menahan adopsi; kode donor tidak dieksekusi hanya karena dibaca; kandidat tidak self-activate. Tidak ada `fetch → import → ACTIVE` atau bulk skill overwrite.

### CP7 — Controlled Technology Builder

Efek yang tepat dilakukan dengan approval, target, artifact, dan postcondition yang dapat diperiksa.

| Substep | Isi |
| --- | --- |
| CP7.1 | Action proposal/preview, execution request, approval dan receipt contracts |
| CP7.2 | Isolated worktree dan bounded file adapters |
| CP7.3 | Bounded shell/test/Git adapters |
| CP7.4 | GitHub feature branch dan draft-PR adapter |
| CP7.5 | Personal actions dan consequential browser/WebMCP approval path |
| CP7.6 | Idempotency, operation journal, replay protection, reconciliation dan rollback |
| CP7.7 | End-to-end builder acceptance, unauthorized/stale/ambiguous action cases |
| CP7.8 | Exact-main acceptance |

**Acceptance:** tidak ada write tanpa grant yang tepat; input/artifact/browser descriptor binding valid pada saat call; ambiguous outcomes direkonsiliasi; receipt dibedakan dari verifikasi hasil. Tidak ada direct mutation protected/default branch, autonomous merge/deploy, unrestricted shell, atau tindakan pribadi tanpa review/izin yang dipersyaratkan.

### CP8 — Adaptive Intelligence

Perbaikan berasal dari outcome yang terbukti dan dievaluasi independen, dengan pengendalian perubahan aktif.

| Substep | Isi |
| --- | --- |
| CP8.1 | Verified episode/outcome contracts dan journal |
| CP8.2 | Fixed versioned evaluator/rubric dan baseline |
| CP8.3 | SCRS calibration datasets serta ukuran drift/correlation/saturation yang bermakna |
| CP8.4 | Bounded candidate generators/REE; update skill/prompt/workflow dan calon offline training/fine-tuning dengan data/compute/rights terpisah, applicability dan kontraindikasi |
| CP8.5 | Replay, held-out dan temporal generalization; provider/skill/retrieval/browser regression |
| CP8.6 | Shadow evaluation setelah jalur qualification/containment tersendiri disetujui; bukan mode yang telah tersedia |
| CP8.7 | Independent review, owner/governance promotion dan version pinning |
| CP8.8 | Regression, disable/supersession dan rollback |
| CP8.9 | Exact-main acceptance |

**Acceptance:** candidate tidak mengubah evaluator, rubric, policy, atau run aktif; unknown tidak menjadi zero/PASS; LLM-as-judge tidak menjadi satu-satunya verdict; hard failure menahan promotion; popularity/media persuasion bukan evidence peningkatan.

Rencana historis **Sentient REE contracts and offline score v0** dipertahankan sebagai pekerjaan kandidat tanpa efek samping di CP8: typed metrics, perhitungan ΔR, kandidat α/β/γ, batas kandidat `abs(δ) ≤ 0.05`, missing-metric/normalization/cancellation guards, source/config version dan synthetic fixtures. Angka batas tersebut adalah parameter rancangan lama yang masih perlu divalidasi pada workload Sentient, bukan ukuran kecerdasan atau izin promotion. Slice offline ini tidak merangkai REE ke LangGraph, mengubah `alpha_beta_gamma.yml` aktif, menulis memory, mengaktifkan `reflective_heuristics.json`, atau mengintegrasikan trading. Penerimaan memerlukan outcome terverifikasi serta evaluator yang tidak dikendalikan bobot kandidat.

### CP9 — Technology Company OS

Integrasi produk dari kemampuan yang telah lulus; bukan jalan pintas melewati gate CP0–CP8.

| Substep | Isi |
| --- | --- |
| CP9.1 | Integrated dependency dan authority audit |
| CP9.2 | Owner workflow acceptance |
| CP9.3 | Personal JARVIS end to end |
| CP9.4 | Engineering/build end to end |
| CP9.5 | Foundry → Capability → Task flow |
| CP9.6 | Learning candidate → shadow → promotion flow |
| CP9.7 | Security, recovery, partial failure dan chaos acceptance |
| CP9.8 | Packaging dan product target acceptance |
| CP9.9 | Final resulting-main/product receipt |

**Acceptance:** source, task, grant, provider generation, efek dan hasil tetap dapat ditelusuri lintas subsistem; fallback menunjukkan kelas eksekusinya; kegagalan sebagian tertangani; semua keputusan aktivasi dapat diaudit/dibatalkan sesuai domain. Deployment produksi tetap memakai approval dan receipt exact artifact/lingkungan.

### Normalisasi label lama

M0/M1/M2, SK-01, M3-A, SCRS v0 adalah slice historis CP0. M3-B dipetakan ke CP1; M4→CP2, M5→CP3, M6→CP4, M7→CP5, M8→CP6, M9→CP7, M10→CP8. Nomor PR GitHub adalah identitas perubahan, bukan nomor CP.

Draft `CP-00…CP-12` tidak lagi menjadi urutan planning. Pemetaan tanggung jawabnya: CP-00→CP0; CP-01→riset dokumentasi/CP6 qualification; CP-02 dan CP-04→CP2; CP-03→CP1; CP-05/06→CP3; CP-07/08→CP4; CP-09→CP5; CP-10→CP6; CP-11→CP7; CP-12→CP8. CP9 adalah integrasi produk. Rencana 12 bulan dalam corpus merupakan rekomendasi historis, bukan deadline resmi tanpa keputusan pemilik.

<!-- END DERIVED ROOT ROADMAP -->

## Catatan histori

Versi roadmap sebelum revisi ini masih menyebut CP0 terbuka. Status tersebut telah digantikan oleh penerimaan CP0 pada SHA di atas. Bukti M1/M2/M3-A/SCRS tetap dapat diperiksa pada [current-state](current-state.md); hasil pengujian historis tidak dipindahkan ke revision baru. PR #17 pada `e8f82b06868311a19f65ae03782a3b499e04ba1a` adalah proposal terdahulu dan perlu direkonsiliasi dengan README ini sebelum kelak diintegrasikan.
