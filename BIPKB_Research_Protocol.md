# BIPKB — Research Protocol

**Protocol edition: 0.2.0.** Work in Progress — Academic Research Resource. Bounded documentary candidate intake completed for owner review; no Stage A research or scientific verification performed. The former 0.1.0-template.1 baseline is preserved in Development, not a research release.

## Scope and research boundaries

The provisional Bioindicators and Phenotypes Knowledge Base concerns indicator species and other bioindicators, observable phenotypes, functional traits, phenotypic plasticity, organismal environmental responses and evidence-based ecological interpretation. This statement records the agreed scope, not findings or a completed domain-requirements study.

EII defines indicators; OSDS concerns observation systems and methods; GISDS concerns spatial information sources. BIPKB studies biological observations, responses and qualified interpretation. IRKB owns independent interdisciplinary synthesis; DRM provides developing methodology and interoperability governance. Boundaries allow overlap and explicit source-owned references without transferring authority or copying another database's corpus.

## Corpus, analysis and synthesis

The corpus will hold accountable source-grounded records, not automatically accepted truths. Analysis interprets specified evidence with explicit assumptions. Synthesis connects findings under authored responsibility. Later analytical prose retains its own authority; acceptance into a corpus does not verify its science or approve every downstream interpretation.

## File authorities

[BIPKB_Machine_Reference.json](BIPKB_Machine_Reference.json) is the sole structured-record authority. [The Scientific Register](BIPKB_Scientific_Reference_Register.md) presents structured material for human reading. This protocol owns methodology; README is the introduction. The local [schema](BIPKB_Machine_Reference.schema.json) checks a local typed documentary serialization, not scientific adequacy or DRM conformance. `scripts/render_bipkb.py` deterministically generates the Scientific Register from JSON and SVGs from annotated Mermaid sources; parity is mandatory. No automatic source synchroniser is implemented.

## Candidate entity distinctions

Keep organism or taxon identity, observed phenotype or trait, observation context, proposed ecological interpretation and supporting evidence distinct. These remain scientific modelling distinctions to investigate; the populated documentary types are not a final biological entity model. An observed phenotype must not automatically establish an environmental cause. Alternative explanations, context, temporal limits and uncertainty need evidence and later domain review.

## Identity and unresolved choices

Local documentary identifiers were issued for this authorised intake; they do not establish accepted scientific entities or external ownership. See [local identifier policy](#local-identifier-policy). Source-owned IDs remain separate. A reference to another database retains its namespace and version. Resolving a locator does not prove equivalence.

Omitted means not supplied, not absent. Unknown information must be explicitly qualified in an appropriate field; not applicable requires a reason. Confirmed absence requires evidence and scope. Bare null is not permitted by this local schema and must never be used as proof of absence. Do not create dummy strings to satisfy a required field: defer intake or propose a reviewed schema extension when the model cannot faithfully represent evidence.

## Evidence, citations and source editions

Entries require accountable provenance and status. References retain actual citations without invented bibliographic completion. Evidence provenance identifies a portable locator, recoverable source edition, contributor/process, rights status and evidence status. Preserve source editions, encoding, locators and fingerprints when material is acquired; record the fingerprint algorithm and exact-byte scope. Keep retrieval/recovery dates distinct from unknown original dates.

Use repository-relative locators or scoped source identifiers with a private access mapping where necessary; do not require private absolute workstation paths in public research records. Public availability is not reuse permission. Rights, sensitivity and unknown restrictions require review before ingestion or publication. This intake uses preserved A1, review and A2 editions; no external datasets or original transcript were acquired. The public record uses portable filenames and exact pins; Development retains private access mappings.

## Classification stewardship and memberships

Definitions and assignments are separate collections. Future definitions identify owner, version, meaning, provenance and status. Memberships refer to a record and definition explicitly; membership changes do not change entity identity. Preserve origin classifications and distinguish locally stewarded extensions from shared adoption. Thirty-nine proposed definition entries are populated; no scientific scheme is adopted and no memberships are inferred. The family codes identify documentary source families, not biological assignments.

## Relationship assertions and uncertainty

Relationships are evidence-backed assertions, not identity fields. Entries declare subject, predicate, object, qualification, provenance and independent status. Internal references must resolve; the fifteen A1 relationships use explicit unresolved-label endpoints, preserving complete predicates and warnings without fabricating entity records. Keep evidence, confidence, disagreement, reference resolution, same-entity claims and semantic alignment distinguishable. No relationship vocabulary or ecological causal claim has been adopted.

## Acceptance and scientific verification

Project inclusion, canonical-record lifecycle, scientific verification and rights permission are separate decisions. The current six-field status object separates documentary inclusion, proposal review, canonical source lifecycle, scientific verification, source access and reuse rights. It is not a universal state machine. Reviewer roles, permitted transitions, evidence thresholds and approval records remain to be designed. No reviewer event or scientific acceptance is fabricated by intake. D-family reported authority is differentiated between user, assistant and mixed attribution; A1 reported decisions are not authenticated original approvals.

## Independent versions and future intake

The initial independent document/schema editions were 0.1.0-template.1. This corpus/document revision is 0.2.0; local schema 0.2.0 and protocol edition 0.2.0 have independently stated meanings, not research releases. Future record, classification, source-edition, protocol, schema and publication changes require separate version meanings and compatibility review. Schema 0.2.0 changes the template serialization and is not assumed backward-compatible merely because it is a MINOR number. The pre-intake template remains recoverable in Development. Preserve prior evidence and issued identities. Research intake requires explicit scope approval, a suitable model, traceable sources, preservation checks and a separate scientific review. No Stage A gate is completed by these templates.

## ADDG workspace responsibilities

Archive preserves original research evidence and sources immutably, not code or development snapshots. Data holds operational datasets, processed records, indexes and database files with lineage. Development holds experiments, extractions, candidate classifications, schema prototypes and reviews; these are not automatically accepted research. Git holds curated structured records, methodology and human presentation. None of the other workspaces is a second editable authority for Git records. No speculative connecting symlinks or source directories are created.

## DRM alignment and limitations

The current curated DRM documentation records Phases 1–3 development completed and the two bounded Phase 4 documentary pilots accepted and closed. DRM-MSP 0.1.0 review revision 2 remains an unadopted candidate; DRM Phase 5 is not authorised. Its example JSON envelope and enums are not mandatory scientific formats. BIPKB neither adopts them nor claims DRM/MSP conformance or advances a phase.

Applicable design principles include stable identity and scoped references; provenance, evidence editions and rights; separate lifecycles, decisions and acceptance authority; independent versions; classification ownership and local extension; qualified relationships, resolution and disagreement; bounded validation and preservation. These principles do not supply missing scientific definitions or operational federation services.

## Validation boundary and pending work

Run `python3 -B scripts/validate_bipkb.py`. It checks local field structure, counts, unique identities, required provenance links and selected internal references. Optional installed jsonschema adds Draft 2020-12 schema checking. Deterministic generation/parity, full source-byte reconstruction and original-field checks now supplement those checks. Neither validates scientific truth, actual rights, genuine reviewer authority, historical non-reuse or complete original-conversation recovery.

Pending decisions include detailed biological/context models, external identity and source editions, scientific review roles and thresholds, rights, adopted classifications, original transcript/map recovery and future discovery. The present ID policy and candidate statuses describe documentary intake only; they do not decide those scientific questions. Extensions require deliberate schema, version and validator review.

## Local identifier policy

IDs are scoped to BIPKB documentary objects. Prefixes are `BIPKB:REC-`, `REF-`, `CLS-`, `REL-`, `EX-`, `NOTE-`, `TASK-`, `AST-`, `PV-`, `CTX-A1-`, `CTX-A2-` `IDR-` and `CHAT-`; each full ID carries the BIPKB namespace. Four-digit suffixes are allocated monotonically within typed collections (three for context spans), independent of future display order or scientific classification. Initial allocation follows the pinned audit's documentary order once only. Never regenerate or renumber IDs after issuance; later additions use the next unused number. Never reuse withdrawn/superseded IDs. Corrections preserve an ID only for the same documentary object; materially different identities require a separately recorded review and new ID. Aliases and duplicate hypotheses do not merge entities automatically. Context IDs identify source spans, not scientific entities; `BIPKB-A1-*` remain exact scoped origin references.

## Intake evidence and preservation contract

A1, its independent review and A2 are separate assistant-authored evidence layers. The Machine Reference pins exact UTF-8 byte SHA-256 values, editions and sizes. Its provenance collection is also the 293-ID disposition crosswalk: exact row, original column names, source section/table/line, typed destination, A2 recommendation and limits, inherited context and deferral reasons. Typed `fields` retain every original source column. Twenty-three A1 and twenty A2 unindexed spans preserve all complementary context; rows plus spans reconstruct the respective complete source bytes. This preserves interpretation levels, proposed source-record fields, evidence keys, inherited statuses, bibliography/access qualifications and historical not-performed declarations. Historical instructions/QA statements are evidence, not current authority.

The review is consulted and pinned but not embedded in full. Twelve A2 corrections retain their precise row, origin, evidence and verification limits; original A1 assertions remain unchanged. The WOODIV 2021/2025, TRY v7 and FloraVeg 2023/current distinctions are reported, not independently verified. No fresh primary checks were performed. Duplicate Open Traits Network and TDWG mentions remain separate pending identity review. Fifteen examples are illustrative-only; fifteen relationships retain unresolved endpoints; thirty-two tasks/gaps remain open. No classification memberships were inferred.

Only five later turns of the normal BIPKB Overview were retrievable, with one truncated response and no older cursor. The early framing and original diagram remain unavailable; no complete L0 audit is claimed. One retrieved reconciliation fragment is separately preserved as supplementary evidence, including details not fully captured by A2 (WOODIV metrics, per-resource cautions and proposed conceptual navigation). Its hash pins only the retrieved 20,000-character fragment, not the complete message. Exact thread/turn/message IDs, speaker, turn timestamp and fragment lines are retained. No new scientific-entity records or adopted classifications are inferred from it; its scientific claims remain assistant-reported. Transient citation tokens are retained in JSON but omitted from human presentation with that transformation disclosed. The conceptual map is a labelled reconstruction, not the original. Its labels and qualified edges are sourced to A1 concepts/examples/relationships. The federation diagram additionally uses A1 scope/boundaries and A2's proposed EIRKB boundary review.

The frozen baseline, independent pre-intake audit, private source mappings, retrieval payload and validation logs are in the verified BIPKB Development workspace. Archive and Data remain unchanged; no full L0–L4 pipeline or second editable structured authority is created. The current owner instruction authorises documentary inclusion only, not scientific acceptance, source-owner lifecycle changes, licensing, MSP adoption, DRM Phase 5 or Stage A/B/C research.

## Reproducibility and bounded regression checks

Run `python3 -B scripts/render_bipkb.py --check`, `python3 -B scripts/validate_bipkb.py` and `python3 -B -m unittest discover -s tests -v`. Optional `--source-dir` on the validator compares the preserved archived input files too; normal checks use reconstructed pinned evidence without private filesystem dependencies. The installed optional `jsonschema` adds full Draft 2020-12 validation; the standard-library checker covers the closed subset used by this edition. Negative tests reject lost original fields/caveats, duplicated IDs, dangling provenance, changed source locators, false scientific/rights/authority promotion, empirical-example conversion, endpoint warning loss and presentation drift. Repeated output bytes must be identical. These controls establish bounded documentary preservation, not semantic correctness, source completeness, actual external rights or scientific conformance.
