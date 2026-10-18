# Local models with Codex on Windows

Use this only when the user wants local inference. Do not install software, download models, or change settings without that request. Confirm current official vendor instructions before giving version-specific steps.

## Choose the integration

There are two separate cases:

1. **Codex CLI with a local backend.** Current LM Studio documentation describes an OpenAI-compatible Responses API and starting Codex with `codex --oss`; its documented default port is `1234`. This is the most direct documented route for asking Codex CLI to use downloaded local models. Confirm the installed Codex CLI supports the documented flags and that the selected model supports the needed context and coding/tool behavior.
2. **Codex desktop current session.** A project skill does not itself change the model running the current desktop session. Do not claim that it can. Offer the CLI route or whatever model/backend settings the installed desktop app officially exposes, after checking the current official product docs.

LM Studio is a practical first choice when the user wants a GUI, model selection, and an OpenAI-compatible local server. Ollama and llama.cpp also expose local APIs useful to custom scripts, but do not assume they are interchangeable with Codex CLI's complete Responses/tool-use needs. Confirm API compatibility for the specific workflow before recommending them as the Codex backend.

## Hardware and model selection

Before recommending a checkpoint, confirm GPU vendor/model, available VRAM, OS/driver, target context, and whether quality, speed, or tool use is the priority. Compare model family, parameter count, quantization, context length, tool calling/structured JSON support, license, and disk/RAM needs. A 24 GB VRAM GPU with 128 GB RAM can host useful quantized coding models, but does not identify the exact suitable checkpoint by itself. Avoid promising a particular model's fit without checking its actual quantized size and runtime requirements.

Start with a small synthetic task. Verify responses stay local, Codex can read/write only the intended workspace, tool calls work, and context length handles a real but non-sensitive sample. Do not use private project data for the first connectivity test.

## Privacy checks

- Bind the inference server to loopback unless the user deliberately configures a secured LAN service.
- Disable cloud fallback, telemetry/sharing options where available, and remote model providers for workflows expected to stay local; verify behavior in the runtime's current settings/docs.
- Do not put API keys into shell history or command-line arguments. If a local server requires a placeholder key, follow its documentation and avoid reusing a real credential.
- Treat OpenAI-compatible API shape as protocol compatibility, not evidence of local processing. Verify the configured base URL, loaded model, runtime process, and network behavior.
- Keep model downloads, caches, prompts and outputs out of the repository and backup exclusions only if they are reproducible and the user agrees.

## Official references

- [LM Studio: Use Codex](https://lmstudio.ai/docs/integrations/codex)
- [LM Studio: Local API server](https://lmstudio.ai/docs/developer/core/server)
- [LM Studio: OpenAI-compatible endpoints](https://lmstudio.ai/docs/developer/openai-compat)
- [llama.cpp server API](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
