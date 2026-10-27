import io
import av


def has_video_stream(content: bytes) -> bool:
    container = av.open(io.BytesIO(content))
    return len(container.streams.video) > 0


def extract_audio_only(content: bytes) -> bytes:
    """Re-mux (no re-encode) just the audio track out of a combined audio+video
    clip, so Whisper/librosa always get a plain audio container regardless of
    whether the browser recorded video alongside it."""
    in_container = av.open(io.BytesIO(content))
    in_stream = in_container.streams.audio[0]

    out_buf = io.BytesIO()
    out_container = av.open(out_buf, mode="w", format="webm")
    out_stream = out_container.add_stream_from_template(in_stream)

    for packet in in_container.demux(in_stream):
        if packet.dts is None:
            continue
        packet.stream = out_stream
        out_container.mux(packet)
    out_container.close()
    return out_buf.getvalue()
