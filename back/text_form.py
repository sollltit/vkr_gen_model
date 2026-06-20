import re


def normalize_markdown(text: str):


    # Переносы перед таблицами
    text = re.sub(
        r"(\|[^\n]+\|)",
        r"\n\1",
        text
    )

    # Чиним таблицы в одну строку
    text = text.replace("| |", "|\n|")


    text = re.sub(
        r"(#{1,6}\s)",
        r"\n\n\1",
        text
    )


    text = re.sub(
        r"\s-\s",
        r"\n- ",
        text
    )

    text = re.sub(
        r"\s\*\s",
        r"\n* ",
        text
    )



    text = re.sub(
        r"\s(\d+\.)\s",
        r"\n\1 ",
        text
    )


    # python def
    text = re.sub(
        r"python\s+def",
        "```python\ndef",
        text
    )

    # js function
    text = re.sub(
        r"javascript\s+function",
        "```javascript\nfunction",
        text
    )

    # Закрываем незакрытые code blocks
    if text.count("```") % 2 != 0:
        text += "\n```"

    text = re.sub(
        r"\.\s([А-ЯA-Z])",
        r".\n\n\1",
        text
    )


    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    text = fix_latex(text)
    
    return text.strip()


def format_math_expressions(text: str) -> str:

    code_blocks = []

    def save_code(match):

        code_blocks.append(match.group(0))

        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    text = re.sub(
        r"```.*?```",
        save_code,
        text,
        flags=re.DOTALL
    )

    inline_codes = []

    def save_inline(match):

        inline_codes.append(match.group(0))

        return f"__INLINE_CODE_{len(inline_codes)-1}__"

    text = re.sub(
        r"`.*?`",
        save_inline,
        text
    )

    text = re.sub(
        r"(\d)\s*\*\s*(\d)",
        r"\1 × \2",
        text
    )

    text = re.sub(
        r"(\d)\s*/\s*(\d)",
        r"\1 ÷ \2",
        text
    )

    text = re.sub(
        r"(\d+)\^(\d+)",
        r"\1^\2",
        text
    )

    for i, block in enumerate(inline_codes):

        text = text.replace(
            f"__INLINE_CODE_{i}__",
            block
        )

    for i, block in enumerate(code_blocks):

        text = text.replace(
            f"__CODE_BLOCK_{i}__",
            block
        )

    return text

def replace_inline(match):

    content = match.group(1).strip()

    if re.search(r"[а-яА-Я]", content):
        return f"({content})"

    if (
        "\\" in content
        or "^" in content
        or "_" in content
        or "=" in content
    ):
        return f"${content}$"

    return f"({content})"

def fix_latex(text: str):

    text = re.sub(
        r"\\\[\s*(.*?)\s*\\\]",
        r"\n$$\n\1\n$$\n",
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r"\[\s*(\\[a-zA-Z]+.*?|.*?=.*?)\s*\]",
        r"\n$$\n\1\n$$\n",
        text,
        flags=re.DOTALL
    )


    text = re.sub(
        r"\(([^()\n]+)\)",
        replace_inline,
        text
    )


    text = text.replace(
        r"\left\frac",
        r"\frac"
    )

    text = re.sub(
        r"\${3,}",
        "$$",
        text
    )

    text = re.sub(
        r"_\{([а-яА-Яa-zA-Z\s]+)\}",
        r"_{\\text{\1}}",
        text
    )

    text = re.sub(
        r"\$\s*(.*?)\s*\$",
        r"$\1$",
        text
    )

    return text