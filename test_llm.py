import json
import time
import ssl
import urllib.request

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

KEY = "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"

MODELS = []

PROMPT = """Верни JSON с фильтрами для поиска товаров по запросу "белые найки до 10000".

Формат:
{
  "filters": {"q": "...", "color": [...], "price_max": 0},
  "explanation": "..."
}"""

def test_model(model):
    t0 = time.time()
    try:
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": PROMPT}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }).encode()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            elapsed = round(time.time() - t0, 2)
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            has_filters = "filters" in parsed
            has_explanation = "explanation" in parsed
            ok = "✅" if has_filters and has_explanation else "⚠️ "
            return f"{ok} {elapsed}s — {json.dumps(parsed, ensure_ascii=False)[:120]}"

    except urllib.error.HTTPError as e:
        body = e.read().decode()[:150]
        return f"❌ HTTP {e.code} — {body}"
    except TimeoutError:
        return f"⏱ timeout ({round(time.time() - t0, 1)}s)"
    except json.JSONDecodeError as e:
        return f"⚠️  невалидный JSON: {str(e)[:80]}"
    except Exception as e:
        return f"❌ {type(e).__name__}: {str(e)[:100]}"


if __name__ == "__main__":
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {KEY}"},
    )
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        data = json.loads(resp.read())
        print(json.dumps(data, indent=2, ensure_ascii=False))
