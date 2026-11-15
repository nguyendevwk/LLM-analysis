# Hướng Dẫn Toàn Diện Các Chế Độ Chạy (Modes) & Tham Số

Tài liệu này hướng dẫn chi tiết cách cấu hình, sử dụng các chế độ chạy (**Modes**) và tham số dòng lệnh (**CLI arguments**) cho toàn bộ hệ thống kiểm thử tự động của dự án `LLM-analysis`.

---

## Mục Lục
1. [Tổng Quan Kiến Trúc Thực Nghiệm](#1-tổng-quan-kiến-trúc-thực-nghiệm)
2. [CLI Experiment Runner (`cli_experiment_runner.py`)](#2-cli-experiment-runner-automationcli_experiment_runnerpy)
   - [Mode 1: Single Experiment (Thực nghiệm đơn lẻ)](#mode-1-single-experiment-thực-nghiệm-đơn-lẻ)
   - [Mode 2: Full Scenario (Chạy toàn bộ ma trận)](#mode-2-full-scenario-chạy-toàn-bộ-ma-trận)
   - [Mode 3: Batch Run (Chạy hàng loạt từ JSON)](#mode-3-batch-run-chạy-hàng-loạt-từ-file-json)
   - [Mode 4: Utility & Kiểm tra nhà cung cấp](#mode-4-utility--kiểm-tra-nhà-cung-cấp)
   - [Universal Mode (Kiểm thử file Python bất kỳ)](#universal-mode-kiểm-thử-file-tùy-ý)
   - [Bảng tổng hợp tham số của CLI Runner](#bảng-tổng-hợp-tham-số-cli-experiment-runner)
3. [Kaggle Dual-GPU Council Runner (`kaggle/council_runner.py`)](#3-kaggle-dual-gpu-council-runner-kagglecouncil_runnerpy)
   - [Mode `council` (Pipeline Coder + Critic 2 GPU)](#mode-council-hội-đồng-2-mô-hình-coder--critic)
   - [Mode `full_scenario` (Đo benchmark song song GPU)](#mode-full_scenario-đo-benchmark-song-song-gpu)
   - [Mode `diagnostics` (Chẩn đoán phần cứng)](#mode-diagnostics-chẩn-đoán-phần-cứng)
   - [Bảng tổng hợp tham số Council Runner](#bảng-tổng-hợp-tham-số-council-runner)
4. [Lưu Ý Quan Trọng Về Thư Viện Đột Biến (`mutmut`)](#4-lưu-ý-quan-trọng-về-thư-viện-đột-biến-mutmut)
5. [Bảng Cheatsheet Lệnh Copy-Paste Nhanh](#5-bảng-cheatsheet-lệnh-copy-paste-nhanh)

---

## 1. Tổng Quan Kiến Trúc Thực Nghiệm

Hệ thống cung cấp hai công cụ thực thi chính:
* **`automation/cli_experiment_runner.py`**: Trình chạy linh hoạt dùng cho cả mô hình HuggingFace cục bộ (như `hf-qwen-2.5-coder-7b`) và các API model từ xa (OpenRouter, Google Gemini, Groq, Anthropic Claude).
* **`kaggle/council_runner.py`**: Trình chạy tối ưu hóa phần cứng Dual-GPU (2x Tesla T4) trên Kaggle, sử dụng kiến trúc phản biện hai mô hình (Coder + Critic) lượng tử hóa 4-bit (NF4).

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LLM-ANALYSIS RUNNERS                            │
├───────────────────────────────────┬────────────────────────────────────┤
│   automation/cli_experiment_runner.py   │      kaggle/council_runner.py      │
├───────────────────────────────────┼────────────────────────────────────┤
│ • Chạy 1 bài test cụ thể          │ • Kiến trúc Dual-Agent             │
│ • Chạy ma trận 3x3 tự động        │ • Coder (GPU 0) + Critic (GPU 1)   │
│ • Chạy danh sách batch từ JSON    │ • Lượng tử hóa 4-bit qua NF4       │
│ • Hỗ trợ API Key & Local HF Model │ • Quality Gates đo lường tự động   │
└───────────────────────────────────┴────────────────────────────────────┘
```

---

## 2. CLI Experiment Runner (`automation/cli_experiment_runner.py`)

### Mode 1: Single Experiment (Thực nghiệm đơn lẻ)
Dùng khi bạn muốn kiểm tra nhanh một mô hình trên một chiến lược và một mức ngữ cảnh cụ thể.

* **Tham số bắt buộc:**
  * `--model <tên_model>`: Định danh mô hình cần chạy.
  * `--strategy <chiến_lược>`:
    * `simple_prompting`: Nhắc lệnh trực tiếp đơn giản.
    * `chain_of_thought_prompting`: Nhắc lệnh suy luận từng bước (CoT).
    * `metamorphic_prompting`: Kiểm thử biến thái dựa trên quan hệ Metamorphic Relations (Đề xuất ⭐).
  * `--context <mức_ngữ_cảnh>`:
    * `interface`: Chỉ cung cấp khai báo hàm/phương thức.
    * `interface_docstring`: Cung cấp khai báo hàm kèm docstring mô tả.
    * `full_context`: Cung cấp toàn bộ mã nguồn của lớp cần kiểm thử.

* **Cú pháp ví dụ:**
```bash
python automation/cli_experiment_runner.py \
  --model hf-qwen-2.5-coder-7b \
  --strategy metamorphic_prompting \
  --context full_context
```

---

### Mode 2: Full Scenario (Chạy toàn bộ ma trận)
Tự động chạy toàn bộ **9 bài toán** (3 chiến lược × 3 mức ngữ cảnh) cho 1 mô hình để tạo ra bảng số liệu hoàn chỉnh cho nghiên cứu.

* **Tham số bắt buộc:**
  * `--model <tên_model>`: Tên mô hình cần đánh giá.
  * `--full-scenario`: Cờ kích hoạt chạy ma trận 3×3.

* **Cú pháp ví dụ:**
```bash
python automation/cli_experiment_runner.py \
  --model hf-qwen-2.5-coder-7b \
  --full-scenario
```

> **Ma trận thực nghiệm gồm:**
> 1. `simple_prompting` + `interface`
> 2. `simple_prompting` + `interface_docstring`
> 3. `simple_prompting` + `full_context`
> 4. `chain_of_thought_prompting` + `interface`
> 5. `chain_of_thought_prompting` + `interface_docstring`
> 6. `chain_of_thought_prompting` + `full_context`
> 7. `metamorphic_prompting` + `interface`
> 8. `metamorphic_prompting` + `interface_docstring`
> 9. `metamorphic_prompting` + `full_context`

---

### Mode 3: Batch Run (Chạy hàng loạt từ file JSON)
Dùng để lên lịch chạy tự động qua đêm cho nhiều mô hình hoặc kịch bản tùy biến.

* **Tham số bắt buộc:**
  * `--config <đường_dẫn_file.json>`: Đường dẫn file JSON định nghĩa các thực nghiệm.

* **Cấu trúc file `cli_config.json`:**
```json
{
  "delay_between_experiments": 5,
  "experiments": [
    {
      "model": "hf-qwen-2.5-coder-7b",
      "strategy": "metamorphic_prompting",
      "context": "full_context"
    },
    {
      "model": "groq:llama-3.3-70b-versatile",
      "strategy": "simple_prompting",
      "context": "interface_docstring"
    }
  ]
}
```

* **Cú pháp thực thi:**
```bash
python automation/cli_experiment_runner.py --config configs/experiments.json
```

---

### Mode 4: Utility & Kiểm tra nhà cung cấp

* **Xem danh sách tất cả mô hình khả dụng:**
```bash
python automation/cli_experiment_runner.py --list-models
```

* **Kiểm tra kết nối và API Key:**
Kiểm tra tính hợp lệ của các biến môi trường `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `GROQ_API_KEY`:
```bash
python automation/cli_experiment_runner.py --check-providers
```

---

### Universal Mode (Kiểm thử file tùy ý)
Mặc định hệ thống dùng bài toán chuẩn `OrderCalculator`. Bạn có thể áp dụng hệ sinh thái này để sinh test cho **bất kỳ file Python nào** trong dự án của bạn:

* `--source-file <đường_dẫn_file.py>`: Đường dẫn file mã nguồn muốn sinh test.
* `--class-name <TênClass>`: Tên class mục tiêu (tự động nhận dạng nếu file chỉ có 1 class).
* `--legacy`: Ép buộc dùng `OrderCalculator` ngay cả khi có truyền `--source-file`.

* **Ví dụ Universal:**
```bash
python automation/cli_experiment_runner.py \
  --source-file src/payment_processor.py \
  --class-name PaymentProcessor \
  --model hf-qwen-2.5-coder-7b \
  --strategy metamorphic_prompting \
  --context full_context
```

---

### Bảng Tổng Hợp Tham Số CLI Experiment Runner

| Tham số | Kiểu dữ liệu | Giá trị mặc định | Giải thích chi tiết |
| :--- | :--- | :--- | :--- |
| `--model` | Chuỗi | Bắt buộc (trừ Utility) | Tên model (`hf-*`, `openrouter:*`, `groq:*`, `gemini-*`) |
| `--strategy` | Lựa chọn | `None` | `simple_prompting`, `chain_of_thought_prompting`, `metamorphic_prompting` |
| `--context` | Lựa chọn | `None` | `interface`, `interface_docstring`, `full_context` |
| `--full-scenario`| Cờ bool | `False` | Tự động chạy đủ 9 kết hợp cho 1 model |
| `--config` | Đường dẫn | `None` | Đường dẫn file JSON chạy batch |
| `--results-dir` | Đường dẫn | `cli_results_v1` | Thư mục lưu kết quả thực nghiệm, test code và báo cáo |
| `--run-id` | Số / Chuỗi | `None` (auto-inc) | ID phiên chạy: số nguyên `1`, `2` hoặc `overwrite` để ghi đè |
| `--temperature` | Số thực | Model default | Độ ngẫu nhiên (vd: `0.0` để sinh code tất định, ít lỗi logic) |
| `--max-tokens` | Số nguyên | Provider default | Giới hạn số token tối đa cho phản hồi |
| `--api-key` | Chuỗi | `None` | Ghi đè API key trực tiếp mà không cần cấu hình `.env` |
| `--source-file` | Đường dẫn | `None` | Bật Universal mode cho file mã nguồn tùy chọn |
| `--class-name` | Chuỗi | `None` | Tên lớp trong file mã nguồn của Universal mode |
| `--list-models` | Cờ bool | `False` | Hiển thị danh mục model hỗ trợ |
| `--check-providers`| Cờ bool | `False` | Kiểm tra kết nối mạng và API keys |

---

## 3. Kaggle Dual-GPU Council Runner (`kaggle/council_runner.py`)

Tận dụng song song 2 GPU Tesla T4 (2x 16GB VRAM) hoàn toàn miễn phí trên Kaggle để chạy mô hình suy luận và phản biện đa tác tử.

### Mode `council` (Hội đồng 2 mô hình Coder + Critic)
Quy trình phối hợp 2 tác tử:
1. **Coder (GPU 0)**: Đọc ngữ cảnh mã nguồn và sinh ra bộ test sơ khởi.
2. **Critic (GPU 1)**: Kiểm tra mã test, rà soát thiếu sót biên, logic assert và gửi phản biện.
3. **Coder (GPU 0)**: Tinh chỉnh và sửa mã test dựa trên đóng góp của Critic.
4. **Quality Gates Engine**: Tự động đo lường Statement Coverage, Branch Coverage và Mutation Score.

* **Lệnh chạy:**
```bash
python kaggle/council_runner.py \
  --mode council \
  --load-in-4bit \
  --coder-model "Qwen/Qwen2.5-Coder-7B-Instruct" \
  --critic-model "Qwen/Qwen3-4B-Instruct-2507"
```

---

### Mode `full_scenario` (Đo benchmark song song GPU)
Chạy toàn bộ ma trận 9 bài toán hoàn toàn offline trên GPU Kaggle:

```bash
python kaggle/council_runner.py \
  --mode full_scenario \
  --load-in-4bit \
  --coder-model "Qwen/Qwen2.5-Coder-7B-Instruct"
```

---

### Mode `diagnostics` (Chẩn đoán phần cứng)
Kiểm tra tình trạng nhận diện GPU và dung lượng VRAM:
```bash
python kaggle/council_runner.py --mode diagnostics
```

---

### Bảng Tổng Hợp Tham Số Council Runner

| Tham số | Giá trị mặc định | Giải thích |
| :--- | :--- | :--- |
| `--mode` | `council` | Chọn chế độ: `council`, `full_scenario`, `diagnostics` |
| `--load-in-4bit` | `False` | **Khuyên dùng!** Lượng tử hóa 4-bit (NF4) tiết kiệm 60% VRAM |
| `--coder-model` | `Qwen/Qwen2.5-Coder-7B-Instruct` | Mô hình lập trình viên sinh test |
| `--critic-model`| `Qwen/Qwen3-4B-Instruct-2507` | Mô hình phản biện đánh giá test |
| `--no-critic` | `False` | Tắt chế độ Critic (chỉ chạy đơn lẻ Coder) |
| `--max-new-tokens`| `512` | Độ dài token tối đa cho mỗi lượt trả lời |
| `--temperature` | `0.0` | Nhiệt độ lấy mẫu (0.0 = lấy mẫu tham lam, ổn định nhất) |
| `--source-file` | `order_calculator.py` | Đường dẫn file mã nguồn được kiểm thử |
| `--class-name` | `OrderCalculator` | Tên class mục tiêu |
| `--output-dir` | `kaggle_results` | Thư mục lưu kết quả trên Kaggle |

---

## 4. Lưu Ý Quan Trọng Về Thư Viện Đột Biến (`mutmut`)

> [!IMPORTANT]
> **Quy chuẩn phiên bản Mutmut trong đề tài:**
> * Tất cả các mốc đối chuẩn (baseline) của các mô hình trong bài báo (GPT-4.5, Claude 3.7 Sonnet, Gemini 2.5 Pro, Nemotron) đều sử dụng **chuẩn 109 mutants của `mutmut 2.5.1`**.
> * **Tuyệt đối không dùng `mutmut 3.x` (như 3.8.1)** vì bản 3.x đã loại bỏ các tùy chọn dòng lệnh `--paths-to-mutate` và `--runner`, dẫn đến lỗi dừng tiến trình và trả về điểm số `0/0 mutants (0.0%)`.

### Lệnh cài đặt chuẩn trên Kaggle:
```bash
pip uninstall -y mutmut
pip install -q --no-warn-conflicts "mutmut==2.5.1" "rich<14"
```

---

## 5. Bảng Cheatsheet Lệnh Copy-Paste Nhanh

### Chạy 1 lệnh Metamorphic Prompting trên Kaggle:
```bash
%%bash
pip uninstall -y mutmut
pip install -q --no-warn-conflicts "mutmut==2.5.1" "rich<14"
cd /kaggle/working/LLM-analysis
git pull origin main
python automation/cli_experiment_runner.py \
  --model hf-qwen-2.5-coder-7b \
  --strategy metamorphic_prompting \
  --context full_context
```

### Chạy Council Dual-GPU (Coder + Critic) trên Kaggle:
```bash
%%bash
cd /kaggle/working/LLM-analysis
git pull origin main
python kaggle/council_runner.py --mode council --load-in-4bit
```

### Xem kết quả thực nghiệm vừa chạy:
```bash
cat cli_results_v1/metamorphic_prompting/full_context/hf-qwen-2.5-coder-7b/run_*/podsumowanie-*.md
```
