"""Send one chat completion to DeepSeek and price it from the usage block.

The DeepSeek base URL speaks the OpenAI format, so the openai package works
with base_url pointed at https://api.deepseek.com.

Usage:
    pip install openai
    export DEEPSEEK_API_KEY=...
    python3 examples/chat_cost.py [deepseek-flash|deepseek-v4-pro]
"""
import os
import sys
from datetime import datetime, timezone

from openai import OpenAI

from pricing import estimate, is_peak

BASE_URL = 'https://api.deepseek.com'


def main(argv: list[str]) -> int:
    key = os.environ.get('DEEPSEEK_API_KEY')
    if not key:
        print('set DEEPSEEK_API_KEY first (keys come from platform.deepseek.com)')
        return 1
    model = argv[1] if len(argv) > 1 else 'deepseek-flash'

    client = OpenAI(api_key=key, base_url=BASE_URL)
    resp = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': 'In one sentence, what is a token?'}],
    )
    usage = resp.usage
    now = datetime.now(timezone.utc)

    # cache_hit_ratio=0 is a deliberate upper bound; see the Token & Token Usage
    # docs for the cache fields your client version exposes on `usage`.
    cost = estimate(model, usage.prompt_tokens, usage.completion_tokens,
                    cache_hit_ratio=0.0, at=now)

    print(resp.choices[0].message.content.strip())
    print(f'model:      {model}')
    print(f'input:      {usage.prompt_tokens} tokens')
    print(f'output:     {usage.completion_tokens} tokens')
    print(f'window:     {"peak" if is_peak(now) else "off-peak"} ({now:%Y-%m-%d %H:%M} UTC)')
    print(f'cost:       ${cost:.6f} (upper bound, no cache hits assumed)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
