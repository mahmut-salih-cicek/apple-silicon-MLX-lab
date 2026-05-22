import os
import re
import json
import shutil
import queue
import threading
import time
import datetime
import locale
from concurrent.futures import Future

from huggingface_hub import snapshot_download

UI_LANG = "en"
sys_lang = locale.getdefaultlocale()[0]
if sys_lang and sys_lang.startswith("tr"):
    UI_LANG = "tr"

if os.path.exists("app_config.json"):
    try:
        with open("app_config.json", "r") as f:
            _cfg = json.load(f)
            if "ui_lang" in _cfg:
                UI_LANG = _cfg["ui_lang"]
    except:
        pass

def save_app_config(lang):
    with open("app_config.json", "w") as f:
        json.dump({"ui_lang": lang}, f)
    return "Uygulama dilini değiştirdiniz, lütfen değişikliklerin geçerli olması için programı yeniden başlatın." if lang == "tr" else "Language changed, please restart the application to apply changes."

TR_DICT = {
    "title": "🎙️ Chatterbox MLX — Final V9 Fast Stable",
    "description": "M1 / Apple Silicon için Türkçe uzun hikaye TTS + voice cloning.
V9 hedefi: hızlı/stabil MLX üretim, doğal vurgu, kontrollü bekleme ve model seçimi.",
    "model_selection": "🤖 Model Seçimi",
    "model_selection_desc": "`MODEL_ROOT` altında bulunan `chatterbox-*` klasörleri otomatik listelenir.
Örn: `chatterbox-6bit`, `chatterbox-8bit`. Modeli değiştirince generate sırasında otomatik yüklenir.",
    "model_dropdown_label": "MLX Model Klasörü",
    "model_dropdown_info": "Modeli listeden seçin. Eğer yoksa 'Model İndir' kısmından indirebilirsiniz.",
    "load_model_btn": "🤖 Seçili Modeli Yükle",
    "refresh_models_btn": "🔄 Model Listesini Yenile",
    "model_status_label": "Model Durumu",
    "download_models_acc": "⬇️ Model İndir",
    "download_models_desc": "HuggingFace üzerinden Chatterbox modellerini indirin. (Eğer test ediyorsanız bu adımı geçiniz)",
    "download_6bit_btn": "⬇️ Chatterbox 6-bit İndir",
    "download_8bit_btn": "⬇️ Chatterbox 8-bit İndir",
    "download_status": "İndirme Durumu",
    "ui_lang_acc": "🌍 Dil Ayarı / Language Settings",
    "ui_lang_label": "Arayüz Dili / UI Language",
    "ui_lang_btn": "💾 Dili Kaydet / Save Language",
    "ui_lang_status": "Dil Ayarı Durumu",
    "best_practice_acc": "✅ Best Practice / Kullanım İpuçları",
    "preset_acc": "### 💾 Preset / Ses Profili",
    "preset_dropdown": "Kayıtlı Presetler",
    "preset_name_input": "Yeni / Güncellenecek Preset Adı",
    "save_preset_btn": "💾 Mevcut Ayarları Kaydet",
    "load_preset_btn": "📥 Seçili Preseti Yükle",
    "delete_preset_btn": "🗑️ Seçili Preseti Sil",
    "preset_status": "Preset Durumu",
    "text_input_label": "Sentezlenecek Metin",
    "hazirla_btn": "📝 Metni Chatterbox'a Hazırla + Chunk Önizle",
    "ref_audio_label": "🎵 Referans Ses / Voice Clone",
    "output_audio_label": "Üretilen Ses",
    "stats_label": "📊 İstatistikler / Chunk Önizleme",
    "master_btn": "🎚️ YouTube Master WAV hazırla",
    "master_out_label": "YouTube Master WAV / Opsiyonel",
    "audio_settings_label": "### 🎛️ Ses Ayarları",
    "lang_dropdown_label": "🌐 Dil / LANG_CODE",
    "exag_label": "🎭 Exaggeration",
    "cfg_label": "⚡ CFG/Pace",
    "temp_label": "🌡️ Temperature",
    "story_settings_label": "### ⚙️ Uzun Hikaye Ayarları",
    "mode_label": "🎚️ İşleme Modu",
    "chunk_size_label": "📄 Chunk size",
    "max_tokens_label": "🧱 Max new tokens",
    "chunk_gap_label": "⏸️ Chunk arası boşluk/ms",
    "seed_label": "🎲 Random seed (0 = rastgele)",
    "retry_label": "🛡️ Retry (kapalı önerilir - performans için)",
    "save_chunks_label": "💾 Chunk WAV dosyalarını kaydet",
    "generate_btn": "🎙️ Ses Üret (Generate Speech)",
    "model_not_selected_error": "⚠️ Lütfen bir model seçin! Eğer model yoksa 'Model İndir' kısmından indirebilirsiniz.",
    "model_downloading": "⏳ Model indiriliyor, lütfen bekleyin... Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir.",
    "model_downloaded": "✅ Model başarıyla indirildi! Lütfen 'Model Listesini Yenile' butonuna basarak modeli seçin."
}

EN_DICT = {
    "title": "🎙️ Chatterbox MLX — Final V9 Fast Stable",
    "description": "Long story TTS + voice cloning for M1 / Apple Silicon.
V9 target: fast/stable MLX generation, natural prosody, controlled pauses, and model selection.",
    "model_selection": "🤖 Model Selection",
    "model_selection_desc": "`chatterbox-*` folders under `MODEL_ROOT` are listed automatically.
E.g.: `chatterbox-6bit`, `chatterbox-8bit`. The model will be loaded automatically during generation.",
    "model_dropdown_label": "MLX Model Folder",
    "model_dropdown_info": "Select the model. If you don't have one, you can download it from 'Download Model' section.",
    "load_model_btn": "🤖 Load Selected Model",
    "refresh_models_btn": "🔄 Refresh Model List",
    "model_status_label": "Model Status",
    "download_models_acc": "⬇️ Download Model",
    "download_models_desc": "Download Chatterbox models from HuggingFace. (Skip if just testing)",
    "download_6bit_btn": "⬇️ Download Chatterbox 6-bit",
    "download_8bit_btn": "⬇️ Download Chatterbox 8-bit",
    "download_status": "Download Status",
    "ui_lang_acc": "🌍 Dil Ayarı / Language Settings",
    "ui_lang_label": "Arayüz Dili / UI Language",
    "ui_lang_btn": "💾 Dili Kaydet / Save Language",
    "ui_lang_status": "Language Setting Status",
    "best_practice_acc": "✅ Best Practice / Tips",
    "preset_acc": "### 💾 Preset / Voice Profile",
    "preset_dropdown": "Saved Presets",
    "preset_name_input": "New / Update Preset Name",
    "save_preset_btn": "💾 Save Current Settings",
    "load_preset_btn": "📥 Load Selected Preset",
    "delete_preset_btn": "🗑️ Delete Selected Preset",
    "preset_status": "Preset Status",
    "text_input_label": "Text to Synthesize",
    "hazirla_btn": "📝 Prepare Text + Preview Chunks",
    "ref_audio_label": "🎵 Reference Audio / Voice Clone",
    "output_audio_label": "Generated Audio",
    "stats_label": "📊 Statistics / Chunk Preview",
    "master_btn": "🎚️ Create YouTube Master WAV",
    "master_out_label": "YouTube Master WAV / Optional",
    "audio_settings_label": "### 🎛️ Audio Settings",
    "lang_dropdown_label": "🌐 Language / LANG_CODE",
    "exag_label": "🎭 Exaggeration",
    "cfg_label": "⚡ CFG/Pace",
    "temp_label": "🌡️ Temperature",
    "story_settings_label": "### ⚙️ Long Story Settings",
    "mode_label": "🎚️ Processing Mode",
    "chunk_size_label": "📄 Chunk size",
    "max_tokens_label": "🧱 Max new tokens",
    "chunk_gap_label": "⏸️ Chunk gap/ms",
    "seed_label": "🎲 Random seed (0 = random)",
    "retry_label": "🛡️ Retry (off recommended for performance)",
    "save_chunks_label": "💾 Save Chunk WAV files",
    "generate_btn": "🎙️ Generate Speech",
    "model_not_selected_error": "⚠️ Please select a model! If you don't have one, you can download it from the 'Download Model' section.",
    "model_downloading": "⏳ Downloading model, please wait... This may take a few minutes depending on your internet speed.",
    "model_downloaded": "✅ Model downloaded successfully! Please click 'Refresh Model List' and select it."
}

def _t(key):
    return TR_DICT.get(key, key) if UI_LANG == "tr" else EN_DICT.get(key, key)

def download_model_hf(repo_id, local_dir_name):
    try:
        local_dir = os.path.join(MODEL_ROOT, local_dir_name)
        snapshot_download(repo_id=repo_id, local_dir=local_dir)
        return _t("model_downloaded")
    except Exception as e:
        return f"❌ Error: {str(e)}"

import gradio as gr
import soundfile as sf
import numpy as np
import mlx.core as mx
from mlx_audio.tts.utils import load_model
from mlx_audio.tts.generate import load_audio

# ============================================================
# Chatterbox MLX Final V9 Fast Stable Model Selector — Best Practice Edition
# Hedef:
# - Apple Silicon / M1 16 GB için Chatterbox MLX'i stabil çalıştırmak.
# - 30–40 dakikalık Türkçe YouTube hikaye metinlerinde doğal akış, vurgu,
#   noktalama, diyalog ve uzun metin güvenliğini korumak.
#
# Net mimari karar:
# 1) Program tarafı sorunu çözer: long story chunking, diyalog/vurgu ayrımı,
#    Pinokio uyumlu concat, sorunlu chunk retry, MLX post-process.
# 2) Metin tarafı kaliteyi artırır: ChatGPT'ye Chatterbox uyumlu metin yazdırmak
#    önerilir ama tek başına zorunlu güvenlik katmanı değildir.
#
# MLX notu:
# - Gradio UI kütüphanesidir; MLX alternatifi yoktur.
# - soundfile WAV yazmak içindir; MLX alternatifi değildir.
# - NumPy sadece final WAV yazma köprüsü olarak kullanılır.
# - Inference, audio normalize, concat ve opsiyonel trimming/compression MLX üzerinde yapılır.
# ============================================================

MODEL_ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_ROOT, "chatterbox-6bit")
DEFAULT_LANG_CODE = "tr"
OUTPUT_PATH = "uretilen_ses.wav"
YOUTUBE_MASTER_PATH = "uretilen_ses_youtube_master.wav"

SUPPORTED_LANGUAGES = {
    "tr": "Turkish / Türkçe",
    "en": "English",
    "ar": "Arabic",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "es": "Spanish",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hi": "Hindi",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ru": "Russian",
    "sv": "Swedish",
    "sw": "Swahili",
    "zh": "Chinese",
}
CHUNKS_DIR = "generated_chunks"
PRESETS_FILE = "voice_presets.json"
PRESETS_AUDIO_DIR = "saved_voice_refs"

# Bilinçli bekleme markerları.
# Not: "..." model için güvenilir bekleme komutu değildir; gerçek bekleme için marker kullan.
PAUSE_MARK_RE = re.compile(r"\[\[pause:(short|medium|long)\]\]", flags=re.IGNORECASE)
PAUSE_MS = {
    "short": 300,
    "medium": 650,
    "long": 1000,
}

_work_queue = queue.Queue()
_model_lock = threading.Lock()
model = None
active_model_path = None


def log(msg: str):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


# ============================================================
# Ana Thread İş Kuyruğu
# MLX stream/thread sorunlarını azaltmak için inference ana thread'de yürür.
# ============================================================
def _submit_to_main_thread(fn, *args, **kwargs):
    future = Future()
    _work_queue.put((future, fn, args, kwargs))
    return future.result()


def _main_thread_worker():
    print("🔄 [MAIN THREAD] İş kuyruğu dinleniyor...", flush=True)
    while True:
        try:
            future, fn, args, kwargs = _work_queue.get()
            try:
                result = fn(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
        except KeyboardInterrupt:
            print("\n⏹️  Kapatılıyor...", flush=True)
            break


# ============================================================
# Model Seçimi / Lazy Loading
# ============================================================
def _discover_model_paths(root: str = MODEL_ROOT):
    """
    /Users/macpro/chatterbox altında chatterbox-* model klasörlerini bulur.
    Örn: chatterbox-6bit, chatterbox-8bit, chatterbox-fp16.
    """
    paths = []
    try:
        if os.path.isdir(root):
            for name in sorted(os.listdir(root)):
                full_path = os.path.join(root, name)
                if not os.path.isdir(full_path):
                    continue
                if not name.startswith("chatterbox-"):
                    continue
                has_config = os.path.exists(os.path.join(full_path, "config.json"))
                has_model = os.path.exists(os.path.join(full_path, "model.safetensors")) or os.path.exists(os.path.join(full_path, "model.safetensors.index.json"))
                if has_config or has_model:
                    paths.append(full_path)
    except Exception as e:
        log(f"⚠️ Model klasörleri taranamadı: {e}")

    if MODEL_PATH not in paths:
        paths.insert(0, MODEL_PATH)
    return paths


def _model_label(path: str) -> str:
    path = str(path or MODEL_PATH)
    return f"{os.path.basename(path)}  —  {path}"


def _load_model_on_main_thread(model_path: str):
    return load_model(model_path)


def _ensure_model_loaded(model_path: str | None):
    """
    Seçili modeli sadece gerektiğinde yükler.
    Program açılırken model yükleyip UI'ı geciktirmez.
    Model değişirse yeni model yüklenir; generate ayarları aynı çalışır.
    """
    global model, active_model_path

    selected_path = str(model_path or MODEL_PATH).strip() or MODEL_PATH
    with _model_lock:
        if model is not None and active_model_path == selected_path:
            return model, active_model_path, f"✅ Model zaten yüklü: {os.path.basename(selected_path)}"

        if not os.path.isdir(selected_path):
            raise FileNotFoundError(f"Model klasörü bulunamadı: {selected_path}")

        log("=" * 60)
        log("🚀 Chatterbox MLX Final V9 - Fast Stable Model Selector")
        log(f"📂 Model yolu: {selected_path}")
        log("⏳ Model yükleniyor...")
        load_t0 = time.time()
        loaded_model = _submit_to_main_thread(_load_model_on_main_thread, selected_path)
        model = loaded_model
        active_model_path = selected_path
        msg = f"✅ Model yüklendi: {os.path.basename(selected_path)} ({time.time() - load_t0:.1f}s) | SR={loaded_model.sample_rate} Hz"
        log(msg)
        log("=" * 60)
        return model, active_model_path, msg


def load_selected_model_ui(model_path: str):
    try:
        _model, _path, msg = _ensure_model_loaded(model_path)
        return msg
    except Exception as e:
        return f"❌ Model yüklenemedi: {e}"


def refresh_model_list_ui(current_path: str | None):
    choices = _discover_model_paths()
    value = current_path if current_path in choices else (choices[0] if choices else MODEL_PATH)
    return gr.update(choices=choices, value=value), f"🔄 Model listesi yenilendi. Bulunan model sayısı: {len(choices)}"


# ============================================================
# MLX Audio Yardımcıları
# ============================================================
def _as_mlx_audio(audio):
    """Audio verisini mono 1D mx.array haline getirir."""
    if isinstance(audio, mx.array):
        a = audio
    else:
        a = mx.array(audio)

    if len(a.shape) > 1:
        a = mx.mean(a, axis=-1)

    a = a.reshape(-1).astype(mx.float32)
    mx.eval(a)
    return a


def _duration_seconds_mlx(audio, sample_rate: int) -> float:
    return float(audio.shape[0]) / float(sample_rate)


def _make_silence_mlx(sample_rate: int, seconds: float, dtype=mx.float32):
    n = max(0, int(sample_rate * seconds))
    return mx.zeros((n,), dtype=dtype)


def _peak_mlx(audio):
    if audio.shape[0] == 0:
        return 0.0
    p = mx.max(mx.abs(audio))
    mx.eval(p)
    return float(p)


def _safe_normalize_mlx(audio, target_peak: float = 0.94):
    """
    Eski davranış: sadece peak target üstündeyse kısar.
    Bunu chunk içinde kullanıyoruz; sessiz chunk'ı tek tek büyütüp nefes/gürültü şişirmesin.
    """
    audio = _as_mlx_audio(audio)
    peak = _peak_mlx(audio)
    if peak < 1e-8:
        return audio
    if peak > target_peak:
        audio = audio * (target_peak / peak)
        mx.eval(audio)
    return audio


def _peak_normalize_mlx(audio, target_peak: float = 0.95, max_gain: float = 2.8):
    """
    CUDA çıktısına yakın algılanan seviye için final WAV'a güvenli peak normalize.
    Önemli: Bunu her chunk'a değil, final concat sonrası uyguluyoruz.
    Böylece performans düşmez ve chunklar arası doğal seviye farkı bozulmaz.
    """
    audio = _as_mlx_audio(audio)
    peak = _peak_mlx(audio)
    if peak < 1e-8:
        return audio

    gain = target_peak / peak
    # Aşırı sessiz/bozuk üretimi 10x büyütüp kötüleştirmemek için limit.
    gain = min(float(gain), float(max_gain))
    if abs(gain - 1.0) > 0.01:
        audio = audio * gain
        mx.eval(audio)

    # Güvenlik: her ihtimale karşı target üstüne taşarsa kırpma değil, tekrar limit.
    peak_after = _peak_mlx(audio)
    if peak_after > target_peak:
        audio = audio * (target_peak / peak_after)
        mx.eval(audio)
    return audio


def _trim_edges_mlx(audio, sample_rate: int, threshold: float = 0.0045, pad_ms: int = 80):
    """
    Chunk başı/sonundaki aşırı sessizliği kırpar.
    Bu mod varsayılan olarak agresif kullanılmaz; dramatik durakları korumak önemlidir.
    """
    audio = _as_mlx_audio(audio)
    if audio.shape[0] == 0:
        return audio

    peak = _peak_mlx(audio)
    if peak < 1e-8:
        return audio

    gate = max(threshold, peak * 0.010)
    active_mask = mx.abs(audio) > gate
    mx.eval(active_mask)
    mask = active_mask.tolist()

    start_idx = None
    end_idx = None

    for idx, is_active in enumerate(mask):
        if is_active:
            start_idx = idx
            break

    if start_idx is None:
        return audio

    for idx in range(len(mask) - 1, -1, -1):
        if mask[idx]:
            end_idx = idx + 1
            break

    pad = int(sample_rate * pad_ms / 1000)
    start = max(0, start_idx - pad)
    end = min(audio.shape[0], end_idx + pad)
    return audio[start:end]


def _compress_long_silences_mlx(
    audio,
    sample_rate: int,
    threshold: float = 0.0038,
    frame_ms: int = 20,
    min_silence_ms: int = 1200,
    keep_ms: int = 420,
):
    """
    Aşırı uzun boşlukları hafifçe kısaltır.
    Varsayılan değerler uzun hikaye için bilinçli olarak yumuşaktır.
    """
    audio = _as_mlx_audio(audio)
    n = audio.shape[0]
    if n == 0:
        return audio

    peak = _peak_mlx(audio)
    if peak < 1e-8:
        return audio

    frame_len = max(1, int(sample_rate * frame_ms / 1000))
    min_silence_frames = max(1, int(min_silence_ms / frame_ms))
    keep_frames = max(1, int(keep_ms / frame_ms))

    pad_len = (-n) % frame_len
    if pad_len:
        padded = mx.concatenate([audio, mx.zeros((pad_len,), dtype=audio.dtype)], axis=0)
    else:
        padded = audio

    frames = padded.reshape((-1, frame_len))
    energy = mx.mean(mx.abs(frames), axis=1)
    gate = max(threshold, peak * 0.010)
    silent_frames = energy < gate
    mx.eval(silent_frames)
    mask = [bool(x) for x in silent_frames.tolist()]

    pieces = []
    start_sample = 0
    i = 0
    total_frames = len(mask)

    while i < total_frames:
        if not mask[i]:
            i += 1
            continue

        j = i
        while j < total_frames and mask[j]:
            j += 1

        silent_len = j - i
        if silent_len >= min_silence_frames:
            silent_start = min(i * frame_len, n)
            silent_end = min(j * frame_len, n)

            if silent_start > start_sample:
                pieces.append(audio[start_sample:silent_start])

            keep_samples = min(int(keep_frames * frame_len), silent_end - silent_start)
            pieces.append(mx.zeros((keep_samples,), dtype=audio.dtype))
            start_sample = silent_end

        i = j

    if start_sample < n:
        pieces.append(audio[start_sample:n])

    if not pieces:
        return audio

    out = mx.concatenate(pieces, axis=0)
    mx.eval(out)
    return out


def _max_silence_run_seconds_mlx(
    audio,
    sample_rate: int,
    threshold: float = 0.0038,
    frame_ms: int = 20,
) -> float:
    """
    Chunk içinde en uzun sessizlik süresini ölçer.
    Bu ağır bir analiz değildir; üretilmiş waveform üzerinde frame enerji kontrolüdür.
    """
    audio = _as_mlx_audio(audio)
    n = audio.shape[0]
    if n == 0:
        return 0.0

    peak = _peak_mlx(audio)
    if peak < 1e-8:
        return float(n) / float(sample_rate)

    frame_len = max(1, int(sample_rate * frame_ms / 1000))
    pad_len = (-n) % frame_len
    if pad_len:
        padded = mx.concatenate([audio, mx.zeros((pad_len,), dtype=audio.dtype)], axis=0)
    else:
        padded = audio

    frames = padded.reshape((-1, frame_len))
    energy = mx.mean(mx.abs(frames), axis=1)
    gate = max(threshold, peak * 0.010)
    silent_frames = energy < gate
    mx.eval(silent_frames)
    mask = [bool(x) for x in silent_frames.tolist()]

    best = 0
    cur = 0
    for is_silent in mask:
        if is_silent:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0

    return best * frame_ms / 1000.0


def _compress_abnormal_pauses_mlx(
    audio,
    sample_rate: int,
    min_silence_ms: int = 4000,
    keep_ms: int = 900,
):
    """
    Son çare güvenlik filtresi.
    0.3-1.5 saniyelik doğal dramatik durakları ellemez.
    Sadece 2.2 saniye üstü anormal/model kaynaklı boşlukları 650ms nefes kalacak şekilde kısaltır.
    """
    return _compress_long_silences_mlx(
        audio,
        sample_rate=sample_rate,
        min_silence_ms=min_silence_ms,
        keep_ms=keep_ms,
    )


# ============================================================
# Chatterbox Uyumlu Metin Hazırlama
# ============================================================
def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("—", " - ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _prepare_text_for_chatterbox(text: str) -> str:
    """
    ChatGPT metnini Chatterbox'a daha uygun hale getirir.
    Ama metni yapay SSML'e çevirmez; Chatterbox sade Türkçe metinde daha stabil.
    """
    text = _normalize_text(text)

    # Başlık tek satır kalsın; fazla boşluklar sadeleşsin.
    text = text.replace("…", "...")

    # Tırnaklardan sonra/önce nefes alanı oluştur.
    text = re.sub(r"([.!?])\s*([”\"])", r"\1\2", text)
    text = re.sub(r"([”\"])\s*([A-ZÇĞİÖŞÜÂÎÛ])", r"\1\n\2", text)

    # Dramatik üç nokta sonrası ayrı nefes alanı.
    text = re.sub(r"\.\.\.\s*", "...\n", text)

    # Çok kısa vurgu cümleleri ayrı satıra alınsın.
    emphasis_phrases = [
        "Kimse bilmiyordu",
        "Ve o gün",
        "Şimdi düşünün",
        "İlahi adalet",
        "Çünkü",
        "Ama",
        "Fakat",
    ]
    for phrase in emphasis_phrases:
        text = re.sub(rf"(?<!\n)({re.escape(phrase)})", r"\n\1", text)

    # Fazla satırları sadeleştir.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _punc_norm_mlx_cuda_story(text: str) -> str:
    """
    CUDA Chatterbox punc_norm mantığına yakın ama hikaye akışını bozmayan normalize.

    Amaç:
    - "..." gibi noktalamanın MLX'te kontrolsüz uzun boşluk üretmesini azaltmak.
    - Özel tırnak/satır/boşluk karmaşasını modele daha stabil vermek.
    - Bilinçli pause markerlarını korumak: [[pause:short]], [[pause:medium]], [[pause:long]].

    Bu fonksiyon ses kırpmaz; sadece model girişini temizler.
    """
    text = _normalize_text(text)
    if not text:
        return ""

    pause_placeholders = []

    def _store_pause(match):
        key = match.group(1).lower()
        placeholder = f"__PAUSE_{len(pause_placeholders)}__"
        pause_placeholders.append((placeholder, f"[[pause:{key}]]"))
        return f" {placeholder} "

    text = PAUSE_MARK_RE.sub(_store_pause, text)

    if text and text[0].islower():
        text = text[0].upper() + text[1:]

    replacements = [
        ("...", ", "),
        ("…", ", "),
        (":", ","),
        (" - ", ", "),
        (";", ", "),
        ("—", "-"),
        ("–", "-"),
        (" ,", ","),
        ("“", '"'),
        ("”", '"'),
        ("‘", "'"),
        ("’", "'"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)

    text = " ".join(text.split()).strip()
    # Tırnak/noktalama temizliği: " . veya . " gibi garip model sinyallerini engelle.
    text = re.sub(r'([.!?])\s+(["\'])', r'\1\2', text)
    text = re.sub(r'(["\'])\s+([.!?])', r'\1\2', text)

    for placeholder, marker_value in pause_placeholders:
        text = text.replace(placeholder, marker_value)

    ends_with_punct = text.endswith((".", "!", "?", "-", ",", "]"))
    ends_with_quoted_punct = len(text) >= 2 and text[-1] in ("\"", "'", "”") and text[-2] in (".", "!", "?")
    if text and not (ends_with_punct or ends_with_quoted_punct):
        text += "."

    return text


def _split_chunk_by_pause_markers(chunk_text: str):
    """
    Chunk içindeki bilinçli pause markerlarını kontrollü beklemeye çevirir.

    Dönüş: [(tts_text, pause_after_ms_or_None), ...]

    Normal metinde marker yoksa tek parça döner; performansı düşürmez.
    Marker varsa kullanıcı bilinçli gerçek bekleme istemiştir.
    """
    chunk_text = chunk_text.strip()
    if not chunk_text:
        return []

    parts = []
    pos = 0

    for match in PAUSE_MARK_RE.finditer(chunk_text):
        before = chunk_text[pos:match.start()].strip()
        pause_key = match.group(1).lower()
        pause_ms = PAUSE_MS.get(pause_key, 650)
        if before:
            parts.append((before, pause_ms))
        pos = match.end()

    tail = chunk_text[pos:].strip()
    if tail:
        parts.append((tail, None))

    return parts or [(chunk_text, None)]


def _is_dialogue_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("“") or s.startswith('"') or "” dedi" in s or '" dedi' in s


def _is_emphasis_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.endswith("...") or s.endswith("…"):
        return True
    if len(s) <= 85 and any(key in s for key in ["Kimse bilmiyordu", "Ve o gün", "Şimdi düşünün", "İlahi adalet"]):
        return True
    return False


def _split_long_sentence(sentence: str, chunk_size: int):
    sentence = sentence.strip()
    if len(sentence) <= chunk_size:
        return [sentence]

    pieces = []
    current = ""
    parts = re.split(r"([,;:])", sentence)
    merged_parts = []
    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if not part:
            i += 1
            continue
        if i + 1 < len(parts) and parts[i + 1] in [",", ";", ":"]:
            part = part + parts[i + 1]
            i += 2
        else:
            i += 1
        merged_parts.append(part)

    for part in merged_parts:
        candidate = f"{current} {part}".strip() if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                pieces.append(current.strip())
            if len(part) > chunk_size:
                words = part.split()
                cur = ""
                for w in words:
                    cand = f"{cur} {w}".strip() if cur else w
                    if len(cand) <= chunk_size:
                        cur = cand
                    else:
                        if cur:
                            pieces.append(cur)
                        cur = w
                current = cur
            else:
                current = part

    if current:
        pieces.append(current.strip())
    return pieces



def _sentence_split_keep_punct(line: str):
    """Noktalama kaybetmeden sade cümle bölme."""
    line = line.strip()
    if not line:
        return []
    parts = re.findall(r".+?(?:\.\.\.|[.!?]+[”\"]?|$)", line)
    return [p.strip() for p in parts if p and p.strip()]


def _is_dialogue_block_text(text: str) -> bool:
    s = text.strip()
    return bool(re.search(r"[“\"].+?[”\"]", s)) or s.startswith(("“", '"'))


def _pack_sentences_cuda_like(sentences, chunk_size: int, min_chunk: int = 135, allow_overflow: int = 55):
    """
    CUDA/Pinokio hissine yakın packing:
    - Çok kısa quote cümlelerini ayrı chunk yapmaz.
    - Chunk size'ı performans için baz alır ama dramatik/diyalog bloklarında az taşmaya izin verir.
    """
    out = []
    cur = ""
    soft_max = int(chunk_size)
    hard_max = int(chunk_size + allow_overflow)

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        candidate = f"{cur} {sent}".strip() if cur else sent

        if len(candidate) <= soft_max:
            cur = candidate
            continue

        # Eğer mevcut chunk çok kısa kalacaksa, hard_max'e kadar birleştir.
        if cur and len(cur) < min_chunk and len(candidate) <= hard_max:
            cur = candidate
            continue

        if cur:
            out.append(cur.strip())

        # Tek cümle çok uzunsa virgül/kelime bazında kır.
        if len(sent) > hard_max:
            out.extend(_split_long_sentence(sent, soft_max))
            cur = ""
        else:
            cur = sent

    if cur:
        out.append(cur.strip())

    return out


def _build_cuda_like_story_blocks(text: str):
    """
    Asıl düzeltme burada:
    Önceki splitter şu tarz satırları ayrı ayrı chunk yapıyordu:
        “Al bacım,” diye konuştu.
        “Senin payına da bu kuyu düştü.
    Bu, MLX'te prosody'yi koparıyor.
    Burada anlatım + konuşma satırlarını tek duygu bloğuna topluyoruz.
    """
    text = _prepare_text_for_chatterbox(text)
    lines = [ln.strip() for ln in re.split(r"\n+", text) if ln.strip()]

    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Hook: başlık iki satırsa birlikte kalsın.
        if (
            i + 1 < len(lines)
            and (line.endswith("...") or line.endswith("…"))
            and len(line) < 95
            and len(lines[i + 1]) < 110
        ):
            blocks.append((f"{line} {lines[i + 1]}").strip())
            i += 2
            continue

        # Sahne anlatımı + hemen ardından gelen diyaloglar aynı blokta kalsın.
        if i + 1 < len(lines) and _is_dialogue_line(lines[i + 1]):
            block_lines = [line]
            i += 1
            while i < len(lines) and _is_dialogue_line(lines[i]):
                block_lines.append(lines[i])
                i += 1
            blocks.append(" ".join(block_lines).strip())
            continue

        # Diyalog bloğu tek başına başladıysa ardışık diyalogları birleştir.
        if _is_dialogue_line(line):
            block_lines = []
            while i < len(lines) and _is_dialogue_line(lines[i]):
                block_lines.append(lines[i])
                i += 1
            blocks.append(" ".join(block_lines).strip())
            continue

        blocks.append(line)
        i += 1

    return blocks

def _split_text_story_mode(text: str, chunk_size: int):
    """
    CUDA benzeri doğal hikaye splitter.
    Amaç:
    - Hook tek duygu bloğu.
    - Konuşma satırları tek tek kopmasın.
    - Halil/Rıza gibi karakter sahnelerinde metne göre vurgu korunsun.
    - Performans düşmesin: regex + string packing, ağır audio analizi yok.
    """
    chunk_size = int(chunk_size)
    blocks = _build_cuda_like_story_blocks(text)

    chunks = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Model-first fix: CUDA benzeri noktalama normalize.
        # Gerçek bekleme gerekiyorsa [[pause:short|medium|long]] markerları korunur.
        block = _punc_norm_mlx_cuda_story(block)

        is_dialogue_block = _is_dialogue_block_text(block)

        # Diyalog/sahne bloklarında biraz daha uzun chunk'a izin veriyoruz.
        # Bu, kısa quote parçalarının prosody koparmasını engeller.
        if is_dialogue_block:
            # Diyaloglarda tek chunk'ı aşırı büyütme.
            # 220+ karakterlik tek diyalog blokları MLX'te uzun boşluk/runaway riskini artırıyor.
            # Bu ayar Halil sahnesini 2 doğal parçaya böler ama kısa replikleri tek tek koparmaz.
            soft_size = min(chunk_size, 220)
            allow_overflow = 15
            min_chunk = 115
        else:
            # Normal anlatımda da çok kısa parçaları azalt.
            soft_size = chunk_size
            allow_overflow = 65
            min_chunk = 140

        sentences = _sentence_split_keep_punct(block)

        # Cümle regex'i boş dönerse bloğu direkt kullan.
        if not sentences:
            sentences = [block]

        packed = _pack_sentences_cuda_like(
            sentences,
            chunk_size=soft_size,
            min_chunk=min_chunk,
            allow_overflow=allow_overflow,
        )

        chunks.extend(packed)

    # Son geçiş: çok kısa sıradan parçaları komşusuyla birleştir.
    merged = []
    for ch in chunks:
        if (
            merged
            and len(ch) < 70
            and not _is_dialogue_block_text(ch)
            and not _is_dialogue_block_text(merged[-1])
            and len(merged[-1]) + 1 + len(ch) <= chunk_size + 45
        ):
            merged[-1] = f"{merged[-1]} {ch}".strip()
        else:
            merged.append(ch)

    return merged

def _split_text_pinokio_mode(text: str, chunk_size: int):
    """Pinokio ChatterBox-Multilingual app.py davranışına yakın sade splitter."""
    text = _normalize_text(text)
    chunk_size = int(chunk_size)

    if len(text) <= chunk_size:
        return [text]

    sentences = re.split(r"[.!?]+", text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_chunk) + len(sentence) + 2 > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if len(sentence) > chunk_size:
                    parts = re.split(r"[,;]+", sentence)
                    for part in parts:
                        part = part.strip()
                        if not part:
                            continue
                        if len(current_chunk) + len(part) + 2 > chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = part
                        else:
                            current_chunk += (", " if current_chunk else "") + part
                else:
                    current_chunk = sentence
        else:
            current_chunk += (". " if current_chunk else "") + sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def _split_text_for_tts(text: str, chunk_size: int, mode: str):
    if mode == "Pinokio Uyumlu":
        return _split_text_pinokio_mode(text, chunk_size)
    return _split_text_story_mode(text, chunk_size)


def _estimate_chunk_duration_limit(chunk_text: str) -> float:
    """
    Chunk için gerçekçi üst süre limiti.
    Amaç sesi kırpmak değil; anormal uzun üretimi retry'a düşürmek.
    """
    clean_text = PAUSE_MARK_RE.sub("", chunk_text)
    chars = max(1, len(clean_text))

    # Eski limit 226 karakter için yaklaşık 29.8s idi; bozuk 25s+ üretimleri yakalamıyordu.
    # Yeni limit 226 karakter için yaklaşık 23.8s verir.
    return max(6.5, chars / 12.0 + 5.0)


def _dynamic_token_cap(chunk_text: str, user_max_tokens: int) -> int | None:
    """
    Hız odaklı speech-token sınırı.
    Amaç: MLX'in uzun sessizlik/runaway üretmesini baştan azaltmak.
    0 bırakılırsa otomatik hızlı cap kullanılır.
    """
    user_max_tokens = int(user_max_tokens)
    clean_len = len(PAUSE_MARK_RE.sub("", chunk_text))

    # V7 fast cap: gereksiz uzun token üretimini azaltır.
    # Örnek: 100 char≈265 token, 160 char≈358 token, 220 char≈451 token.
    auto_cap = int(max(170, min(650, clean_len * 1.55 + 110)))

    if user_max_tokens <= 0:
        return auto_cap

    return int(max(150, min(user_max_tokens, auto_cap)))


# ============================================================
# Model Inference
# ============================================================
def _generate_on_main_thread(model, gen_kwargs):
    results = model.generate(**gen_kwargs)
    result = next(results)
    audio = _as_mlx_audio(result.audio)
    return audio, result


def _generate_chunk_with_retry(
    model,
    chunk_text: str,
    ref_audio,
    audio_prompt_sr,
    exaggeration: float,
    cfg_weight: float,
    temperature: float,
    max_tokens: int,
    sample_rate: int,
    chunk_index: int,
    safety_retry: bool,
    light_cleanup: bool,
    lang_code: str,
):
    best_audio = None
    best_result = None
    best_duration = 10**9
    best_gen_time = 0.0
    max_duration = _estimate_chunk_duration_limit(chunk_text)
    attempts = 1  # V7 Fast Stable: retry kapalı; performansı öldüren tekrar üretim yok

    for attempt in range(attempts):
        attempt_temp = max(0.25, float(temperature) - 0.08 * attempt)
        attempt_cfg = max(0.25, float(cfg_weight) - 0.06 * attempt)

        gen_kwargs = dict(
            text=chunk_text,
            audio_prompt=ref_audio,
            audio_prompt_sr=audio_prompt_sr,
            exaggeration=float(exaggeration),
            cfg_weight=attempt_cfg,
            temperature=attempt_temp,
            lang_code=lang_code,
        )

        base_token_cap = _dynamic_token_cap(chunk_text, max_tokens)
        token_cap = None
        if base_token_cap is not None:
            # Retry sırasında sadece cfg/temp değil, token cap de kontrollü düşer.
            # Böylece aynı uzun/sessiz üretimi tekrar tekrar alma riski azalır.
            token_cap = max(180, int(base_token_cap * (0.82 ** attempt)))
            gen_kwargs["max_new_tokens"] = token_cap

        if attempt > 0:
            retry_seed = int(time.time() * 1000 + chunk_index * 131 + attempt * 997) % (2**31)
            mx.random.seed(retry_seed)
            log(f"     ↻ Tekrar deneme {attempt + 1}/{attempts} | seed={retry_seed} cfg={attempt_cfg:.2f} temp={attempt_temp:.2f} tokens={token_cap}")

        t0 = time.time()
        audio, result = _submit_to_main_thread(_generate_on_main_thread, model, gen_kwargs)
        gen_time = time.time() - t0

        audio = _safe_normalize_mlx(audio)

        max_silence = _max_silence_run_seconds_mlx(audio, sample_rate)
        duration = _duration_seconds_mlx(audio, sample_rate)
        abnormal_pause = max_silence >= 4.0
        too_long = duration > max_duration

        if light_cleanup:
            audio = _trim_edges_mlx(audio, sample_rate)
            audio = _compress_long_silences_mlx(audio, sample_rate)
            audio = _safe_normalize_mlx(audio)
            max_silence = _max_silence_run_seconds_mlx(audio, sample_rate)
            duration = _duration_seconds_mlx(audio, sample_rate)
            abnormal_pause = max_silence >= 4.0
            too_long = duration > max_duration

        # En iyi aday: en kısa değil, önce "anormal boşluğu olmayan" aday.
        # Tüm adaylar bozuksa en kısa olan tutulur ve en sonda güvenlik filtresi uygulanır.
        current_score = (1 if abnormal_pause else 0, 1 if too_long else 0, duration)
        best_score = getattr(_generate_chunk_with_retry, "_best_score", None)
        if attempt == 0:
            best_score = None
        if best_audio is None or best_score is None or current_score < best_score:
            best_audio = audio
            best_result = result
            best_duration = duration
            best_gen_time = gen_time
            _generate_chunk_with_retry._best_score = current_score

        if not safety_retry or (not abnormal_pause and not too_long):
            break

        reasons = []
        if too_long:
            reasons.append(f"süre {duration:.1f}s > {max_duration:.1f}s")
        if abnormal_pause:
            reasons.append(f"iç boşluk {max_silence:.1f}s")
        log(f"     ⚠️ Anormal chunk: {', '.join(reasons)}. Yeniden denenecek.")

    final_max_silence = _max_silence_run_seconds_mlx(best_audio, sample_rate)
    if final_max_silence >= 4.0:
        before = _duration_seconds_mlx(best_audio, sample_rate)
        best_audio = _compress_abnormal_pauses_mlx(
            best_audio,
            sample_rate=sample_rate,
            min_silence_ms=4000,
            keep_ms=900,
        )
        best_audio = _safe_normalize_mlx(best_audio)
        after = _duration_seconds_mlx(best_audio, sample_rate)
        saved = before - after
        if saved > 0.25:
            log(f"     ✂️ Anormal iç boşluk düzeltildi: -{saved:.1f}s | en uzun boşluk={final_max_silence:.1f}s")

    return best_audio, best_result, _duration_seconds_mlx(best_audio, sample_rate), best_gen_time


# ============================================================
# Başlangıç
# ============================================================
log("=" * 60)
log("🚀 Chatterbox MLX Final V9 - Fast Stable Model Selector")
log("=" * 60)
log("📌 Model lazy-load modunda. Generate veya 'Modeli Yükle' ile seçili model yüklenecek.")
log(f"📂 Varsayılan model yolu: {MODEL_PATH}")
log("=" * 60)


# ============================================================
# Önizleme / Analiz
# ============================================================
def chunk_preview(metin, chunk_size, mode):
    if not metin or not metin.strip():
        return "⚠️ Metin yok."
    chunks = _split_text_for_tts(metin, int(chunk_size), mode)
    lengths = [len(c) for c in chunks]
    total_chars = sum(lengths)
    preview_lines = []
    preview_lines.append(f"✅ Chunk analizi")
    preview_lines.append(f"Mod: {mode}")
    preview_lines.append(f"Toplam karakter: {len(_normalize_text(metin))}")
    preview_lines.append(f"Chunk sayısı: {len(chunks)}")
    preview_lines.append(f"Ortalama chunk: {int(total_chars / max(1, len(chunks)))} karakter")
    preview_lines.append(f"En kısa / en uzun: {min(lengths)} / {max(lengths)} karakter")
    preview_lines.append("")
    preview_lines.append("İlk 12 chunk:")
    for idx, ch in enumerate(chunks[:12], start=1):
        preview_lines.append(f"{idx:02d}. [{len(ch)}] {ch[:150]}{'...' if len(ch) > 150 else ''}")
    if len(chunks) > 12:
        preview_lines.append(f"... +{len(chunks) - 12} chunk daha")
    return "\n".join(preview_lines)


def hazirla_metin(metin):
    if not metin or not metin.strip():
        return ""
    return _prepare_text_for_chatterbox(metin)


def hazirla_ve_onizle(metin, chunk_size, mode):
    """
    Tek buton: metni Chatterbox'a hazırlar ve aynı anda chunk önizleme üretir.
    Metnin duygu/vurgusunu yazıda korur; model girişinde punc_norm ayrıca uygulanır.
    """
    if not metin or not metin.strip():
        return "", "⚠️ Metin yok."

    prepared = _prepare_text_for_chatterbox(metin)
    preview = chunk_preview(prepared, int(chunk_size), mode)
    return prepared, preview


def add_pause_marker(metin, marker):
    """Metin kutusunun sonuna kontrollü pause marker ekler."""
    base = (metin or "").rstrip()
    if base:
        return f"{base} {marker} "
    return f"{marker} "


def create_youtube_master_wav():
    """
    Opsiyonel indirme: model çıktısını yeniden üretmez.
    Sadece mevcut WAV'ı güvenli peak normalize eder ve PCM_16 olarak yazar.
    Gerçek model kalitesini artırmaz; YouTube'a hazır, tutarlı seviye verir.
    """
    if not os.path.exists(OUTPUT_PATH):
        return None, "⚠️ Önce ses üretmelisin. Orijinal WAV bulunamadı."

    audio, sr = sf.read(OUTPUT_PATH, dtype="float32", always_2d=False)
    audio = np.asarray(audio, dtype=np.float32)

    if audio.size == 0:
        return None, "⚠️ Ses dosyası boş görünüyor."

    # DC offset temizliği: çok hafif, ses karakterini değiştirmez.
    if audio.ndim == 1:
        audio = audio - np.mean(audio)
    else:
        audio = audio - np.mean(audio, axis=0, keepdims=True)

    peak = float(np.max(np.abs(audio)))
    if peak > 1e-8:
        audio = audio * (0.95 / peak)

    audio = np.clip(audio, -0.999, 0.999).astype(np.float32)
    sf.write(YOUTUBE_MASTER_PATH, audio, int(sr), subtype="PCM_16")
    return YOUTUBE_MASTER_PATH, (
        "✅ YouTube Master WAV hazır.\n"
        "Bu işlem yeniden TTS üretmez; sadece mevcut WAV seviyesini güvenli normalize eder.\n"
        f"Dosya: {YOUTUBE_MASTER_PATH}"
    )


# ============================================================
# Ana Ses Üretme Fonksiyonu
# ============================================================
def ses_uret(
    metin,
    referans_ses_yolu,
    lang_code,
    selected_model_path,
    exaggeration,
    cfg_pace,
    chunk_size,
    temperature,
    random_seed,
    max_new_tokens,
    chunk_gap_ms,
    processing_mode,
    safety_retry,
    save_chunks,
):
    try:
        if not selected_model_path or not os.path.exists(selected_model_path):
            return None, _t("model_not_selected_error")
        if not metin or not metin.strip():
            return None, "⚠️ Lütfen sentezlenecek bir metin girin."

        active_model, active_model_path, model_msg = _ensure_model_loaded(selected_model_path)

        mode = processing_mode
        light_cleanup = mode == "Güvenli Uzun Metin"
        splitter_mode = "Long Story" if mode != "Pinokio Uyumlu" else "Pinokio Uyumlu"

        # Long Story modunda metni Chatterbox'a uygun hafif hazırla.
        if splitter_mode == "Long Story":
            metin = _prepare_text_for_chatterbox(metin)
        else:
            metin = _normalize_text(metin)

        log("─" * 60)
        log("📝 YENİ SES ÜRETİM İSTEĞİ")
        log(f"   Mod: {mode}")
        log(f"   Metin: '{metin[:90]}{'...' if len(metin) > 90 else ''}'")
        log(f"   Metin uzunluğu: {len(metin)} karakter")
        log(f"   🤖 Model: {os.path.basename(active_model_path)}")
        log(f"   📂 Model yolu: {active_model_path}")
        log(f"   Referans ses: {'✅ ' + os.path.basename(referans_ses_yolu) if referans_ses_yolu else '❌ Yok'}")
        log(f"   🌐 Dil kodu: {lang_code}")
        log(f"   🎭 Exaggeration: {exaggeration}")
        log(f"   ⚡ CFG/Pace: {cfg_pace}")
        log(f"   📄 Chunk size: {chunk_size}")
        log(f"   🌡️ Temperature: {temperature}")
        log(f"   🎲 Random seed: {random_seed}")
        log(f"   🧱 Max new tokens: {max_new_tokens} (0 = otomatik güvenli cap)")
        log(f"   ⏸️ Chunk gap: {chunk_gap_ms}ms")
        log(f"   🛡️ Safety retry: {safety_retry} (V7 fast: retry forced off)")
        log(f"   ✂️ Light cleanup: {light_cleanup}")

        if int(random_seed) > 0:
            seed = int(random_seed)
        else:
            seed = int(time.time() * 1000) % (2**31)
        mx.random.seed(seed)
        log(f"   🎲 Aktif seed: {seed}")

        ref_audio = None
        audio_prompt_sr = None
        if referans_ses_yolu:
            log("   🎵 Referans ses yükleniyor...")
            loaded_ref = load_audio(referans_ses_yolu, sample_rate=active_model.sample_rate)
            ref_audio = _as_mlx_audio(loaded_ref)
            audio_prompt_sr = active_model.sample_rate
            log(f"   🎵 Referans ses yüklendi: {_duration_seconds_mlx(ref_audio, active_model.sample_rate):.1f}s")

        chunks = _split_text_for_tts(metin, int(chunk_size), splitter_mode)
        if not chunks:
            return None, "⚠️ Metin parçalanamadı."

        # Bilinçli gerçek beklemeler: [[pause:short]], [[pause:medium]], [[pause:long]]
        # Marker yoksa parça sayısı değişmez; performans düşmez.
        chunks_with_pause = []
        for ch in chunks:
            chunks_with_pause.extend(_split_chunk_by_pause_markers(ch))
        chunks_with_pause = [(txt, pause_ms) for txt, pause_ms in chunks_with_pause if txt.strip()]
        chunks = [txt for txt, _pause_ms in chunks_with_pause]

        if save_chunks:
            os.makedirs(CHUNKS_DIR, exist_ok=True)
            with open(os.path.join(CHUNKS_DIR, "chunks.txt"), "w", encoding="utf-8") as f:
                for idx, ch in enumerate(chunks, start=1):
                    pause_info = ""
                    if "chunks_with_pause" in locals() and idx - 1 < len(chunks_with_pause):
                        pause_ms = chunks_with_pause[idx - 1][1]
                        pause_info = f" | pause_after={pause_ms}ms" if pause_ms is not None else ""
                    f.write(f"--- CHUNK {idx:04d} | {len(ch)} chars{pause_info} ---\n{ch}\n\n")

        log(f"   📄 Parça sayısı: {len(chunks)}")

        all_audio = []
        total_gen_time = 0.0
        problem_chunks = []

        for i, chunk_text in enumerate(chunks):
            log(f"   ▶ Parça {i + 1}/{len(chunks)} | {len(chunk_text)} karakter: '{chunk_text[:65]}{'...' if len(chunk_text) > 65 else ''}'")

            audio, result, duration, gen_time = _generate_chunk_with_retry(
                model=active_model,
                chunk_text=chunk_text,
                ref_audio=ref_audio,
                audio_prompt_sr=audio_prompt_sr,
                exaggeration=float(exaggeration),
                cfg_weight=float(cfg_pace),
                temperature=float(temperature),
                max_tokens=int(max_new_tokens),
                sample_rate=active_model.sample_rate,
                chunk_index=i,
                safety_retry=bool(safety_retry),
                light_cleanup=light_cleanup,
                lang_code=str(lang_code),
            )

            max_expected = _estimate_chunk_duration_limit(chunk_text)
            if duration > max_expected:
                problem_chunks.append((i + 1, len(chunk_text), round(duration, 1), round(max_expected, 1)))

            total_gen_time += gen_time
            log(
                f"     ✅ Parça {i + 1} tamamlandı: {gen_time:.2f}s | "
                f"RTF: {getattr(result, 'real_time_factor', 'n/a')}x | Süre: {duration:.1f}s"
            )

            all_audio.append(audio)

            if save_chunks:
                chunk_path = os.path.join(CHUNKS_DIR, f"chunk_{i + 1:04d}.wav")
                sf.write(chunk_path, np.asarray(audio, dtype=np.float32), active_model.sample_rate)

        if len(all_audio) > 1:
            pieces = []
            base_gap_ms = max(0, int(chunk_gap_ms))
            for idx, a in enumerate(all_audio):
                pieces.append(a)
                if idx == len(all_audio) - 1:
                    continue

                intentional_pause_ms = None
                if "chunks_with_pause" in locals() and idx < len(chunks_with_pause):
                    intentional_pause_ms = chunks_with_pause[idx][1]

                gap_ms = intentional_pause_ms if intentional_pause_ms is not None else base_gap_ms
                if gap_ms > 0:
                    pieces.append(_make_silence_mlx(active_model.sample_rate, gap_ms / 1000.0, dtype=all_audio[0].dtype))

            final_audio_mx = mx.concatenate(pieces, axis=0)
            mx.eval(final_audio_mx)
            log(f"   🔗 {len(all_audio)} parça MLX ile birleştirildi")
        else:
            final_audio_mx = all_audio[0]

        # CUDA çıktısındaki dolgunluk/algılanan kaliteye yaklaşmak için final seviyeyi yükselt.
        # Chunk içinde boost yapmıyoruz; sadece final WAV'da güvenli peak normalize.
        final_audio_mx = _peak_normalize_mlx(final_audio_mx, target_peak=0.95, max_gain=2.8)
        total_duration = _duration_seconds_mlx(final_audio_mx, active_model.sample_rate)

        final_audio_np = np.asarray(final_audio_mx, dtype=np.float32)
        sf.write(OUTPUT_PATH, final_audio_np, active_model.sample_rate)

        rtf = total_gen_time / max(total_duration, 1e-6)
        log(f"   💾 Kaydedildi: {OUTPUT_PATH}")
        log(f"   📊 Toplam süre: {total_duration:.1f}s ses / {total_gen_time:.2f}s üretim | RTF={rtf:.2f}x")
        log("─" * 60)

        problem_text = ""
        if problem_chunks:
            problem_text = "\n⚠️ Olası sorunlu chunklar:\n" + "\n".join(
                f"- Chunk {idx}: {chars} karakter, {dur}s üretildi, beklenen üst limit {limit}s"
                for idx, chars, dur, limit in problem_chunks
            )

        info_lines = [
            "✅ Sentezleme Tamamlandı!",
            f"Mod: {mode}",
            f"Dil: {lang_code}",
            f"⏱️ Üretim süresi: {total_gen_time:.2f}s",
            f"🔊 Ses süresi: {total_duration:.1f}s",
            f"🚀 RTF: {rtf:.2f}x",
            f"📄 Parça sayısı: {len(chunks)}",
            f"💾 Dosya: {OUTPUT_PATH}",
            "🧠 MLX: inference + normalize + concat",
            "🌉 NumPy: sadece final WAV/chunk WAV yazma köprüsü",
            "🎚️ Opsiyonel: YouTube Master WAV butonu mevcut WAV için güvenli seviye dosyası hazırlar",
        ]
        info = chr(10).join(info_lines) + problem_text
        return OUTPUT_PATH, info

    except Exception as e:
        import traceback
        log(f"   ❌ HATA: {e}")
        traceback.print_exc()
        return None, f"❌ Hata oluştu: {str(e)}"


# ============================================================
# Preset Sistemi — Referans Ses + Ayar Kaydet / Yükle
# ============================================================
def _safe_filename(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"[^A-Za-z0-9ÇĞİÖŞÜçğıöşü_-]+", "_", name)
    return name.strip("_") or "preset"


def _load_presets() -> dict:
    if not os.path.exists(PRESETS_FILE):
        return {}
    try:
        with open(PRESETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        log(f"⚠️ Preset okunamadı: {e}")
        return {}


def _save_presets(presets: dict) -> None:
    with open(PRESETS_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)


def _preset_choices():
    return sorted(_load_presets().keys())


def _copy_reference_audio_for_preset(preset_name: str, ref_path: str | None) -> str:
    if not ref_path or not os.path.exists(ref_path):
        return ""

    os.makedirs(PRESETS_AUDIO_DIR, exist_ok=True)
    ext = os.path.splitext(ref_path)[1] or ".wav"
    safe_name = _safe_filename(preset_name)
    dest = os.path.join(PRESETS_AUDIO_DIR, f"{safe_name}_reference{ext}")
    shutil.copy2(ref_path, dest)
    return dest


def save_current_preset(
    preset_name,
    referans_ses_yolu,
    lang_choice,
    exaggeration,
    cfg_pace,
    chunk_size,
    temperature,
    random_seed,
    max_new_tokens,
    chunk_gap_ms,
    processing_mode,
    safety_retry,
    save_chunks,
):
    preset_name = (preset_name or "").strip()
    if not preset_name:
        return gr.update(choices=_preset_choices()), "⚠️ Preset adı gir."

    presets = _load_presets()
    saved_ref = _copy_reference_audio_for_preset(preset_name, referans_ses_yolu)

    # Eğer yeni referans yüklenmediyse ve aynı isimde eski preset varsa eski referansı koru.
    if not saved_ref and preset_name in presets:
        saved_ref = presets[preset_name].get("reference_audio", "")

    presets[preset_name] = {
        "reference_audio": saved_ref,
        "lang_choice": str(lang_choice),
        "exaggeration": float(exaggeration),
        "cfg_pace": float(cfg_pace),
        "chunk_size": int(chunk_size),
        "temperature": float(temperature),
        "random_seed": int(random_seed),
        "max_new_tokens": int(max_new_tokens),
        "chunk_gap_ms": int(chunk_gap_ms),
        "processing_mode": str(processing_mode),
        "safety_retry": bool(safety_retry),
        "save_chunks": bool(save_chunks),
        "updated_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    _save_presets(presets)

    return (
        gr.update(choices=_preset_choices(), value=preset_name),
        "✅ Preset kaydedildi: " + str(preset_name) + chr(10) + "🎵 Referans ses: " + str(saved_ref or "yok"),
    )


def load_selected_preset(preset_name):
    presets = _load_presets()
    if not preset_name or preset_name not in presets:
        defaults = (
            f"{DEFAULT_LANG_CODE} — {SUPPORTED_LANGUAGES[DEFAULT_LANG_CODE]}",
            None,
            0.45,
            0.30,
            200,
            0.40,
            0,
            0,
            40,
            "Doğal Hikaye",
            False,
            False,
            "⚠️ Preset bulunamadı.",
        )
        return defaults

    p = presets[preset_name]
    ref = p.get("reference_audio", "")
    if ref and not os.path.exists(ref):
        ref = None

    return (
        p.get("lang_choice", f"{DEFAULT_LANG_CODE} — {SUPPORTED_LANGUAGES[DEFAULT_LANG_CODE]}"),
        ref,
        float(p.get("exaggeration", 0.45)),
        float(p.get("cfg_pace", 0.30)),
        int(p.get("chunk_size", 220)),
        float(p.get("temperature", 0.45)),
        int(p.get("random_seed", 0)),
        int(p.get("max_new_tokens", 0)),
        int(p.get("chunk_gap_ms", 50)),
        p.get("processing_mode", "Doğal Hikaye"),
        bool(p.get("safety_retry", False)),
        bool(p.get("save_chunks", False)),
        "✅ Preset yüklendi: " + str(preset_name) + chr(10) + "🎵 Referans ses: " + str(ref or "yok"),
    )


def delete_selected_preset(preset_name):
    presets = _load_presets()
    if not preset_name or preset_name not in presets:
        return gr.update(choices=_preset_choices(), value=None), "⚠️ Silinecek preset bulunamadı."

    ref = presets[preset_name].get("reference_audio", "")
    if ref and os.path.exists(ref):
        try:
            os.remove(ref)
        except Exception as e:
            log(f"⚠️ Referans ses silinemedi: {e}")

    del presets[preset_name]
    _save_presets(presets)
    return gr.update(choices=_preset_choices(), value=None), f"🗑️ Preset silindi: {preset_name}"


# ============================================================
# Gradio Arayüz
# ============================================================
custom_css = """
body { background-color: #0d0d0d !important; }
.gradio-container {
    background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%) !important;
    color: #e0e0e0 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    max-width: 1040px !important;
    margin: 0 auto !important;
}
h1 {
    background: linear-gradient(135deg, #ff4444 0%, #ff8800 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    text-align: center;
    font-size: 1.6rem !important;
}
h3 { color: #ff6633 !important; font-size: 0.95rem !important; }
button.primary {
    background: linear-gradient(135deg, #cc2200 0%, #ff4400 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 12px 0 !important;
    box-shadow: 0 4px 20px rgba(255, 68, 0, 0.35) !important;
    transition: all 0.2s ease !important;
}
button.primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 25px rgba(255, 68, 0, 0.5) !important;
}
"""

with gr.Blocks(title="Chatterbox MLX") as demo:
    gr.Markdown(f"# {_t('title')}")
    gr.Markdown(_t('description'))

    model_choices = _discover_model_paths()
    default_model_value = MODEL_PATH if MODEL_PATH in model_choices else (model_choices[0] if model_choices else None)

    with gr.Accordion(_t("model_selection"), open=False):
        gr.Markdown(_t("model_selection_desc"))
        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=model_choices,
                value=default_model_value,
                label=_t("model_dropdown_label"),
                info=_t("model_dropdown_info"),
            )
        with gr.Row():
            load_model_btn = gr.Button(_t("load_model_btn"))
            refresh_models_btn = gr.Button(_t("refresh_models_btn"))
        model_status = gr.Textbox(
            label=_t("model_status_label"),
            value=f"📌: {default_model_value}" if default_model_value else "⚠️ Yok",
            interactive=False,
            lines=2,
        )

    with gr.Accordion(_t("download_models_acc"), open=False):
        gr.Markdown(_t("download_models_desc"))
        with gr.Row():
            download_6bit_btn = gr.Button(_t("download_6bit_btn"))
            download_8bit_btn = gr.Button(_t("download_8bit_btn"))
        download_status = gr.Textbox(label=_t("download_status"), interactive=False)

    with gr.Accordion(_t("ui_lang_acc"), open=False):
        with gr.Row():
            ui_lang_dropdown = gr.Dropdown(choices=["tr", "en"], value=UI_LANG, label=_t("ui_lang_label"))
            ui_lang_save_btn = gr.Button(_t("ui_lang_btn"))
        ui_lang_status = gr.Textbox(label=_t("ui_lang_status"), interactive=False)

    with gr.Accordion(_t("best_practice_acc"), open=False):
        gr.Markdown(
            "**Önerilen / Recommended:** `Exaggeration 0.45` · `CFG/Pace 0.30` · `Temperature 0.40` · `Chunk size 200` \n\n"
            "**Pause markers:** `[[pause:short]]` (300ms) / `[[pause:medium]]` (650ms) / `[[pause:long]]` (1000ms)"
        )

    gr.Markdown(_t("preset_acc"))
    with gr.Row():
        preset_dropdown = gr.Dropdown(
            choices=_preset_choices(),
            value=None,
            label=_t("preset_dropdown"),
        )
        preset_name_input = gr.Textbox(
            label=_t("preset_name_input"),
            placeholder="Preset Name",
        )

    with gr.Row():
        save_preset_btn = gr.Button(_t("save_preset_btn"))
        load_preset_btn = gr.Button(_t("load_preset_btn"))
        delete_preset_btn = gr.Button(_t("delete_preset_btn"))

    preset_status = gr.Textbox(
        label=_t("preset_status"),
        interactive=False,
        lines=2,
    )

    with gr.Row():
        with gr.Column(scale=3):
            metin_girdisi = gr.Textbox(
                label=_t("text_input_label"),
                lines=14,
            )

            with gr.Row():
                hazirla_btn = gr.Button(_t("hazirla_btn"))

            with gr.Row():
                pause_short_btn = gr.Button("+ [[pause:short]]")
                pause_medium_btn = gr.Button("+ [[pause:medium]]")
                pause_long_btn = gr.Button("+ [[pause:long]]")

            referans_ses = gr.Audio(
                label=_t("ref_audio_label"),
                type="filepath",
            )

        with gr.Column(scale=2):
            ses_ciktisi = gr.Audio(label=_t("output_audio_label"))
            istatistikler = gr.Textbox(
                label=_t("stats_label"),
                interactive=False,
                lines=16,
            )
            master_btn = gr.Button(_t("master_btn"))
            master_ciktisi = gr.Audio(label=_t("master_out_label"))

    gr.Markdown(_t("audio_settings_label"))
    with gr.Row():
        lang_dropdown = gr.Dropdown(
            choices=[f"{code} — {name}" for code, name in SUPPORTED_LANGUAGES.items()],
            value=f"{DEFAULT_LANG_CODE} — {SUPPORTED_LANGUAGES[DEFAULT_LANG_CODE]}",
            label=_t("lang_dropdown_label"),
        )
        exaggeration_slider = gr.Slider(
            minimum=0.25, maximum=1.2, value=0.45, step=0.05, label=_t("exag_label"),
        )
        cfg_slider = gr.Slider(
            minimum=0.20, maximum=0.80, value=0.30, step=0.02, label=_t("cfg_label"),
        )
        temperature_slider = gr.Slider(
            minimum=0.20, maximum=1.20, value=0.40, step=0.05, label=_t("temp_label"),
        )

    gr.Markdown(_t("story_settings_label"))
    with gr.Row():
        mode_dropdown = gr.Dropdown(
            choices=["Doğal Hikaye", "Güvenli Uzun Metin", "Pinokio Uyumlu"],
            value="Doğal Hikaye",
            label=_t("mode_label"),
        )
        chunk_size_slider = gr.Slider(
            minimum=180, maximum=420, value=200, step=10, label=_t("chunk_size_label"),
        )
        max_tokens_slider = gr.Slider(
            minimum=0, maximum=2000, value=0, step=50, label=_t("max_tokens_label"),
        )
        chunk_gap_slider = gr.Slider(
            minimum=0, maximum=500, value=40, step=10, label=_t("chunk_gap_label"),
        )

    with gr.Row():
        seed_input = gr.Number(
            value=0, label=_t("seed_label"), precision=0,
        )
        safety_retry_checkbox = gr.Checkbox(
            value=False, label=_t("retry_label"),
        )
        save_chunks_checkbox = gr.Checkbox(
            value=False, label=_t("save_chunks_label"),
        )

    uret_butonu = gr.Button(_t("generate_btn"), variant="primary")

    load_model_btn.click(fn=load_selected_model_ui, inputs=[model_dropdown], outputs=[model_status])
    refresh_models_btn.click(fn=refresh_model_list_ui, inputs=[model_dropdown], outputs=[model_dropdown, model_status])

    def dl_6bit():
        yield _t("model_downloading")
        yield download_model_hf("mlx-community/chatterbox-6bit", "chatterbox-6bit")

    def dl_8bit():
        yield _t("model_downloading")
        yield download_model_hf("mlx-community/chatterbox-8bit", "chatterbox-8bit")

    download_6bit_btn.click(fn=dl_6bit, inputs=[], outputs=[download_status])
    download_8bit_btn.click(fn=dl_8bit, inputs=[], outputs=[download_status])

    ui_lang_save_btn.click(fn=save_app_config, inputs=[ui_lang_dropdown], outputs=[ui_lang_status])

    save_preset_btn.click(
        fn=save_current_preset,
        inputs=[
            preset_name_input, referans_ses, lang_dropdown, exaggeration_slider, cfg_slider,
            chunk_size_slider, temperature_slider, seed_input, max_tokens_slider, chunk_gap_slider,
            mode_dropdown, safety_retry_checkbox, save_chunks_checkbox,
        ],
        outputs=[preset_dropdown, preset_status],
    )

    load_preset_btn.click(
        fn=load_selected_preset,
        inputs=[preset_dropdown],
        outputs=[
            lang_dropdown, referans_ses, exaggeration_slider, cfg_slider, chunk_size_slider,
            temperature_slider, seed_input, max_tokens_slider, chunk_gap_slider, mode_dropdown,
            safety_retry_checkbox, save_chunks_checkbox, preset_status,
        ],
    )

    delete_preset_btn.click(fn=delete_selected_preset, inputs=[preset_dropdown], outputs=[preset_dropdown, preset_status])

    hazirla_btn.click(fn=hazirla_ve_onizle, inputs=[metin_girdisi, chunk_size_slider, mode_dropdown], outputs=[metin_girdisi, istatistikler])

    pause_short_btn.click(fn=lambda metin: add_pause_marker(metin, "[[pause:short]]"), inputs=[metin_girdisi], outputs=[metin_girdisi])
    pause_medium_btn.click(fn=lambda metin: add_pause_marker(metin, "[[pause:medium]]"), inputs=[metin_girdisi], outputs=[metin_girdisi])
    pause_long_btn.click(fn=lambda metin: add_pause_marker(metin, "[[pause:long]]"), inputs=[metin_girdisi], outputs=[metin_girdisi])

    master_btn.click(fn=create_youtube_master_wav, inputs=[], outputs=[master_ciktisi, istatistikler])

    uret_butonu.click(
        fn=lambda metin, ref, lang_choice, selected_model_path, *args: ses_uret(
            metin, ref, str(lang_choice).split(" — ")[0], selected_model_path, *args,
        ),
        inputs=[
            metin_girdisi, referans_ses, lang_dropdown, model_dropdown, exaggeration_slider,
            cfg_slider, chunk_size_slider, temperature_slider, seed_input, max_tokens_slider,
            chunk_gap_slider, mode_dropdown, safety_retry_checkbox, save_chunks_checkbox,
        ],
        outputs=[ses_ciktisi, istatistikler],
    )

if __name__ == "__main__":
    gradio_thread = threading.Thread(
        target=lambda: demo.launch(share=False, css=custom_css),
        daemon=True,
    )
    gradio_thread.start()
    log("🌐 Gradio arayüzü başlatıldı: http://127.0.0.1:7860")
    _main_thread_worker()
