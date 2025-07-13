import streamlit as st
import uuid

# Cấu hình trang, đặt ở đầu file
st.set_page_config(page_title="Checklist Giao Dịch Fractal", layout="wide", initial_sidebar_state="collapsed")

# --- CSS Tùy chỉnh để giao diện đẹp hơn ---
def local_css():
    st.markdown("""
        <style>
            /* --- THEME & GENERAL STYLES --- */
            :root {
                --bg-color: #f8f9fa; /* Light grey background for less glare */
                --surface-color: #ffffff; /* White for cards and inputs */
                --primary-color: #007bff; /* A more standard blue for primary actions */
                --primary-color-dark: #0056b3;
                --text-color: #212529;
                --text-secondary-color: #6c757d;
                --green-color: #28a745;
                --red-color: #dc3545;
                --yellow-color: #ffc107;
                --border-color: #dee2e6;
            }

            .stApp {
                background-color: var(--bg-color);
                color: var(--text-color);
            }
            h1, h2 {
                color: var(--text-color) !important;
                border-bottom: 2px solid var(--border-color);
                padding-bottom: 10px;
            }
            .stTextInput>div>div>input, .stTextArea>textarea {
                background-color: var(--surface-color);
                color: var(--text-color);
                border: 1px solid var(--border-color);
                border-radius: 8px;
            }
            .stTextInput>div>div>input:focus, .stTextArea>textarea:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }

            /* --- GÓP Ý: Cải thiện UI/UX cho các nút bấm --- */
            .stButton>button {
                width: 100%;
                border-radius: 8px;
                font-weight: bold;
                transition: all 0.2s ease;
                border: 1px solid var(--border-color);
                background-color: var(--surface-color);
                color: var(--text-color);
            }
            .stButton>button:hover {
                border-color: var(--text-color);
                background-color: #e9ecef;
            }
            /* Nút hành động chính (Thêm, Có) */
            .stButton>button.primary {
                background-color: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }
            .stButton>button.primary:hover {
                background-color: var(--primary-color-dark);
                border-color: var(--primary-color-dark);
            }
            /* Nút hành động nguy hiểm (Xóa, Không) */
            .stButton>button.destructive {
                background-color: transparent;
                color: var(--red-color);
                border-color: var(--border-color);
            }
            .stButton>button.destructive:hover {
                background-color: var(--red-color);
                color: white;
                border-color: var(--red-color);
            }

            /* --- Idea Item Card Styles --- */
            .idea-card {
                border-left: 5px solid transparent;
                background-color: var(--surface-color);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 1rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.07);
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                display: flex;
                flex-direction: column;
                height: 100%; /* Make cards in a row equal height */
            }
            .idea-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            }
            .idea-content {
                flex-grow: 1; /* Allows content to push footer down */
            }
            .idea-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 10px;
            }
            .idea-title {
                font-size: 1.3em;
                font-weight: 700;
                color: var(--text-color);
            }
            .idea-htf {
                font-style: italic;
                color: var(--text-secondary-color);
                margin-left: 8px;
            }
            .idea-desc {
                font-size: 1em;
                color: var(--text-secondary-color);
                margin-bottom: 15px;
            }
            .idea-status {
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 0.85em;
                font-weight: 700;
                color: #ffffff;
                display: inline-block;
                margin-top: auto; /* Pushes status to the bottom of its container */
            }
            
            /* Status Colors */
            .status-pending { background-color: var(--yellow-color); color: #212529; }
            .status-entry { background-color: var(--primary-color); }
            .status-invalid { background-color: var(--text-secondary-color); }
            .status-win { background-color: var(--green-color); }
            .status-loss { background-color: var(--red-color); }
            
            .border-pending { border-left-color: var(--yellow-color); }
            .border-entry { border-left-color: var(--primary-color); }
            .border-invalid { border-left-color: var(--text-secondary-color); }
            .border-win { border-left-color: var(--green-color); }
            .border-loss { border-left-color: var(--red-color); }

            /* Checklist View Styles */
            .checklist-container {
                max-width: 700px;
                margin: auto;
                background-color: var(--surface-color);
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.07);
            }
            .final-result {
                padding: 20px;
                border-radius: 10px;
                font-weight: bold;
                text-align: center;
                font-size: 1.2em;
            }
            .result-win { background-color: rgba(40, 167, 69, 0.1); border: 1px solid var(--green-color); color: var(--green-color);}
            .result-loss { background-color: rgba(220, 53, 69, 0.1); border: 1px solid var(--red-color); color: var(--red-color);}
            .result-invalid { background-color: rgba(108, 117, 125, 0.1); border: 1px solid var(--text-secondary-color); color: var(--text-secondary-color);}
            .result-entry { background-color: rgba(0, 123, 255, 0.1); border: 1px solid var(--primary-color); color: var(--primary-color);}

        </style>
    """, unsafe_allow_html=True)

# --- Khởi tạo State ---
if 'ideas' not in st.session_state:
    st.session_state.ideas = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'list'
if 'current_idea_id' not in st.session_state:
    st.session_state.current_idea_id = None
# GÓP Ý: Thêm state để quản lý việc xác nhận xóa
if 'confirming_delete' not in st.session_state:
    st.session_state.confirming_delete = None

# --- GÓP Ý: Cấu trúc lại Logic Checklist thành dạng dữ liệu ---
# Điều này giúp bạn dễ dàng thêm, bớt hoặc thay đổi các bước mà không cần sửa hàm handle_answer
CHECKLIST_FLOW = {
    'htf_c2': {
        'text': 'Có tín hiệu HTF Nến 2?',
        'on_yes': 'ltf_c2',
        'on_no': 'htf_c3'
    },
    'ltf_c2': {
        'text': 'Có tín hiệu LTF CISD trong Nến 2?',
        'on_yes': 'STATUS_ENTRY',
        'on_no': 'ltf_c3_path_A'
    },
    'ltf_c3_path_A': {
        'text': 'Có tín hiệu LTF CISD trong Nến 3?',
        'on_yes': 'STATUS_ENTRY',
        'on_no': ('STATUS_INVALID', 'Thiếu xác nhận LTF CISD trong Nến 3.')
    },
    'htf_c3': {
        'text': 'Có tín hiệu HTF Nến 3?',
        'on_yes': 'ltf_c3_path_B',
        'on_no': ('STATUS_INVALID', 'Thiếu tín hiệu đóng cửa HTF Nến 3.')
    },
    'ltf_c3_path_B': {
        'text': 'Có tín hiệu LTF CISD trong Nến 3?',
        'on_yes': 'STATUS_ENTRY',
        'on_no': ('STATUS_INVALID', 'Thiếu xác nhận LTF CISD trong Nến 3.')
    }
}

STATUS_MAP = {
    'pending': 'Đang chờ',
    'entry': 'Chờ kết quả',
    'invalid': 'Không hợp lệ',
    'win': 'Thắng',
    'loss': 'Thua'
}

def get_idea_by_id(idea_id):
    """Tìm một ý tưởng trong state bằng ID."""
    return next((idea for idea in st.session_state.ideas if idea['id'] == idea_id), None)

def add_idea(ticker, htf, description):
    """Thêm một ý tưởng mới vào danh sách."""
    new_idea = {
        'id': str(uuid.uuid4()),
        'ticker': ticker,
        'htf': htf,
        'description': description,
        'status': 'pending',
        'current_question': 'htf_c2', # Điểm bắt đầu của checklist
        'answers': {},
        'result_text': ''
    }
    st.session_state.ideas.insert(0, new_idea)
    st.session_state.confirming_delete = None # Reset trạng thái xóa

def delete_idea(idea_id):
    """Xóa một ý tưởng khỏi danh sách."""
    st.session_state.ideas = [idea for idea in st.session_state.ideas if idea['id'] != idea_id]
    st.session_state.confirming_delete = None # Reset trạng thái xóa

def handle_answer(idea_id, answer):
    """Xử lý logic checklist khi người dùng trả lời (phiên bản cải tiến)."""
    idea = get_idea_by_id(idea_id)
    if not idea: return

    current_question_key = idea['current_question']
    idea['answers'][current_question_key] = answer
    
    flow_step = CHECKLIST_FLOW.get(current_question_key)
    if not flow_step: return

    next_step = flow_step['on_yes'] if answer else flow_step['on_no']
    
    if isinstance(next_step, tuple): # (STATUS_INVALID, "Lý do...")
        status, reason = next_step
        idea['status'] = status.replace('STATUS_', '').lower()
        idea['result_text'] = reason
        idea['current_question'] = None
    elif 'STATUS_' in next_step: # STATUS_ENTRY
        idea['status'] = next_step.replace('STATUS_', '').lower()
        idea['current_question'] = None
    else: # Chuyển sang câu hỏi tiếp theo
        idea['current_question'] = next_step

def record_outcome(idea_id, outcome):
    """Ghi nhận kết quả Win/Loss."""
    idea = get_idea_by_id(idea_id)
    if idea:
        idea['status'] = outcome

def reset_idea(idea_id):
    """Reset một ý tưởng về trạng thái ban đầu."""
    idea = get_idea_by_id(idea_id)
    if idea:
        idea['status'] = 'pending'
        idea['current_question'] = 'htf_c2'
        idea['answers'] = {}
        idea['result_text'] = ''

# --- Giao diện (Views) ---

def render_list_view():
    """Hiển thị giao diện danh sách các ý tưởng."""
    st.title("Checklist Giao Dịch Fractal")

    with st.expander("Thêm Ý Tưởng Mới", expanded=not st.session_state.ideas):
        with st.form(key="add_idea_form"):
            col1, col2 = st.columns([1, 1])
            ticker = col1.text_input("Mã Giao dịch", placeholder="VD: EURUSD")
            htf = col2.text_input("HTF", placeholder="VD: H4")
            description = st.text_area("Mô tả ý tưởng", placeholder="VD: Đảo chiều tăng sau khi quét đáy tuần...")
            
            submitted = st.form_submit_button("➕ Thêm Ý Tưởng")
            if submitted and ticker and htf and description:
                add_idea(ticker, htf, description)
                # GÓP Ý: Thêm phản hồi cho người dùng
                st.success(f"Đã thêm ý tưởng cho **{ticker.upper()}**!")
                st.rerun()

    st.markdown("---")
    
    if not st.session_state.ideas:
        st.info("Chưa có ý tưởng nào. Hãy thêm một ý tưởng mới để bắt đầu!")
        return

    cols = st.columns(2)
    for i, idea in enumerate(st.session_state.ideas):
        col = cols[i % 2]
        
        # Container cho mỗi ý tưởng
        with col.container():
            status_text = STATUS_MAP.get(idea['status'], 'Không rõ')
            if idea['status'] == 'pending':
                question_info = CHECKLIST_FLOW.get(idea['current_question'])
                status_text = f"Chờ: {question_info['text']}" if question_info else "Đang chờ"
            elif idea['status'] == 'invalid':
                status_text = f"Không hợp lệ: {idea['result_text']}"
            
            st.markdown(f"""
            <div class="idea-card border-{idea['status']}">
                <div class="idea-content">
                    <div class="idea-header">
                        <div>
                            <span class="idea-title">{idea['ticker'].upper()}</span>
                            <span class="idea-htf">({idea['htf']})</span>
                        </div>
                    </div>
                    <p class="idea-desc">{idea['description']}</p>
                </div>
                <div class="idea-status status-{idea['status']}">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

            # GÓP Ý: Logic nút bấm và xác nhận xóa
            if st.session_state.confirming_delete == idea['id']:
                st.warning(f"Bạn có chắc muốn xóa ý tưởng **{idea['ticker'].upper()}** không?")
                btn_col1, btn_col2 = st.columns(2)
                if btn_col1.button("✅ Xác nhận xóa", key=f"confirm_del_{idea['id']}", type="primary"):
                    delete_idea(idea['id'])
                    st.rerun()
                if btn_col2.button("Hủy", key=f"cancel_del_{idea['id']}"):
                    st.session_state.confirming_delete = None
                    st.rerun()
            else:
                btn_col1, btn_col2 = st.columns(2)
                if btn_col1.button("📝 Checklist", key=f"check_{idea['id']}"):
                    st.session_state.current_idea_id = idea['id']
                    st.session_state.current_view = 'checklist'
                    st.rerun()
                if btn_col2.button("❌ Xóa", key=f"del_{idea['id']}"):
                    st.session_state.confirming_delete = idea['id']
                    st.rerun()

def render_checklist_view():
    """Hiển thị giao diện checklist chi tiết."""
    idea = get_idea_by_id(st.session_state.current_idea_id)
    if not idea:
        st.error("Không tìm thấy ý tưởng. Đang quay lại danh sách.")
        st.session_state.current_view = 'list'
        st.rerun()
        return
    
    with st.container():
        st.markdown('<div class="checklist-container">', unsafe_allow_html=True)
        
        st.header(f"Checklist: {idea['ticker'].upper()} ({idea['htf']})")
        st.caption(idea['description'])
        st.markdown("---")
        
        if idea['status'] == 'pending':
            question_key = idea['current_question']
            question_text = CHECKLIST_FLOW.get(question_key, {}).get('text', 'Câu hỏi không xác định')
            st.subheader(question_text)
            
            col1, col2 = st.columns(2)
            if col1.button("✅ Có", key=f"yes_{question_key}", type="primary"):
                handle_answer(idea['id'], True)
                st.rerun()
            if col2.button("❌ Không", key=f"no_{question_key}", type="secondary"):
                handle_answer(idea['id'], False)
                st.rerun()

        elif idea['status'] == 'entry':
            st.markdown('<div class="final-result result-entry">Thiết lập hợp lệ. Ghi nhận kết quả giao dịch:</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            if col1.button("🏆 Thắng (Win)", type="primary"):
                record_outcome(idea['id'], 'win')
                st.rerun()
            if col2.button("💔 Thua (Loss)", type="secondary"):
                record_outcome(idea['id'], 'loss')
                st.rerun()

        elif idea['status'] == 'invalid':
            st.markdown(f'<div class="final-result result-invalid">Không hợp lệ: {idea["result_text"]}</div>', unsafe_allow_html=True)
        
        elif idea['status'] == 'win':
            st.markdown('<div class="final-result result-win">KẾT QUẢ CUỐI CÙNG: THẮNG (WIN)</div>', unsafe_allow_html=True)
        
        elif idea['status'] == 'loss':
            st.markdown('<div class="final-result result-loss">KẾT QUẢ CUỐI CÙNG: THUA (LOSS)</div>', unsafe_allow_html=True)

        st.markdown("---", help="Hành động")
        col_b1, col_b2 = st.columns([1,1])
        if col_b1.button("◀️ Quay lại Danh sách"):
            st.session_state.current_view = 'list'
            st.session_state.confirming_delete = None # Reset khi rời trang
            st.rerun()
        if col_b2.button("🔄 Reset Ý tưởng này"):
            reset_idea(idea['id'])
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Logic ---
local_css()

# GÓP Ý: Thay đổi nhỏ trong cách gọi nút bấm để áp dụng style
# Streamlit không cho phép thêm class trực tiếp, nhưng ta có thể dùng `type="primary"`
# hoặc `type="secondary"` và tùy chỉnh nó. Tuy nhiên, cách tiếp cận trong CSS
# ở trên là tổng quát hơn. Để có các nút chuyên dụng (primary, destructive),
# chúng ta phải dùng st.markdown để tạo nút HTML, nhưng điều đó phức tạp hơn.
# Phiên bản này giữ `st.button` và cải thiện CSS chung.
# Để có hiệu ứng nút `primary` và `destructive` rõ ràng hơn, bạn có thể
# dùng `st.button("Tên nút", type="primary")` cho các hành động chính.

if st.session_state.current_view == 'list':
    render_list_view()
else:
    render_checklist_view()
