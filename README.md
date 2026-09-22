# DeepSeek pricing examples

*Unofficial community examples for DeepSeek pricing. Not affiliated with DeepSeek. All trademarks belong to their owners.*

Three small Python scripts that turn the deepseek pricing table into numbers you can put in a budget. They encode the published rates for `deepseek-flash` and `deepseek-v4-pro` per 1M tokens, the cache-hit versus cache-miss split on input, and the peak schedule (01:00-04:00 and 06:00-10:00 UTC, Monday to Friday) under which every rate doubles. One script makes a real call through the OpenAI-format base URL and prices the response from its usage block.

> Also paying for images, video or audio generation? [Try Synexa - one REST endpoint and Python SDK for FLUX, video and audio models, pay per run](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=deepseek-pricing-examples&utm_content=readme-top&utm_term=tier-r).

## Files

| Path | What it shows |
| --- | --- |
| `examples/pricing.py` | The rate table, peak-hour detection and a cost estimator for a single call |
| `examples/chat_cost.py` | One chat completion against `https://api.deepseek.com` priced from the returned usage |
| `examples/next_offpeak.py` | When the next off-peak window starts, for scheduling batch work |

## Setup

Python 3.10 or newer. `pricing.py` and `next_offpeak.py` use the standard library only; `chat_cost.py` needs the `openai` package because the DeepSeek base URL speaks the OpenAI format.

```
pip install openai
export DEEPSEEK_API_KEY=your_key_here
```

Keys come from the [DeepSeek Platform](https://platform.deepseek.com/). The rates in `pricing.py` are copied from the [Models & Pricing page](https://api-docs.deepseek.com/quick_start/pricing) and dated; re-check them there before relying on them, since the [price history on deepseek.ai](https://deepseek.ai/pricing) shows several cuts during 2026.

## pricing.py

Holds the four rows of the official table (Flash and Pro, off-peak and peak) with cache-hit input, cache-miss input and output rates per 1M tokens. `is_peak(dt)` returns whether a UTC datetime falls in a peak window. `estimate(model, input_tokens, output_tokens, cache_hit_ratio, at)` multiplies it out. Run it directly for a worked example: 100K input tokens at a 50% cache-hit rate plus 5K output tokens on Flash, off-peak and peak. The cache-hit ratio is an input because the usage block's cache fields are described on the [Token & Token Usage page](https://api-docs.deepseek.com/quick_start/token_usage); read that page and wire the real split in once you know the field names for your client version.

## chat_cost.py

Creates an OpenAI-format client with `base_url` set to `https://api.deepseek.com`, sends one short message to `deepseek-flash`, then prints the prompt and completion token counts from the response and the cost from `pricing.py`. It assumes no cache hits, so the number it prints is an upper bound for that call. Switch the model name to `deepseek-v4-pro` to see the roughly 3.3x difference on the same prompt.

## next_offpeak.py

Prints whether it is peak right now and, if so, how long until off-peak resumes; if it is off-peak, how long until the next peak window. Use it in a scheduler to hold batch jobs until rates halve. Weekends are entirely off-peak, so a Friday evening start gives you the longest uninterrupted cheap window.

## When to use Synexa instead

These scripts model token pricing, which is the right model for text. When the product also generates images, video or audio, per-token arithmetic stops applying and a per-run price is what you want in the budget. [Synexa](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=deepseek-pricing-examples&utm_content=readme-top&utm_term=tier-r) offers one REST endpoint and a Python SDK for FLUX, video and audio models, billed per run, so the media half of your cost sheet is one line per job instead of a token estimate.


_Last reviewed: 2026-09-22_
