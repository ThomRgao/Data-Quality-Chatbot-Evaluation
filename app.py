"""DataTrust - Data Analyst portfolio application."""
from pathlib import Path
from html import escape
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.quality import analyze
from src.evaluation import models, run_case, score_review
from src.workspace import read_table, save_table, read_runs, save_runs, manage
ROOT = Path(__file__).parent

class Antarmuka:

    def __init__(self, original):
        self.original = original

    def __getattr__(self, name):
        return getattr(self.original, name)

    def dataframe(self, data, *args, **kwargs):
        if isinstance(data, pd.DataFrame):
            config = dict(kwargs.get('column_config', {}))
            for c in data.columns:
                config.setdefault(c, KOLOM.get(c, c))
            kwargs['column_config'] = config
        return self.original.dataframe(data, *args, **kwargs)

    def data_editor(self, data, *args, **kwargs):
        config = dict(kwargs.get('column_config', {}))
        for c in data.columns:
            if c not in config:
                config[c] = KOLOM.get(c, c)
        kwargs['column_config'] = config
        return self.original.data_editor(data, *args, **kwargs)
KOLOM = {'Area': 'Bidang', 'Criterion': 'Kriteria', 'PIC role': 'Peran PIC', 'Mandatory': 'Wajib', 'Evidence / gap': 'Bukti / kekurangan', 'Action': 'Tindakan', 'Priority': 'Prioritas', 'Scenario': 'Skenario', 'Defect ID': 'ID kendala', 'Retest action': 'Tindakan uji ulang', 'Department': 'Departemen', 'User ID': 'ID pengguna', 'Eligible': 'Memenuhi kriteria', 'Training complete': 'Pelatihan selesai', 'Active in last 7 days': 'Aktif 7 hari terakhir', 'Task completed': 'Tugas selesai', 'Severity': 'Tingkat keparahan', 'Owner role': 'Peran pemilik', 'Issue ID': 'ID kendala', 'Description': 'Deskripsi', 'Due date': 'Tenggat', 'Test ID': 'ID pengujian', 'Case ID': 'ID kasus', 'Split': 'Kelompok', 'Category': 'Kategori', 'Question': 'Pertanyaan', 'Reference answer': 'Jawaban acuan', 'Source ID': 'ID sumber', 'Expected behavior': 'Perilaku yang diharapkan', 'Topic': 'Topik', 'Version': 'Versi', 'Effective date': 'Tanggal berlaku', 'Expiry date': 'Tanggal kedaluwarsa', 'Access': 'Akses', 'Record ID': 'ID baris', 'Shipment ID': 'ID pengiriman', 'Branch': 'Cabang', 'Fee': 'Biaya', 'Created at': 'Waktu dibuat', 'Updated at': 'Waktu diperbarui', 'Delivered at': 'Waktu terkirim', 'Fee IDR': 'Biaya (Rp)', 'Created date': 'Tanggal dibuat', 'Delivered date': 'Tanggal terkirim', 'Type': 'Jenis', 'Dependency': 'Ketergantungan', 'Next action': 'Tindakan berikutnya', 'eligible': 'Memenuhi kriteria', 'active': 'Aktif', 'trained': 'Dilatih', 'completed': 'Selesai', 'branch': 'Cabang', 'shipments': 'Pengiriman', 'fees_idr': 'Biaya (Rp)', 'delivered_share': 'Proporsi terkirim', 'recorded': 'Tercatat', 'reviewed': 'Dinilai', 'accepted': 'Lulus', 'acceptance_rate': 'Tingkat kelulusan'}
st = Antarmuka(st)
st.set_page_config(page_title='DataTrust', page_icon='◈', layout='wide', initial_sidebar_state='expanded')
st.markdown('<style>\n:root{--ink:#16243c;--muted:#6c7a91;--violet:#6252d9;--line:#e7eaf0}\n.stApp{background:#f5f7fb;color:var(--ink)}\n[data-testid="stSidebar"]{background:#121e35;border-right:none}\n[data-testid="stSidebar"] *{color:#dae3f5}\n[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{font-size:13px;line-height:1.6}\n[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:10px 4px}\n.block-container{padding:2rem 2.4rem 4rem;max-width:1550px}\nh1,h2,h3{letter-spacing:-.035em;color:var(--ink)}\nh1{font-weight:750!important;font-size:2.65rem!important}\nh3{font-size:1.1rem!important;letter-spacing:-.02em}\n.eyebrow{font-size:11px;font-weight:750;letter-spacing:.16em;color:#796bea;margin-bottom:12px}\n.hero-copy{font-size:15px;line-height:1.7;color:#718097;max-width:820px;margin-bottom:24px}\n.tag{display:inline-block;font-size:10px;font-weight:750;letter-spacing:.08em;padding:6px 10px;border-radius:20px;background:#ece9ff;color:#6552c7;margin-right:7px}\n.metric{background:white;border:1px solid #e6eaf1;border-radius:15px;padding:20px 22px;min-height:130px;margin:8px 0 16px;box-shadow:0 4px 15px #14233c03}\n.metric-name{font-size:11px;font-weight:700;color:#8390a5;letter-spacing:.07em;text-transform:uppercase}\n.metric-value{font-size:33px;line-height:1.35;letter-spacing:-.04em;font-weight:750;margin-top:10px;color:#1d2b43}\n.metric-sub{font-size:11px;color:#8b96aa;margin-top:5px}\n.module{background:white;border:1px solid #e5eaf2;border-radius:18px;padding:25px 27px;margin:8px 0 16px;min-height:260px}\n.module-index{font-size:11px;letter-spacing:.13em;font-weight:750;margin-bottom:17px;color:#8273ed}\n.module h2{font-size:23px;line-height:1.3;margin:0 0 14px}\n.module p{color:#7d889b;line-height:1.75;font-size:14px}\n.module-footer{border-top:1px solid #edf0f5;margin-top:24px;padding-top:15px;font-size:11px;color:#64718a;font-weight:650}\n.decision{background:#fff7ed;border:1px solid #f8d4a7;border-radius:14px;padding:19px 23px;margin:6px 0 20px}\n.decision strong{color:#ab5c17;font-size:18px}.decision p{color:#926b43;font-size:13px;margin:7px 0 0}\n.good{background:#edf9f3;border-color:#b8e5cc}.good strong{color:#217b54}.good p{color:#4b8168}\n.micro{font-size:11px;color:#8b96a8;line-height:1.6}\n.section-note{font-size:12px;color:#7d8a9f;margin:0 0 10px}\n[data-testid="stVerticalBlockBorderWrapper"]{border-radius:16px}\n[data-testid="stTabs"] button{font-size:13px!important;font-weight:600}\n.stButton>button{border-radius:9px}.stDownloadButton>button{border-radius:9px}\n[data-testid="stPlotlyChart"]{border:1px solid #e7ebf3;border-radius:14px;overflow:hidden;background:white}\nfooter{visibility:hidden}\n@media(max-width:800px){.block-container{padding:1.2rem}h1{font-size:2rem!important}.metric-value{font-size:27px}}\n</style>', unsafe_allow_html=True)

def load(name):
    return read_table(ROOT, name)

def metric(label, value, sub):
    st.markdown(f'<div class="metric"><div class="metric-name">{escape(label)}</div><div class="metric-value">{escape(str(value))}</div><div class="metric-sub"></div></div>', unsafe_allow_html=True)

def hero(kicker, title, text):
    st.markdown(f'<div class="eyebrow">{escape(kicker)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="hero-copy">{escape(text)}</div>', unsafe_allow_html=True)

def polish(fig, height=335):
    fig.update_layout(height=height, paper_bgcolor='white', plot_bgcolor='white', font=dict(family='Arial', size=12, color='#7b879c'), title_font=dict(size=15, color='#26364e'), margin=dict(l=25, r=25, t=60, b=30), legend=dict(orientation='h', y=-0.2, x=0, title=None), colorway=['#7160d8', '#79c2b1', '#e9ad60', '#b8c5df'], hoverlabel=dict(bgcolor='white', font_size=12))
    fig.update_xaxes(showgrid=False, zeroline=False, title=None)
    fig.update_yaxes(gridcolor='#edf0f6', zeroline=False, title=None, rangemode='tozero')
    return fig

def download_frame(frame, label, filename, key):
    st.download_button(label, frame.to_csv(index=False).encode('utf-8-sig'), filename, 'text/csv', key=key)
EDIT_ROUTES = {'Ubah Data Pengiriman': 'shipments.csv', 'Kelola Pertanyaan AI': 'evaluation_cases.csv', 'Kelola Sumber Jawaban': 'knowledge_base.csv'}
with st.sidebar:
    page = st.radio('MENU', ['Kualitas Data', 'Evaluasi AI', 'Metodologi', 'Kelola Data', 'Ubah Data Pengiriman', 'Kelola Pertanyaan AI', 'Kelola Sumber Jawaban'])
if page == 'Kelola Data' or page in EDIT_ROUTES:

    def validate(name, frame):
        expected = list(pd.read_csv(ROOT / 'data' / name, nrows=0).columns)
        if list(frame.columns) != expected:
            raise ValueError('Struktur kolom tidak sesuai.')
        if name in {'readiness.csv', 'uat.csv', 'issues.csv', 'adoption.csv'}:
            tables = {n: load(n + '.csv') for n in ['readiness', 'uat', 'issues', 'adoption']}
            tables[name[:-4]] = frame
            assess(**tables)
        elif name == 'shipments.csv':
            analyze(frame)
        elif name == 'evaluation_cases.csv':
            if frame.empty or frame['Case ID'].duplicated().any() or (frame['Case ID'].astype(str).str.strip() == '').any():
                raise ValueError('ID kasus wajib unik dan tidak kosong.')
            if not set(frame['Split']).issubset({'Development', 'Held-out'}):
                raise ValueError('Split harus Development atau Held-out.')
            sources = set(load('knowledge_base.csv')['Source ID'])
            if not set(frame['Source ID']).issubset(sources):
                raise ValueError('Source ID harus terdaftar pada basis pengetahuan.')
        elif name == 'knowledge_base.csv':
            if frame.empty or frame['Source ID'].duplicated().any():
                raise ValueError('ID sumber wajib unik dan tabel tidak boleh kosong.')
            if not set(load('evaluation_cases.csv')['Source ID']).issubset(set(frame['Source ID'])):
                raise ValueError('Sumber masih dipakai oleh kasus uji.')
    manage(st, ROOT, validate, fixed_name=EDIT_ROUTES.get(page))
    st.stop()
if page == 'Kualitas Data':
    hero('RUANG ANALISIS', 'Data yang jelas, analisis yang tepat.', 'Periksa kualitas data, susun laporan, dan nilai jawaban AI dengan data yang dapat Anda ubah.')
    with st.expander('Pengaturan data dan batas pembaruan', expanded=True):
        upload = st.file_uploader('Unggah CSV dengan kolom yang sama', type='csv')
        cutoff = st.date_input('Tanggal pembaruan paling lama yang diterima', value=pd.Timestamp('2026-09-24').date())
    try:
        raw = pd.read_csv(upload, keep_default_na=False) if upload is not None else load('shipments.csv')
        result = analyze(raw, cutoff.isoformat())
    except (ValueError, UnicodeError, pd.errors.ParserError) as e:
        st.error('Data tidak dapat diproses: ' + str(e))
        st.stop()
    cols = st.columns(4)
    for c, vals in zip(cols, [('Data awal', f"{result['raw']:,}", 'Jumlah baris sebelum pemeriksaan'), ('Duplikasi berlebih', f"{result['duplicate_excess']:,}", 'Dikeluarkan melalui aturan duplikasi'), ('Pengiriman valid', f"{len(result['clean']):,}", f"{result['coverage']:.1%} dari data tanpa duplikasi"), ('Dikarantina', f"{len(result['quarantine']):,}", 'Memerlukan pemeriksaan pemilik data')]):
        with c:
            metric(*vals)
    tabs = st.tabs(['Ringkasan kualitas', 'Periksa data', 'SQL & definisi'])
    with tabs[0]:
        a, b = st.columns([1, 1.05])
        with a:
            rules = result['rules'].copy()
            rules['Rule'] = rules['Rule'].str.replace('_', ' ').str.title()
            fig = px.bar(rules.sort_values('Records'), x='Records', y='Rule', orientation='h', color_discrete_sequence=['#7160d8'], title='Jumlah pelanggaran per aturan')
            st.plotly_chart(polish(fig, 370), use_container_width=True)
        with b:
            flow = go.Figure(go.Sankey(arrangement='snap', node=dict(label=['Data awal', 'Duplikasi berlebih', 'Tanpa duplikasi', 'Valid', 'Dikarantina'], color=['#9caec9', '#e9ad60', '#b9afef', '#79c2b1', '#d99595'], pad=24, thickness=15), link=dict(source=[0, 0, 2, 2], target=[1, 2, 3, 4], value=[result['duplicate_excess'], result['unique'], len(result['clean']), len(result['quarantine'])], color=['#f4dec1', '#e1ddf7', '#c8e7df', '#edd4d4'])))
            flow.update_layout(title='Alur pemeriksaan data')
            st.plotly_chart(polish(flow, 370), use_container_width=True)
        st.subheader('Laporan cabang dari data valid')
        st.dataframe(result['kpi'], hide_index=True, use_container_width=True, column_config={'fees_idr': st.column_config.NumberColumn('Biaya (Rp)', format='localized'), 'delivered_share': st.column_config.NumberColumn('Proporsi terkirim', format='percent')})
    with tabs[1]:
        selection = st.selectbox('Pilih data', ['Pengiriman valid', 'Data karantina', 'Data awal lengkap'])
        frame = {'Pengiriman valid': result['clean'], 'Data karantina': result['quarantine'], 'Data awal lengkap': raw}[selection]
        st.dataframe(frame, hide_index=True, use_container_width=True, height=380)
        download_frame(frame, 'Unduh tabel ini', selection.lower().replace(' ', '_') + '.csv', 'export_quality')
    with tabs[2]:
        st.markdown('**Kunci pengiriman:** Shipment ID. Gunakan pembaruan valid terbaru; jika sama, pilih Record ID terbesar. Data tanpa kunci dikarantina. Pemeriksaan mencakup cabang, biaya, status, tanggal, urutan pengiriman, dan kebaruan.')
        st.code((ROOT / 'src/quality.sql').read_text(), language='sql')
    summary = {k: result[k] for k in ['raw', 'unique', 'duplicate_excess', 'coverage']}
    summary.update(accepted=len(result['clean']), quarantined=len(result['quarantine']))
    st.download_button('Unduh ringkasan kualitas', json.dumps(summary, indent=2), 'quality_summary.json', 'application/json')
elif page == 'Evaluasi AI':
    hero('RUANG ANALISIS', 'Evaluasi jawaban berdasarkan bukti.', 'Periksa kualitas data, susun laporan, dan nilai jawaban AI dengan data yang dapat Anda ubah.')
    cases = load('evaluation_cases.csv')
    kb = load('knowledge_base.csv')
    runs = st.session_state.setdefault('runs', read_runs(ROOT))
    reviewed = [r for r in runs if r.get('reviewed')]
    cols = st.columns(4)
    accepted = sum((r.get('accepted', False) for r in reviewed))
    for c, vals in zip(cols, [('Kasus uji', str(len(cases)), 'Kategori layanan'), ('Pengembangan / pengujian akhir', str((cases['Split'] == 'Development').sum()) + ' / ' + str((cases['Split'] == 'Held-out').sum()), 'Tetapkan konfigurasi sebelum pengujian akhir'), ('Jawaban tercatat', str(len(runs)), 'Satu jawaban tersimpan per kasus'), ('Jawaban lulus evaluasi', f'{accepted}/{len(reviewed)}' if reviewed else 'Belum dinilai', 'Hanya jawaban yang sudah dinilai')]):
        with c:
            metric(*vals)
    tabs = st.tabs(['Daftar kasus', 'Jalankan model lokal', 'Nilai jawaban', 'Hasil & unduhan'])
    with tabs[0]:
        a, b = st.columns(2)
        with a:
            split = st.selectbox('Kelompok data', ['Semua', 'Development', 'Held-out'])
        with b:
            category = st.selectbox('Kategori layanan', ['Semua'] + sorted(cases['Category'].unique()))
        filtered = cases.copy()
        if split != 'Semua':
            filtered = filtered[filtered['Split'] == split]
        if category != 'Semua':
            filtered = filtered[filtered['Category'] == category]
        st.dataframe(filtered, hide_index=True, use_container_width=True, height=320)
        with st.expander('Basis pengetahuan dan penanggung jawab'):
            st.dataframe(kb, hide_index=True, use_container_width=True)
    with tabs[1]:
        a, b = st.columns([1, 1.2])
        with a:
            st.subheader('Hubungkan Ollama')
            if st.button('Cari model terpasang'):
                try:
                    st.session_state['models'] = models()
                except (OSError, ValueError) as e:
                    st.warning('Ollama belum terhubung di 127.0.0.1:11434. Jalankan Ollama di komputer ini lalu coba lagi.')
            available = st.session_state.get('models', [])
            if available:
                model = st.selectbox('Model terpasang', available)
            else:
                model = st.text_input('Nama model terpasang', placeholder='Gunakan nama pada ollama list')
            caseid = st.selectbox('Pilih kasus uji', cases['Case ID'].tolist())
            case = cases[cases['Case ID'] == caseid].iloc[0]
            frozen = st.checkbox('Konfigurasi model, prompt, dan pengetahuan sudah ditetapkan untuk pengujian akhir', value=False)
            if st.button('Jalankan kasus terpilih', type='primary', disabled=not model or (case['Split'] == 'Held-out' and (not frozen))):
                with st.spinner('Menunggu jawaban model…'):
                    try:
                        record = run_case(case, kb, model)
                    except (OSError, ValueError, KeyError) as e:
                        st.error('Jawaban belum tersimpan. ' + str(e))
                    else:
                        st.session_state['runs'] = [r for r in runs if r['case_id'] != caseid] + [record]
                        st.success('Jawaban tersimpan. Lanjutkan ke tab penilaian.')
                        if 'runs' in st.session_state:
                            save_runs(ROOT, st.session_state['runs'])
                        st.rerun()
        with b:
            st.subheader(case['Question'])
            st.info(case['Reference answer'])
        st.divider()
        with st.expander('Atau tempel jawaban dari chatbot sendiri'):
            with st.form('manual_answer'):
                mid = st.selectbox('ID kasus untuk jawaban', cases['Case ID'].tolist())
                actual = st.text_area('Jawaban chatbot')
                modelname = st.text_input('Versi model / aplikasi')
                timestamp = st.text_input('Waktu pengujian (format ISO)', '')
                if st.form_submit_button('Simpan jawaban'):
                    if not actual.strip() or not modelname.strip() or (not timestamp.strip()):
                        st.error('Isi jawaban, versi, dan waktu pengujian.')
                    else:
                        from datetime import datetime
                        try:
                            datetime.fromisoformat(timestamp)
                        except ValueError:
                            st.error('Gunakan waktu berformat ISO, misalnya 2026-11-02T18:00:00+07:00.')
                        else:
                            c = cases[cases['Case ID'] == mid].iloc[0]
                            record = dict(case_id=mid, split=c['Split'], response=actual, model=modelname, run_at=timestamp, response_type='actual_pasted', reviewed=False, prompt_version='external; document separately')
                            st.session_state['runs'] = [r for r in st.session_state['runs'] if r['case_id'] != mid] + [record]
                            if 'runs' in st.session_state:
                                save_runs(ROOT, st.session_state['runs'])
                            st.rerun()
    with tabs[2]:
        if not runs:
            st.info('Jalankan model lokal atau tempel jawaban chatbot terlebih dahulu, lalu lakukan penilaian.')
        else:
            rid = st.selectbox('Kasus tersimpan', [r['case_id'] for r in runs])
            record = next((r for r in runs if r['case_id'] == rid))
            c = cases[cases['Case ID'] == rid].iloc[0]
            a, b = st.columns(2)
            with a:
                st.markdown('**Jawaban chatbot**')
                st.write(record['response'])
            with b:
                st.markdown('**Jawaban acuan**')
                st.write(c['Reference answer'])
            with st.form('review_' + rid):
                cells = st.columns(4)
                scores = []
                for cell, label in zip(cells, ['Ketepatan', 'Kesesuaian sumber', 'Kelengkapan', 'Eskalasi']):
                    with cell:
                        scores.append(st.selectbox(label, [0, 1, 2], index=None, placeholder='Pilih nilai'))
                privacy = st.selectbox('Lulus privasi', ['Yes', 'No'], index=None)
                reviewer = st.text_input('Nama / ID penilai')
                notes = st.text_area('Catatan / kategori kesalahan')
                if st.form_submit_button('Simpan penilaian'):
                    try:
                        if not reviewer.strip():
                            raise ValueError('Identitas penilai wajib diisi.')
                        scoring = score_review(*scores, privacy)
                    except ValueError as e:
                        st.error(str(e))
                    else:
                        record.update(scoring, reviewed=True, reviewer=reviewer, review_notes=notes, accuracy=scores[0], grounding=scores[1], completeness=scores[2], escalation=scores[3], privacy=privacy)
                        if 'runs' in st.session_state:
                            save_runs(ROOT, st.session_state['runs'])
                        st.rerun()
    with tabs[3]:
        st.markdown('**Catat → nilai → bandingkan.** Hasil tersimpan otomatis. Menjalankan ulang kasus mengganti jawaban dan penilaian sebelumnya. Unduh hasil dahulu jika ingin membandingkan versi.')
        if runs:
            st.dataframe(pd.DataFrame(runs), hide_index=True, use_container_width=True)
            st.download_button('Unduh hasil (JSON)', json.dumps(runs, indent=2, ensure_ascii=False, default=str), 'actual_model_runs.json', 'application/json')
            download_frame(pd.DataFrame(runs), 'Unduh hasil (CSV)', 'actual_model_runs.csv', 'runs_csv')
            summaries = []
            for split in ['Development', 'Held-out']:
                group = [r for r in runs if r['split'] == split]
                rr = [r for r in group if r.get('reviewed')]
                summaries.append(dict(split=split, recorded=len(group), reviewed=len(rr), accepted=sum((r.get('accepted', False) for r in rr)), acceptance_rate=sum((r.get('accepted', False) for r in rr)) / len(rr) if rr else None))
            st.dataframe(pd.DataFrame(summaries), hide_index=True, use_container_width=True)
        else:
            st.info('Belum ada jawaban model yang tersimpan.')
else:
    hero('RUANG ANALISIS', 'Pahami definisi sebelum mengambil keputusan.', 'Periksa kualitas data, susun laporan, dan nilai jawaban AI dengan data yang dapat Anda ubah.')
    tabs = st.tabs(['Kamus data', 'Protokol evaluasi'])
    with tabs[0]:
        st.markdown((ROOT / 'docs/data-dictionary.md').read_text())
    with tabs[1]:
        st.markdown((ROOT / 'docs/evaluation-protocol.md').read_text())
