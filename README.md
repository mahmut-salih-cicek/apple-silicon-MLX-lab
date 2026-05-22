# Chatterbox MLX — Final V9 Fast Stable 🎙️

*[🇹🇷 Türkçe versiyonu aşağıdadır](#türkçe-tr)*

**Chatterbox MLX** is a fast and stable Text-to-Speech (TTS) and voice cloning interface built with Gradio, specifically optimized for Apple Silicon (M1/M2/M3) Macs using MLX. It is designed to handle long-form storytelling naturally while keeping the inference speed high.

---

## English (EN)

### Features
- **Fast & Stable MLX Generation:** Fully optimized for Apple Silicon.
- **Voice Cloning:** Simply upload a reference audio file to clone the speaker's voice.
- **Long Story Mode:** Smart chunking preserves natural prosody, pauses, and dialogue flows.
- **In-App Model Downloading:** Directly download 6-bit or 8-bit quantized models from HuggingFace via the UI.
- **Bilingual Interface:** Automatically detects your system language (Turkish or English) or lets you set it manually.

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/chatterbox-mlx.git
cd chatterbox-mlx
```

**2. Create a virtual environment (Recommended)**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

### How to Run

After installing the requirements, you can start the application by running:
```bash
python app.py
```
*The Gradio interface will automatically start at `http://127.0.0.1:7860`. Open this address in your web browser.*

### Usage & Tips
1. **Downloading a Model:** If you don't have a model yet, open the **"Download Model"** accordion in the UI and click to download the 6-bit or 8-bit version. The model will be placed in the project folder automatically.
2. **Refresh & Select:** Once downloaded, click **"Refresh Model List"** and select your model. Click **"Load Selected Model"**.
3. **Best Practice Settings for Storytelling:**
   - **Exaggeration:** `0.45`
   - **CFG/Pace:** `0.30`
   - **Temperature:** `0.40`
   - **Chunk Size:** `200`
4. **Pause Markers:** For reliable and natural pauses between sentences or paragraphs, use the built-in markers instead of punctuation:
   - `[[pause:short]]` : Short breath (~300ms)
   - `[[pause:medium]]` : Dramatic pause (~650ms)
   - `[[pause:long]]` : Scene transition (~1000ms)

---

## Türkçe (TR)

**Chatterbox MLX**, Apple Silicon (M1/M2/M3) Mac'ler için özel olarak optimize edilmiş, MLX altyapısını kullanan hızlı ve stabil bir Metinden Sese (TTS) ve ses kopyalama (voice cloning) arayüzüdür. Özellikle uzun hikayelerde ve diyaloglarda doğal vurguları koruyacak şekilde tasarlanmıştır.

### Özellikler
- **Hızlı ve Stabil MLX:** Apple Silicon için tam optimizasyon.
- **Ses Kopyalama (Voice Cloning):** Kopyalamak istediğiniz sesi (referans sesi) yüklemeniz yeterli.
- **Uzun Hikaye Modu:** Akıllı metin bölme (chunking) özelliği ile doğal vurgular ve bekleme süreleri korunur.
- **Uygulama İçi Model İndirme:** 6-bit veya 8-bit versiyonları arayüz içerisinden HuggingFace aracılığıyla tek tıkla indirebilirsiniz.
- **İki Dil Desteği:** Sistem dilinizi otomatik algılar (Türkçe/İngilizce). İsterseniz ayarlar bölümünden değiştirebilirsiniz.

### Kurulum

**1. Projeyi klonlayın**
```bash
git clone https://github.com/your-username/chatterbox-mlx.git
cd chatterbox-mlx
```

**2. Sanal ortam (Virtual Environment) oluşturun (Önerilir)**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Gerekli kütüphaneleri yükleyin**
```bash
pip install -r requirements.txt
```

### Nasıl Çalıştırılır?

Gereksinimleri yükledikten sonra terminalde proje klasöründeyken aşağıdaki komutu çalıştırın:
```bash
python app.py
```
*Gradio arayüzü `http://127.0.0.1:7860` adresinde başlayacaktır. Bu adresi tarayıcınızda açabilirsiniz.*

### Kullanım ve İpuçları (Tips)
1. **Model İndirme:** Henüz bir modeliniz yoksa, arayüzdeki **"Model İndir"** sekmesini açarak 6-bit veya 8-bit modellerden birini indirebilirsiniz. Model proje klasörüne otomatik olarak kurulacaktır.
2. **Model Seçimi:** İndirme tamamlandıktan sonra **"Model Listesini Yenile"** tuşuna basıp indirdiğiniz modeli seçin ve **"Seçili Modeli Yükle"** butonuna tıklayın.
3. **Hikaye Anlatımı İçin En İyi Ayarlar:**
   - **Exaggeration (Vurgu):** `0.45`
   - **CFG/Pace (Hız):** `0.30`
   - **Temperature:** `0.40`
   - **Chunk Size:** `200`
4. **Duraklama (Pause) Kullanımı:** Doğal ve tutarlı duraklamalar elde etmek için sadece noktalama işaretleri yerine arayüzdeki marker'ları kullanın:
   - `[[pause:short]]` : Kısa nefes alma (~300ms)
   - `[[pause:medium]]` : Dramatik duraklama (~650ms)
   - `[[pause:long]]` : Sahne geçişi (~1000ms)
