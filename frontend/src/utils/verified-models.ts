// Here are the list of verified models and providers that we know work well with OpenHands.
export const VERIFIED_PROVIDERS = [
  "openai",
  "azure",
  "anthropic",
  "deepseek",
  "github",
];
export const VERIFIED_MODELS = [
  "o3-mini-2025-01-31",
  "o3-2025-04-16",
  "o4-mini-2025-04-16",
  "claude-3-5-sonnet-20241022",
  "claude-3-7-sonnet-20250219",
  "deepseek-chat",
  // GitHub Models
  "openai/gpt-4.1",
  "openai/gpt-4o",
  "openai/o1",
  "openai/o3",
  "openai/o3-mini",
  "meta/llama-3.3-70b-instruct",
  "mistral-ai/mistral-large-2411",
  "deepseek/deepseek-r1",
];

// LiteLLM does not return OpenAI models with the provider, so we list them here to set them ourselves for consistency
// (e.g., they return `gpt-4o` instead of `openai/gpt-4o`)
export const VERIFIED_OPENAI_MODELS = [
  "gpt-4o",
  "gpt-4o-mini",
  "gpt-4-turbo",
  "gpt-4",
  "gpt-4-32k",
  "o1-mini",
  "o1",
  "o3",
  "o3-2025-04-16",
  "o3-mini",
  "o3-mini-2025-01-31",
  "o4-mini",
  "o4-mini-2025-04-16",
];

// LiteLLM does not return the compatible Anthropic models with the provider, so we list them here to set them ourselves
// (e.g., they return `claude-3-5-sonnet-20241022` instead of `anthropic/claude-3-5-sonnet-20241022`)
export const VERIFIED_ANTHROPIC_MODELS = [
  "claude-2",
  "claude-2.1",
  "claude-3-5-sonnet-20240620",
  "claude-3-5-sonnet-20241022",
  "claude-3-5-haiku-20241022",
  "claude-3-haiku-20240307",
  "claude-3-opus-20240229",
  "claude-3-sonnet-20240229",
  "claude-3-7-sonnet-20250219",
];

// GitHub models are returned with the full provider/model format
export const VERIFIED_GITHUB_MODELS = [
  "openai/gpt-4.1",
  "openai/gpt-4.1-mini",
  "openai/gpt-4.1-nano",
  "openai/gpt-4o",
  "openai/gpt-4o-mini",
  "openai/o1",
  "openai/o1-mini",
  "openai/o3",
  "openai/o3-mini",
  "openai/o4-mini",
  "meta/llama-3.3-70b-instruct",
  "meta/llama-4-maverick-17b-128e-instruct-fp8",
  "meta/llama-4-scout-17b-16e-instruct",
  "meta/meta-llama-3.1-405b-instruct",
  "meta/meta-llama-3.1-70b-instruct",
  "mistral-ai/mistral-large-2411",
  "mistral-ai/mistral-medium-2505",
  "mistral-ai/codestral-2501",
  "deepseek/deepseek-r1",
  "deepseek/deepseek-v3-0324",
  "xai/grok-3",
  "xai/grok-3-mini",
  "microsoft/phi-4",
  "microsoft/phi-4-reasoning",
  "microsoft/mai-ds-r1",
  "cohere/cohere-command-r-plus",
  "ai21-labs/ai21-jamba-1.5-large",
];
