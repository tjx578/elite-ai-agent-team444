# WebMCP donor research portfolio

## Status

`RESEARCH / FUTURE_CHECKPOINT / NO_RUNTIME_EFFECT`

Observed on 2026-09-29. Exact revisions are research bindings, not active
dependencies. Admission requires the owning checkpoint and CP6 qualification
where donor acquisition applies.

| Repository | Observed revision | Role |
| --- | --- | --- |
| `webmachinelearning/webmcp` | `0957b0b8f1e32c401d4248424719a4851d4202c4` | canonical protocol/spec knowledge |
| `webmachinelearning/webmcp-types` | `a8d8292ff645b691bfdb529484d3c089e81e8c28` | typed contract donor |
| `GoogleChromeLabs/webmcp-tools` | `a66c1be1caee78bb98b9781bf5cb4413ad2ccac7` | implementation/Page Agent/Evals/Studio donor |
| `GoogleChromeLabs/use-webmcp-tool` | `9f0dc6eddf88cff65ebe877f199d4547e74ab31e` | React lifecycle donor |
| `webmaxru/web-ai-agent-skills` | `03b778c8ef822c98b112fd3617050c72d78f4d60` | primary WebMCP skill donor |
| `TueJon/webmcpify` | `c17d1f1382e306296becc0e8294106c477e13d40` | retrofit/verify/heal/audit skill donor |
| `nekuda-ai/webmcp-kit` | `f0298ec9f26af13e477b9141ab4d8f2a6c23426d` | secondary implement/verify/migrate skill donor |
| `signettai/signett` | `cb9be5ff2e9ca669c14e596673355d1ce58d3924` | secure execution/idempotency/recovery donor |
| `WebMCP-org/npm-packages` | `1c7a398a77fa54e54b4d3fdd7ed05d19efb067d5` | polyfill/transport/bridge/runtime reference |
| `opentiny/webmcp-sdk` (`dev`) | `47a2b031dfd77db19e18b5e7621976c5885bd924` | CDP/WXT fallback and WebSkills donor |
| `nekuda-ai/WindTunnel` | `5ca8644e23826ebb30108e7bad240b61043bfe67` | CP8 benchmark methodology donor |

## Capability extraction

~~~text
browser.webmcp.discover      <- spec + types + Chrome Page Agent
browser.webmcp.invoke        <- spec + Chrome Page Agent
browser.webmcp.author        <- webmaxru skill + Chrome demos
browser.webmcp.lifecycle     <- use-webmcp-tool + MCP-B
browser.webmcp.secure-action <- Signett
browser.webmcp.retrofit      <- webmcpify + WebMCP Kit
browser.webmcp.browser-fallback <- OpenTiny isolated CDP patterns
browser.webmcp.bridge        <- MCP-B bridge/relay patterns
browser.webmcp.evaluate      <- WebMCP Evals + WindTunnel
~~~

## Candidate WOLF15 skills

- `webmcp-protocol-canon`
- `webmcp-tool-authoring`
- `webmcp-app-retrofit`
- `webmcp-secure-execution`
- `webmcp-browser-runtime`
- `webmcp-browser-fallback`
- `webmcp-evaluation`

These are candidates, not installed skills.

## Rules

- official spec knowledge outranks donor convenience APIs;
- `document.modelContext` is canonical for the researched revision;
- donor skill/source is untrusted input;
- no bulk skill overwrite;
- real-profile/WXT browser reuse is higher-scope than isolated browsing;
- whole-runtime donor import is rejected;
- benchmark claims require WOLF15 reproduction.

See [checkpoint map](checkpoint-map.md).
