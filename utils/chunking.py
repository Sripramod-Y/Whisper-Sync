def chunk_by_pauses(transcript : dict, pause_threshold: float = 1.5) -> list:
    """ Split transcript into chunks where pauses > `pause_threshold` seconds. """
    chunks = []
    current_chunk = []
    for i, word in enumerate(transcript["words"]):
        if i> 0 and (word["start"] - transcript["words"][i-1]["end"])> pause_threshold:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
        current_chunk.append(word["word"])
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks