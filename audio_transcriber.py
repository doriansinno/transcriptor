"""Audioaufnahme und Transkription mit Whisper."""
from __future__ import annotations

import queue
import threading
import time
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
import sounddevice as sd
import whisper

RAW_PATH = Path("mitschrift_raw.txt")


class AudioTranscriber:
    """Kapselt Aufnahme- und Transkriptions-Threads."""

    def __init__(self, device_id: int | None, sample_rate: int = 16000, block_duration: int = 5, language: str = "de", model: str = "base") -> None:
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.block_duration = block_duration
        self.language = language
        self.model_name = model

        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._text_queue: queue.Queue[str] = queue.Queue()
        self._running = threading.Event()
        self._record_thread: threading.Thread | None = None
        self._transcribe_thread: threading.Thread | None = None
        self._last_chunks: List[str] = []
        self._max_chunks = 8
        self._lock = threading.Lock()

    @staticmethod
    def list_input_devices() -> List[Tuple[int, str]]:
        devices = sd.query_devices()
        return [(idx, dev["name"]) for idx, dev in enumerate(devices) if dev["max_input_channels"] > 0]

    def start(self) -> None:
        if self._running.is_set():
            return
        self._running.set()
        self._record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self._transcribe_thread = threading.Thread(target=self._transcribe_loop, daemon=True)
        self._record_thread.start()
        self._transcribe_thread.start()

    def stop(self) -> None:
        self._running.clear()
        if self._record_thread:
            self._record_thread.join(timeout=2)
        if self._transcribe_thread:
            self._transcribe_thread.join(timeout=2)

    def _record_loop(self) -> None:  # pragma: no cover - Hardwareabhängig
        block_size = int(self.sample_rate * self.block_duration)
        while self._running.is_set():
            try:
                audio = sd.rec(
                    frames=block_size,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype="float32",
                    device=self.device_id,
                )
                sd.wait()
                self._audio_queue.put(audio.flatten())
            except Exception as exc:
                print(f"Fehler bei der Audioaufnahme: {exc}")
                time.sleep(1)

    def _transcribe_loop(self) -> None:  # pragma: no cover - Whisperabhängig
        model = whisper.load_model(self.model_name)
        while self._running.is_set():
            try:
                audio = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                result = model.transcribe(audio, language=self.language)
                text = result.get("text", "").strip()
                if text:
                    print(f"[Transkription] {text}")
                    with RAW_PATH.open("a", encoding="utf-8") as handle:
                        handle.write(text + "\n")
                    self._text_queue.put(text)
                    self._remember_chunk(text)
            except Exception as exc:
                print(f"Fehler bei der Transkription: {exc}")

    def _remember_chunk(self, text: str) -> None:
        with self._lock:
            self._last_chunks.append(text)
            if len(self._last_chunks) > self._max_chunks:
                self._last_chunks = self._last_chunks[-self._max_chunks :]

    def get_recent_text(self) -> str:
        with self._lock:
            return "\n".join(self._last_chunks)

    def iter_text(self) -> Iterable[str]:
        while self._running.is_set() or not self._text_queue.empty():
            try:
                yield self._text_queue.get(timeout=0.5)
            except queue.Empty:
                continue
