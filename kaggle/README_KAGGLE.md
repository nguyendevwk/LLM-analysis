# Hướng Dẫn Chạy Thực Nghiệm LLM Test Generation Trên Kaggle Dual-GPU ($0 API Cost)

> [!IMPORTANT]
> **Lưu ý triển khai**:
> 1. **Chỉ chạy qua dòng lệnh (CMD / Terminal) hoặc Jupyter Notebook** trên Kaggle, hoàn toàn **không đẩy các model nặng này lên giao diện Web (Streamlit)** để tránh chiếm dụng và tràn VRAM của máy chủ web.
> 2. **Ưu tiên sử dụng modelbase gốc và lượng tử hóa chuẩn NF4 (NormalFloat4)** (`load_in_4bit=True` qua `bitsandbytes>=0.46.1`): Sử dụng trực tiếp `Qwen/Qwen2.5-Coder-7B-Instruct` (hoặc `14B`) và `Qwen/Qwen3-4B-Instruct-2507`, giải phóng VRAM xuống còn ~4.5GB - 8.5GB (không bao giờ tràn VRAM trên Tesla T4 15GB).

---

## 1. Kiến Trúc Điều Phối Hai GPU (Dual-GPU Council Engine)

```
┌────────────────────────────────────────────────────────┐       ┌────────────────────────────────────────────────────────┐
│                 GPU 0: CODER (cuda:0)                  │       │                 GPU 1: CRITIC (cuda:1)                 │
│  - Model: Qwen/Qwen2.5-Coder-7B-Instruct (hoặc 14B)    │       │  - Model: Qwen/Qwen3-4B-Instruct-2507                  │
│  - Quantization: Chuẩn 4-bit NF4 (~4.5GB - 8.5GB VRAM) │       │  - Quantization: Chuẩn 4-bit NF4 (~3.2 GB VRAM)        │
│  - Nhiệm vụ: Sinh mã test & fixtures                   │       │  - Nhiệm vụ: Sửa lỗi cú pháp, logic, vacuous & review  │
└────────────────────────────────────────────────────────┘       └────────────────────────────────────────────────────────┘
```

---

## 2. Cách 1: Chạy Bằng Jupyter Notebook Trên Kaggle (Khuyên Dùng)

1. **Tạo Notebook mới**: Vào [Kaggle](https://www.kaggle.com/) -> **Create** -> **New Notebook**.
2. **Cài đặt phần cứng (Bắt buộc)**:
   - Ở thanh công cụ bên phải (Notebook options):
     - **Accelerator**: Chọn `GPU T4 x2`.
     - **Internet**: Bật `Internet On` (để tải thư viện và model từ Hugging Face).
     - **Persistence**: Chọn `Files only`.
3. **Upload Notebook**:
   - Chọn **File** -> **Import Notebook** -> Chọn file [`kaggle_test_generator.ipynb`](./kaggle_test_generator.ipynb).
4. **Chạy Run All**:
   - Notebook sẽ tự động cài đặt `transformers`, `accelerate`, `bitsandbytes>=0.46.1`, `coverage`, `pytest`.
   - Nạp model Coder lên GPU 0 và Critic lên GPU 1 với chuẩn NF4 4-bit.
   - Tự động sinh test suite, chạy kiểm tra độ phủ nhánh và đo điểm đột biến.
   - Xuất file nén `kaggle_benchmark_results.zip` để tải về máy.

---

## 3. Cách 2: Chạy Bằng Dòng Lệnh (Council Runner)

Trong giao diện dòng lệnh (Terminal) của Kaggle:

```bash
# 1. Clone repository
git clone https://github.com/nguyendevwk/LLM-analysis.git
cd LLM-analysis

# 2. Cài đặt các thư viện
pip install -q --no-warn-conflicts -U "bitsandbytes>=0.46.1" transformers accelerate torch coverage pytest mutmut "rich<14"

# 3. Chạy pipeline Council (Coder 7B + Critic 4B với chuẩn NF4):
python council_runner.py --mode council --load-in-4bit

# Hoặc dùng Coder 14B:
python council_runner.py --mode council --coder-model "Qwen/Qwen2.5-Coder-14B-Instruct" --load-in-4bit

# 4. Chạy full scenario ma trận 2 chiến lược × 3 mức ngữ cảnh:
python council_runner.py --mode full_scenario --load-in-4bit

# 5. Chạy kiểm thử khô không cần nạp trọng số (Mock mode):
python council_runner.py --mock --mode council
```

---

## 4. Chạy Bằng CLI Runner Chuẩn Của Dự Án

Bạn cũng có thể sử dụng trực tiếp `cli_experiment_runner.py` trên Kaggle bằng cờ model `hf:`:

```bash
cd automation

# Chạy Qwen 2.5 Coder 14B bản gốc với chuẩn NF4 trên GPU Kaggle:
python cli_experiment_runner.py \
  --model "hf:Qwen/Qwen2.5-Coder-14B-Instruct" \
  --strategy simple_prompting \
  --context full_context

# Chạy Qwen3 4B (4-bit NF4):
python cli_experiment_runner.py \
  --model "hf:Qwen/Qwen3-4B-Instruct-2507" \
  --strategy chain_of_thought_prompting \
  --context interface_docstring
```

---

## 5. Danh Sách Model Cục Bộ & Kaggle Hỗ Trợ

| Model ID | Provider | Ghi chú VRAM |
|---|---|---|
| `hf-qwen-2.5-coder-7b` | Hugging Face (Kaggle GPU) | Modelbase gốc + Chuẩn NF4: ~4.5GB VRAM (GPU 0) |
| `hf-qwen-2.5-coder-14b` | Hugging Face (Kaggle GPU) | Modelbase gốc + Chuẩn NF4: ~8.5GB VRAM (GPU 0) |
| `hf-qwen3-4b` | Hugging Face (Kaggle GPU) | Modelbase gốc + Chuẩn NF4: ~3.2GB VRAM (GPU 1) |
| `hf-qwen-2.5-3b` | Hugging Face (Kaggle GPU) | Modelbase gốc + Chuẩn NF4: ~2.8GB VRAM (GPU 1) |
| `local-qwen-2.5-coder-14b` | Local (Ollama/vLLM) | Máy cá nhân / Server nội bộ qua API |
| `local-qwen3-4b` | Local (Ollama/vLLM) | Máy cá nhân / Server nội bộ qua API |
