# BIPKB project instructions

Read README.md, BIPKB_Research_Protocol.md, CHANGELOG.md and the Machine Reference before changes.

- BIPKB_Machine_Reference.json owns structured records. The Scientific Reference Register presents them for human reading; the Research Protocol owns methods. Later analytical documents own their authored prose.
- This is a populated documentary-candidate corpus; the original template baseline is retained in Development. Further research intake, evidence acquisition, identifier issuance, scientific classification adoption and publication require explicit scoped approval. Do not infer approval from creating these files.
- Preserve issued identities, evidence editions, attribution, uncertainty and distinctions between omitted, unknown, not applicable and confirmed absent information. Never infer scientific verification from project acceptance or structural checks.
- Keep classifications separate from memberships and relationships separate from identity. Do not infer environmental causes from observed traits or phenotypes.
- DRM principles guide development; MSP remains an unadopted candidate. Do not copy neighbour schemas or classifications, claim conformance, advance a DRM phase or implement automatic synchronisation without approval.
- Run `python3 -B scripts/validate_bipkb.py` after changes and report optional dependency limits. This validator is a structural check, not comprehensive scientific or rights validation.
- Keep work within BIPKB. Preserve other workspaces and research repositories. Do not stage, commit, configure remotes, push, create releases, select a licence or publish without explicit authorisation.

- Preserve all 293 A1 origins and complete fields/context; never extract from A2 alone or silently replace originals with corrections. Scientific Register is generated: edit JSON authority, then run `python3 -B scripts/render_bipkb.py`; editable annotated Mermaid sources own diagram content. Run parity checks and regression tests. Do not reallocate existing local IDs.
