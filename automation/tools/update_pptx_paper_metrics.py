#!/usr/bin/env python3
"""Bổ sung đánh giá CSR_run, MC và chỉ số trùng lặp vào slide hiện có."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

BASE = Path(__file__).resolve().parent
TEMP = Path('/tmp/opencode/pptx_paper_metrics')
NAVY = RGBColor.from_string('16213B')
TEAL = RGBColor.from_string('167D9A')


def text(shape, value):
    frame = shape.text_frame
    prototype = deepcopy(frame.paragraphs[0].runs[0]._r.rPr) if frame.paragraphs[0].runs else None
    frame.clear()
    frame.paragraphs[0].text = value
    if prototype is not None:
        frame.paragraphs[0].runs[0]._r.insert(0, prototype)


def box(slide, value, x, y, w, h, size=20):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    shape.text_frame.word_wrap = True
    shape.text_frame.margin_left = 0
    for i, line in enumerate(value.split('\n')):
        p = shape.text_frame.paragraphs[0] if i == 0 else shape.text_frame.add_paragraph()
        p.text = line
        p.font.name = 'Calibri'
        p.font.size = Pt(size)
        p.font.color.rgb = NAVY
        p.space_after = Pt(10)
    return shape


def table(slide, rows, widths, y=1.5, height=3.9, size=17):
    t = slide.shapes.add_table(len(rows), len(rows[0]), Inches(.65), Inches(y),
                               Inches(12), Inches(height)).table
    for c, width in zip(t.columns, widths):
        c.width = Inches(width)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = str(val)
            c.fill.solid()
            c.fill.fore_color.rgb = NAVY if i == 0 else RGBColor.from_string('F0F5F8' if i % 2 else 'FFFFFF')
            for p in c.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(size)
                p.font.bold = i == 0
                p.font.color.rgb = RGBColor(255, 255, 255) if i == 0 else NAVY
    return t


def fmt(s):
    return f'{s.mean():.2f} ± {s.std():.2f}'.replace('.', ',')


def main():
    path = BASE / 'docs/Nhom7_CNPMTT_Thuyet_trinh_cap_nhat.pptx'
    prs = Presentation(path)
    old = list(prs.slides)
    if any(sh.has_text_frame and 'CSR_run, MC và UT: cách đọc' in sh.text
           for sl in old for sh in sl.shapes):
        raise RuntimeError('Slide đã được bổ sung; không chèn lặp.')
    backup = path.parent / 'backups' / f'{path.stem}_before_metrics_{datetime.now():%Y%m%d_%H%M%S}.pptx'
    backup.parent.mkdir(exist_ok=True)
    shutil.copy2(path, backup)
    df = pd.read_csv(BASE / 'synthesis_output/data/aggregated_raw_dataset.csv')
    TEMP.mkdir(parents=True, exist_ok=True)

    def new_slide(title, category):
        s = prs.slides.add_slide(old[15].slide_layout)
        for shape in list(s.shapes):
            shape._element.getparent().remove(shape._element)
        for shape in list(old[15].shapes)[:4]:
            s.shapes._spTree.insert_element_before(deepcopy(shape._element), 'p:extLst')
        text(s.shapes[0], title)
        text(s.shapes[2], category)
        return s

    theory = new_slide('CSR_run, MC và UT: cách đọc', 'LÝ THUYẾT')
    table(theory, [
        ['Chỉ số', 'Định nghĩa / cách đo', 'Lưu ý khi đánh giá'],
        ['CSR của paper', '|Test không sinh ngoại lệ| / |Test sinh ra| × 100%', 'Đơn vị: test case; không chỉ là đúng cú pháp'],
        ['CSR_run', 'Lượt biên dịch thành công / tổng lượt × 100%', 'Dữ liệu hiện có; khác CSR của paper và Pass rate'],
        ['MC', 'Phương thức có test / tổng phương thức × 100%', 'MC cao không bảo đảm BC, MS hoặc oracle đúng'],
        ['UT / U_proxy', 'UT: kịch bản độc nhất sau rà soát; proxy: N_test − D (chặn dưới 0)', 'D đếm cặp hay test phải được xác minh; proxy không phải UT'],
    ], [1.45, 5.0, 5.55], height=4.35, size=18)
    box(theory, 'Nguồn: Walczak và cộng sự, arXiv:2507.14256, mục III-B.\nCác phép đo khác đơn vị quan sát không được dùng thay thế cho nhau.', .7, 6, 12, .8, 17)

    models = new_slide('Đánh giá bổ sung: độ tin cậy và MC', 'KẾT QUẢ')
    rows = [['Mô hình', 'n', 'CSR_run (%)', 'MC (%)']]
    for name, g in df.groupby('model_display'):
        rows.append([name, len(g), fmt(g.compilation_rate), fmt(g.method_coverage)])
    table(models, rows, [4.2, 1, 3.4, 3.4], height=3.9, size=18)
    box(models, 'Theo lượt: CSR_run = 98,89% (891/901); MC = 99,18%.\nBốn mô hình cùng CSR_run 100%. MC gần bão hòa, chưa cho biết khả năng bắt lỗi.', .7, 5.8, 12, .9, 19)
    models.notes_slide.notes_text_frame.text = (
        'Giá trị là trung bình ± độ lệch chuẩn mẫu (ddof=1), nhóm theo mô hình. '
        'CSR_run là cờ biên dịch 0/100 từng lượt, không phải tỷ lệ test case theo paper. '
        'MC lấy từ method_coverage_rate của pipeline. Không suy ra ý nghĩa thống kê từ bảng này.')

    context = new_slide('Ngữ cảnh và prompting: CSR_run, MC', 'ĐÁNH GIÁ')
    fig, axes = plt.subplots(1, 2, figsize=(13, 4), layout='constrained')
    groups = df.groupby(['context_short', 'strategy_short'])[['compilation_rate', 'method_coverage']].mean()
    for ax, metric, label in zip(axes, ['compilation_rate', 'method_coverage'], ['CSR_run (%)', 'MC (%)']):
        pivot = groups[metric].unstack().reindex(['Interface', 'I+Doc', 'Full Context'])
        pivot.plot.bar(ax=ax, color=['#167D9A', '#E3A049'], rot=0)
        ax.set_title(label)
        ax.set_ylim(0, 110)
        ax.set_xlabel('Ngữ cảnh')
        ax.set_ylabel('%')
        ax.legend(title='Chiến lược')
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=.2)
    fig.savefig(TEMP / 'context_metrics.png', dpi=180)
    plt.close(fig)
    context.shapes.add_picture(str(TEMP / 'context_metrics.png'), Inches(.7), Inches(1.55), width=Inches(11.9))
    box(context, 'Các tỷ lệ quan sát đều cao nhưng không tăng đơn điệu theo lượng context.\nĐọc cùng BC, MS và Pass rate; chưa quy khác biệt cho cơ chế của mô hình.', .7, 5.85, 12, .9, 19)
    context.notes_slide.notes_text_frame.text = ('Cột hiển thị trung bình theo lượt, không hiển thị khoảng tin cậy. '
        'MC theo context: Interface 99,83%; I+Doc 99,42%; Full 98,28%. '
        'CSR_run theo context: 99,00%; 99,33%; 98,33%. Chưa có kiểm định khác biệt.')

    unique = new_slide('Trùng lặp đầu ra: phân tích thăm dò', 'THẢO LUẬN')
    fig, ax = plt.subplots(figsize=(10.5, 3.5), layout='constrained')
    means = df.groupby('strategy_short')[['total_test_methods', 'unique_tests']].mean().reindex(['Simple', 'CoT'])
    means.columns = ['Tổng test sinh ra', 'U_proxy (không phải UT)']
    means.plot.bar(ax=ax, color=['#167D9A', '#E3A049'], rot=0)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', padding=3)
    ax.set_ylim(0, 90)
    ax.set_ylabel('Số test trung bình / lượt')
    ax.set_xlabel('Chiến lược')
    ax.spines[['top', 'right']].set_visible(False)
    fig.savefig(TEMP / 'unique_proxy.png', dpi=180)
    plt.close(fig)
    unique.shapes.add_picture(str(TEMP / 'unique_proxy.png'), Inches(1.15), Inches(1.4), width=Inches(10.7))
    box(unique, 'U_proxy = max(N_test − D, 0); D là số lượng do bộ phát hiện trùng trả về.\nKhông suy ra số kịch bản độc nhất từ độ giống mã. Cần gom nhóm, giữ đại diện và rà soát.\nQuan sát này gợi ý kiểm tra trùng lặp, chưa xác nhận mức dư thừa ngữ nghĩa.', .7, 5.25, 12, 1.35, 19)
    unique.notes_slide.notes_text_frame.text = (
        'UT trong paper được rà soát thủ công theo kịch bản. Bộ phân tích hiện đánh dấu cả hai test '
        'có độ tương tự mã >=99,5%; một số kết quả cũ có thể ghi số cặp. '
        'Không gọi phép trừ này là khử trùng giữ đại diện và không đưa proxy vào kết luận chính.')

    # Integrate terminology into existing theory, methods and results slides.
    t = old[4].shapes[4].table
    t.cell(2, 1).text = 'Câu lệnh, nhánh và phương thức có test'
    t.cell(2, 2).text = 'SC, BC, MC'
    t.cell(4, 2).text = 'Test count, assertions; U_proxy (thăm dò)'
    text(old[15].shapes[5], 'Ghi riêng biên dịch (CSR_run), thực thi và Pass rate.\nBổ sung MC; trùng lặp chỉ dùng proxy, chưa phải UT của paper.')
    old[15].shapes[4].table.cell(4, 2).text = 'SC, BC, MC, MS, CSR_run, Pass rate'
    text(old[12].shapes[6], 'Đã đối chiếu 901 lượt: Nemotron + Simple + Interface có 11 lượt.\nThống kê gộp theo lượt; không loại lượt bổ sung ngoài thiết kế 900.')
    text(old[13].shapes[6], 'Bộ phân tích ghi 12 phương thức. MC đo ánh xạ phương thức–test;\nkhông áp dụng mặc định giới hạn BC của paper cho bộ mở rộng.')
    # Replace the strategy table with a version including the two validated data fields.
    old_shape = old[18].shapes[4]
    old_shape._element.getparent().remove(old_shape._element)
    strategy_rows = [['Chỉ số', 'Simple', 'CoT', 'Chênh lệch']]
    for metric, label in [('statement_coverage', 'SC (%)'), ('branch_coverage', 'BC (%)'),
                          ('method_coverage', 'MC (%)'), ('compilation_rate', 'CSR_run (%)'),
                          ('mutation_score', 'MS (%)'), ('response_time', 'Thời gian (s)')]:
        m = df.groupby('strategy_short')[metric].mean()
        delta = f'{m.CoT - m.Simple:+.2f} đpt' if metric != 'response_time' else f'×{m.CoT / m.Simple:.2f}'
        strategy_rows.append([label, f'{m.Simple:.2f}'.replace('.', ','), f'{m.CoT:.2f}'.replace('.', ','), delta.replace('.', ',')])
    table(old[18], strategy_rows, [2, 1.55, 1.55, 2.2], y=1.48, height=3.65, size=17)
    # Existing lower picture and footer are preserved; table ends before them.
    limits = old[22].shapes[4].table
    limits.cell(2, 0).text = 'Số lần lặp không cân bằng (901 lượt)'
    limits.cell(2, 1).text = 'Đã xác định lượt thêm; cần xét trọng số khi so sánh'
    text(old[22].shapes[5], 'CSR_run khác CSR theo test; UT proxy chưa được xác thực.\nCI/CD vẫn cần thực thi, đối chiếu oracle và rà soát đầu ra.')

    # Place new slides within the original flow, not after the closing slide.
    order = []
    for i, s in enumerate(old):
        order.append(s)
        if i == 9:
            order.append(theory)
        if i == 19:
            order.extend([models, context])
        if i == 20:
            order.append(unique)
    ids = {el.id: el for el in list(prs.slides._sldIdLst)}
    for s in order:
        prs.slides._sldIdLst.append(ids[s.slide_id])
    prs.save(path)
    check = Presentation(path)
    assert len(check.slides) == len(old) + 4
    print(f'UPDATED {path}\nBACKUP {backup}\nSLIDES {len(old)} -> {len(check.slides)}')


if __name__ == '__main__':
    main()
