# Hướng Dẫn Chạy Thực Nghiệm LLM Test Generation Trên Kaggle Dual-GPU ($0 API Cost)

Tài liệu này hướng dẫn cách triển khai và chạy tự động sinh unit test và đo lường độ phủ nhánh (Branch Coverage), điểm đột biến (Mutation Score) trên môi trường **Kaggle Dual-GPU (2x Tesla T4 15GB)** hoàn toàn miễn phí.

---

## 1. Kiến Trúc Điều Phối Hai GPU (Dual-GPU MoA)

```
┌──────────────────────────────────────────────┐       ┌──────────────────────────────────────────────┐
│           GPU 0: CODER (cuda:0)              │       │           GPU 1: CRITIC (cuda:1)             │
│  - Model: Qwen/Qwen2.5-Coder-14B-Instruct    │       │  - Model: Qwen/Qwen3-4B-Instruct-2507        │
│  - Quantization: 4-bit NF4 (~8.5 GB VRAM)    │       │  - Quantization: 4-bit NF4 (~3.2 GB VRAM)    │
│  - Nhiệm vụ: Sinh mã test & fixtures         │       │  - Nhiệm vụ: Sửa lỗi cú pháp, logic & review │
└──────────────────────────────────────────────┘       └──────────────────────────────────────────────┘
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
   - Notebook sẽ tự động cài đặt `transformers`, `accelerate`, `bitsandbytes`, `coverage`, `pytest`.
   - Nạp model Coder 14B lên GPU 0 và Critic 4B lên GPU 1.
   - Tự động sinh test suite, chạy kiểm tra độ phủ nhánh và đo điểm đột biến.
   - Xuất file nén `kaggle_benchmark_results.zip` để tải về máy.

---

## 3. Cách 2: Chạy Bằng Dòng Lệnh (CLI Runner)

Trong giao diện dòng lệnh (Terminal) của Kaggle:

```bash
# 1. Clone repository
git clone https://github.com/nguyendevwk/LLM-analysis.git
cd LLM-analysis

# 2. Cài đặt các thư viện
pip install -q torch transformers accelerate bitsandbytes coverage pytest

# 3. Chạy pipeline Council (Coder 14B + Critic 4B)
python kaggle/kaggle_dual_gpu_runner.py --mode council

# 4. Chạy full scenario ma trận 2 chiến lược × 3 mức ngữ cảnh
python kaggle/kaggle_dual_gpu_runner.py --mode full_scenario --coder-model "Qwen/Qwen2.5-Coder-14B-Instruct"

# 5. Chạy cho class bất kỳ của bạn (Universal Mode)
python kaggle/kaggle_dual_gpu_runner.py \
  --mode council \
  --source-file /path/to/your_class.py \
  --class-name YourClassName
```

---

## 4. Chạy Bằng CLI Runner Chuẩn Của Dự Án

Bạn cũng có thể sử dụng trực tiếp `cli_experiment_runner.py` trên Kaggle bằng cờ model `hf:`:

```bash
cd automation

# Chạy Qwen 2.5 Coder 14B trực tiếp trên GPU Kaggle:
python cli_experiment_runner.py \
  --model "hf:Qwen/Qwen2.5-Coder-14B-Instruct" \
  --strategy simple_prompting \
  --context full_context

# Chạy Qwen3 4B:
python cli_experiment_runner.py \
  --model "hf:Qwen/Qwen3-4B-Instruct-2507" \
  --strategy chain_of_thought_prompting \
  --context interface_docstring
```

---

## 5. Danh Sách Model Cục Bộ & Kaggle Hỗ Trợ

| Model ID | Provider | Ghi chú VRAM |
|---|---|---|
| `hf-qwen-2.5-coder-14b` | Hugging Face (Kaggle GPU) | 4-bit NF4: ~8.5GB VRAM (GPU 0) |
| `hf-qwen-2.5-coder-7b` | Hugging Face (Kaggle GPU) | 4-bit NF4: ~4.5GB VRAM |
| `hf-qwen3-4b` | Hugging Face (Kaggle GPU) | 4-bit NF4: ~3.2GB VRAM (GPU 1) |
| `hf-qwen-2.5-3b` | Hugging Face (Kaggle GPU) | 4-bit NF4: ~2.8GB VRAM |
| `local-qwen-2.5-coder-14b` | Local (Ollama/vLLM) | Máy cá nhân / Server nội bộ |
| `local-qwen3-4b` | Local (Ollama/vLLM) | Máy cá nhân / Server nội bộ |
