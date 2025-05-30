from typing import Generator

def generate_prompt_chunk(content: str, prompt_template: str, model: str, system_text: str, max_tokens: int) -> Generator[str, None, None]:
    """Generate chunks of content that fit within token limits.

    Args:
        content: The content to chunk.
        prompt_template: The template for the prompt.
        model: The model name.
        system_text: The system text.
        max_tokens: The maximum number of tokens.

    Yields:
        Chunks of content formatted with the prompt template.
    """
    # Simple chunking by paragraphs for now
    paragraphs = content.split("\n\n")
    current_chunk = []
    current_length = 0

    for paragraph in paragraphs:
        # Rough estimate of tokens (4 chars per token)
        paragraph_length = len(paragraph) // 4
        if current_length + paragraph_length > max_tokens:
            if current_chunk:
                yield prompt_template.format(content="\n\n".join(current_chunk))
            current_chunk = [paragraph]
            current_length = paragraph_length
        else:
            current_chunk.append(paragraph)
            current_length += paragraph_length

    if current_chunk:
        yield prompt_template.format(content="\n\n".join(current_chunk))

def reduce_message_length(gen: Generator[str, None, None], model: str, system_text: str, max_tokens: int) -> str:
    """Reduce the length of a message to fit within token limits.

    Args:
        gen: Generator of message chunks.
        model: The model name.
        system_text: The system text.
        max_tokens: The maximum number of tokens.

    Returns:
        The reduced message.
    """
    # For now, just return the first chunk
    return next(gen) 