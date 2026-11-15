#!/usr/bin/env python3
"""Bổ sung chỉ số đối chiếu paper vào báo cáo Word, có sao lưu bản gốc."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import shutil

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

import generate_synthesis_report as synthesis


BASE = Path(__file__).resolve().parent
TEMP = Path('/tmp/opencode/docx_paper_metrics')


def insert_after(anchor, text, style='Normal'):
    element = OxmlElement('w:p')
    anchor._p.addnext(element)
    p = Paragraph(element, anchor._parent)
    p.style = style
    p.add_run(text)
    return p


def replace_text(p, text):
    properties = deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    p.clear()
    run = p.add_run(text)
    if properties is not None:
        run._r.insert(0, properties)


def add_row(table, values):
    row = table.add_row()
    for cell, value in zip(row.cells, values):
        cell.text = str(value)


def fmt(series):
    return f'{series.mean():.2f} ± {series.std():.2f}'.replace('.', ',')


def main():
    TEMP.mkdir(parents=True, exist_ok=True)
    df = synthesis.load_all_experimental_data()
    # Render PNG from the same chart code; do not modify existing SVG artifacts.
    savefig = plt.savefig

    def png_save(path, *args, **kwargs):
        kwargs['format'] = 'png'
        kwargs['dpi'] = 180
        savefig(TEMP / (Path(path).stem + '.png'), *args, **kwargs)

    plt.savefig = png_save
    try:
        synthesis.generate_all_svg_charts(df, pd.DataFrame())
    finally:
        plt.savefig = savefig

    fig, axes = plt.subplots(1, 3, figsize=(17, 5), layout='constrained')
    for ax, metric, title in zip(axes, ['compilation_rate', 'method_coverage', 'unique_tests'],
                                ['(a) Biên dịch thành công theo lượt chạy',
                                 '(b) Độ phủ phương thức (MC)',
                                 '(c) Test không bị đánh dấu trùng (proxy)']):
        sns.barplot(data=df, x='model_short', y=metric, hue='strategy_short',
                    errorbar='sd', capsize=.08, ax=ax)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel('Mô hình')
        ax.set_ylabel('%' if metric != 'unique_tests' else 'Số test')
        ax.tick_params(axis='x', rotation=40)
        ax.legend(title='Chiến lược', fontsize=8)
        if metric != 'unique_tests':
            ax.set_ylim(0, 125)
    fig.savefig(TEMP / 'fig_metrics_supplement.png', dpi=180, bbox_inches='tight')
    plt.close(fig)

    for path in sorted((BASE / 'docs').glob('*.docx')):
        doc = Document(path)
        if any('Đối chiếu bổ sung CSR, MC và UT' in p.text for p in doc.paragraphs):
            raise RuntimeError(f'{path.name}: đã bổ sung; không chèn lặp.')
        backup_dir = path.parent / 'backups'
        backup_dir.mkdir(exist_ok=True)
        backup = backup_dir / f'{path.stem}_{datetime.now():%Y%m%d_%H%M%S_%f}.docx'
        shutil.copy2(path, backup)
        paragraphs = list(doc.paragraphs)
        tables = list(doc.tables)

        # Definitions retain the distinction between original-paper metrics and proxies.
        tables[0].rows[5].cells[2].text = 'CSR của paper tính theo test case; bộ mở rộng đo tỷ lệ lượt biên dịch thành công'
        add_row(tables[3], ['Biên dịch thành công theo lượt (CSR_run)',
                           'Tỷ lệ lượt có compilation_success_rate = 100',
                           'Không đồng nhất CSR theo test case trong paper hoặc tỷ lệ Pass'])
        add_row(tables[3], ['Method coverage (MC)',
                           'Số phương thức có test / tổng số phương thức × 100%',
                           'Có test tương ứng không bảo đảm assertion đúng hoặc mọi nhánh được phủ'])
        add_row(tables[3], ['UT trong paper / chỉ số đại diện trong bộ mở rộng',
                           'Paper đếm kịch bản duy nhất sau rà soát thủ công; bộ mở rộng có phát hiện mã tương tự',
                           'Tổng test trừ test bị đánh dấu trùng không phải phép khử trùng giữ một đại diện'])
        replace_text(paragraphs[138],
                     'Method coverage (MC) và số kịch bản độc nhất (UT) được nghiên cứu gốc đề cập bên cạnh CSR, BC, MS và thời gian. '
                     'Bộ mở rộng có method_coverage_rate nên có thể bổ sung MC. Tuy nhiên, UT của paper được rà soát thủ công theo kịch bản; '
                     'dữ liệu duplicate_tests_found chỉ phản ánh mã test có độ tương tự cao, chưa xác nhận trùng ngữ nghĩa. '
                     'Mutation score vẫn cần được đọc theo tập mutant và quy tắc xử lý từng trạng thái.')

        anchor = paragraphs[172]
        for text in [
            'Đối chiếu cách đo CSR: paper [1] định nghĩa CSR = |S|/|T| × 100%, với S là tập test chạy không sinh ngoại lệ và T là toàn bộ test được tạo. '
            'Trong pipeline mở rộng, summary.compilation_success_rate là 0 hoặc 100 cho từng lượt; báo cáo ký hiệu CSR_run = số lượt biên dịch thành công / tổng số lượt × 100%. '
            'CSR_run không thay thế CSR theo test case, không phải tỷ lệ Pass và không xác nhận toàn bộ bộ test chạy thành công.',
            'MC = methods_tested_count / total_methods × 100%, lấy từ method_coverage_rate; đối tượng có 12 phương thức. '
            'Đây là độ phủ ánh xạ phương thức–test của bộ phân tích, không thay thế độ phủ nhánh hoặc kiểm chứng oracle.',
            'Chỉ số đại diện về trùng lặp: U_proxy = max(N_test − duplicate_tests_found, 0). '
            'Bộ phân tích hiện đánh dấu cả hai test của một cặp có độ tương tự mã ít nhất 99,5%; một số dữ liệu cũ có thể lưu số cặp thay vì số test. '
            'Vì vậy U_proxy chỉ được trình bày như số test còn lại theo quy tắc đánh dấu, không được gọi là UT chính xác. '
            'Muốn tái lập UT của paper cần gom nhóm trùng, giữ một đại diện mỗi nhóm và rà soát tính độc nhất của kịch bản.'
        ]:
            anchor = insert_after(anchor, text)

        # Add rows to existing context and strategy result tables, preserving their structure.
        for metric, label in [('compilation_rate', 'CSR_run (%)'), ('method_coverage', 'MC (%)'),
                              ('unique_tests', 'Test không bị đánh dấu trùng (proxy)')]:
            add_row(tables[10], [label] + [fmt(df[df.context == c][metric]) for c in
                                          ['interface', 'interface_docstring', 'full_context']])
            add_row(tables[11], [label] + [fmt(df[df.strategy_short == s][metric]) for s in ['Simple', 'CoT']])

        replace_text(paragraphs[148],
                     'Đã đối chiếu 901 analysis_results.json thuộc bốn nguồn: cli_results_v3; cli_results_v1 (chỉ Nemotron); '
                     'cli_results_v10; cli_results_v11. Cấu hình Nemotron 3 Super 120B + Simple + Interface có 11 lượt thay vì 10, '
                     'giải thích chênh lệch so với 900 lượt dự kiến. Giữ đủ 901 lượt theo bộ tổng hợp, không tự loại quan sát bổ sung. '
                     'Thống kê gộp tính theo lượt chạy nên nhóm có nhiều lượt đóng góp trọng số lớn hơn.')
        replace_text(paragraphs[182],
                     'Bộ dữ liệu gồm 720 lượt Claude/Gemini và 181 lượt của ba mô hình trọng số mở, tổng cộng 901 lượt trên 42 cấu hình. '
                     'Lượt vượt thiết kế thuộc Nemotron 3 Super 120B + Simple + Interface (11 lượt); các cấu hình khác có 30 hoặc 10 lượt. '
                     'Thống kê trong phần bổ sung tính trực tiếp trên dữ liệu từng lượt và dùng độ lệch chuẩn mẫu (ddof = 1).')

        anchor = paragraphs[221]
        anchor = insert_after(anchor, 'Đối chiếu bổ sung CSR, MC và UT', 'Heading 3')
        anchor = insert_after(anchor,
            'Phần bổ sung sử dụng 901 lượt chạy. CSR_run trung bình theo lượt đạt ' +
            f'{df.compilation_rate.mean():.2f}%'.replace('.', ',') +
            ', tương ứng 891/901 lượt biên dịch thành công; MC trung bình đạt ' +
            f'{df.method_coverage.mean():.2f}%'.replace('.', ',') +
            '. Các số liệu này không thay thế CSR per-test và UT được rà soát thủ công của paper. '
            'Các giá trị trong bảng là trung bình ± độ lệch chuẩn mẫu của từng lượt trong nhóm.')
        anchor = insert_after(anchor, 'Bảng 4.6. Đối chiếu chỉ số bổ sung theo mô hình', 'Table Heading')
        table = doc.add_table(rows=1, cols=5)
        table.style = tables[12].style
        for c, text in zip(table.rows[0].cells, ['Mô hình', 'n', 'CSR_run (%)', 'MC (%)', 'U_proxy (test)']):
            c.text = text
        for name, group in df.groupby('model_display', sort=True):
            add_row(table, [name, len(group), fmt(group.compilation_rate), fmt(group.method_coverage), fmt(group.unique_tests)])
        anchor._p.addnext(table._tbl)
        # Move a following paragraph after the newly inserted table.
        anchor = insert_after(anchor, '')
        table._tbl.addnext(anchor._p)
        anchor.add_run('Bốn mô hình có CSR_run 100% gồm Claude Opus 4.5, Gemini 3 Pro và hai GPT-OSS; '
                       'đây là kết quả đồng hạng, không có mô hình dẫn đầu duy nhất. Gemini 3 Flash có CSR_run 95,56% '
                       'và MC 95,88%; MC của các mô hình còn lại đạt 100%. MC bão hòa không có nghĩa BC hoặc MS cũng cao.')
        anchor = insert_after(anchor,
            'CoT có trung bình 75,17 test và U_proxy 71,34; Simple có 49,48 test và U_proxy 48,73. '
            'Sự chênh lệch cho thấy cần kiểm tra mức trùng lặp khi tăng quy mô đầu ra, nhưng chưa đủ để kết luận '
            'số kịch bản độc nhất hay tỷ lệ dư thừa ngữ nghĩa. Không sử dụng U_proxy như phép đo UT đã được xác thực.')
        anchor = insert_after(anchor, '')
        anchor.add_run().add_picture(str(TEMP / 'fig_metrics_supplement.png'), width=Inches(6.2))
        insert_after(anchor,
                     'Hình 4.6. Chỉ số bổ sung theo mô hình và chiến lược: (a) CSR_run; (b) MC; '
                     '(c) số test không bị đánh dấu trùng (proxy, không phải UT thủ công). Thanh sai số biểu diễn độ lệch chuẩn mẫu.')

        # Replace embedded figures without losing the text in their paragraphs.
        chart_mapping = {
            197: 'fig1_coverage_mutation_dual_panel',
            206: 'fig2_strategy_context_comparison',
            214: 'fig3_quality_smells_evaluation',
            228: 'fig6_context_prompting_interaction',
            240: 'fig4_efficiency_test_suite_volume',
        }
        for idx, name in chart_mapping.items():
            p = paragraphs[idx]
            for drawing in p._p.xpath('.//w:drawing'):
                drawing.getparent().remove(drawing)
            p.add_run().add_picture(str(TEMP / f'{name}.png'), width=Inches(6.2))
        replace_text(paragraphs[200],
            'Hình 4.1. Độ phủ và độ tin cậy: (a) SC; (b) BC; (c) MC theo mô hình và chiến lược; '
            '(d) MS theo ngữ cảnh; (e) tỷ lệ lượt biên dịch thành công (nhãn CSR trong hình tương ứng CSR_run); '
            '(f) tương quan SC–MS. Thanh sai số là độ lệch chuẩn mẫu.')
        replace_text(paragraphs[215],
            'Hình 4.3. Chất lượng mã và thực thi: (a) điểm chất lượng tổng thể; (b) chất lượng assertion và kiểm tra ngoại lệ; '
            '(c) điểm vắng mặt mùi mã; (d) tỷ lệ bộ test thực thi thành công. Các điểm chất lượng là thước đo tự động của pipeline, '
            'không phải các phép đo trong paper gốc.')
        replace_text(paragraphs[213],
            'Hình 4.3 bổ sung các thước đo cấu trúc mã và khả năng thực thi do pipeline tính. '
            'Không diễn giải hình này thành tỷ lệ test rỗng, xác suất flaky test hay độ trùng assertion vì các đại lượng đó không được biểu diễn.')
        replace_text(paragraphs[241],
            'Hình 4.5. Thời gian và quy mô bộ test: (a) phân tán thời gian–MS (chưa tính đường biên Pareto); '
            '(b) tổng số test và U_proxy (nhãn UT trong hình chỉ là proxy, chưa phải kịch bản độc nhất); '
            '(c) assertion trung bình mỗi test; (d) phân bố MS.')
        replace_text(paragraphs[245],
            'Đã xác định nguồn chênh lệch số mẫu: cấu hình Nemotron + Simple + Interface có 11 lượt; '
            'tổng thực tế là 901 lượt. Số lần lặp không cân bằng giữa mô hình và cấu hình làm trung bình theo lượt khác '
            'trung bình trọng số bằng nhau theo mô hình. Không dùng hai kiểu trung bình thay thế cho nhau.')
        insert_after(paragraphs[250],
            'Giới hạn của phần bổ sung: CSR_run là chỉ báo biên dịch theo lượt, không phải CSR theo test của paper. '
            'MC dựa trên kết quả ánh xạ của bộ phân tích; U_proxy chưa được xác thực bằng rà soát kịch bản. '
            'Số lượng bản ghi có chỉ số không bảo đảm tính đúng đắn của bộ đo. Cần chuẩn hóa trường duplicate_tests_found '
            'và kiểm tra mã test trước khi sử dụng chỉ số độc nhất trong kết luận chính.')
        insert_after(paragraphs[259],
            'Bổ sung CSR_run và MC giúp tách khả năng biên dịch khỏi phạm vi phương thức được kiểm tra: '
            'trung bình theo lượt lần lượt là 98,89% và 99,18%. Tuy vậy, các mức cao này không thay thế khả năng '
            'phát hiện đột biến; UT theo định nghĩa kịch bản độc nhất của paper vẫn cần được xác nhận thủ công.')
        # Ask Word to refresh fields (TOC, page numbers) when the document opens.
        settings = doc.settings.element
        update = OxmlElement('w:updateFields')
        update.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'true')
        settings.append(update)
        doc.save(path)
        check = Document(path)
        assert len(check.tables) == len(tables) + 1
        assert any('Đối chiếu bổ sung CSR, MC và UT' in p.text for p in check.paragraphs)
        print(f'UPDATED: {path}\nBACKUP: {backup}\nTABLES: {len(check.tables)}; IMAGES: {len(check.inline_shapes)}')


if __name__ == '__main__':
    main()
