import re


_CHAT_PATTERN = r'(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - ([^:]+): (.*)'
_CHUNK_SIZE = 15


def parse_chat_file(path: str) -> list[str]:
    """Parse a chat export file and return chunks of ~15 messages each."""
    chunks: list[str] = []
    current_chunk = ""
    counter = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(_CHAT_PATTERN, line)
            if not match:
                continue

            date, time, author, message = match.groups()

            if "<Media omessi>" in message:
                continue

            current_chunk += f"[{date} {time}] {author}: {message.strip()}\n"
            counter += 1

            if counter == _CHUNK_SIZE:
                chunks.append(current_chunk)
                current_chunk = ""
                counter = 0

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
