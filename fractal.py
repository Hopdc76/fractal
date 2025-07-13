import streamlit as st
import uuid

# Cấu hình trang, đặt ở đầu file
st.set_page_config(page_title="Checklist Giao Dịch Fractal", layout="wide", initial_sidebar_state="collapsed")

# --- CSS Tùy chỉnh để giao diện đẹp hơn ---
def local_css():
    st.markdown("""
        <style>
            /* General Styles */
            .stApp {
                background-color: #131722;
                color: #e0e3e9;
            }
            h1, h2 {
                border-bottom: 2px solid #2962ff;
                padding-bottom: 10px;
                color: #ffffff;
            }
            .stButton>button {
                width: 100%;
                border-radius: 8px;
                color: #ffffff;
                font-weight: bold;
                transition: all 0.3s ease;
                border: 1px solid #4a4a4a;
            }
            .stButton>button:hover {
                opacity: 0.8;
                border-color: #2962ff;
            }
            .stButton>button.primary {
                background-color: #2962ff;
            }
            .stButton>button.secondary {
                background-color: #6c757d;
            }
            
            /* Idea Item Card Styles */
            .idea-card {
                border-left: 5px solid transparent;
                background-color: #1e222d;
                padding: 15px 20px;
                border-radius: 10px;
                margin-bottom: 1rem;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transition: transform 0.2s ease-in-out;
            }
            .idea-card:hover {
                transform: translateY(-3px);
            }

            .idea-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 10px;
            }
            .idea-title {
                font-size: 1.25em;
                font-weight: 700;
                color: #ffffff;
            }
            .idea-htf {
                font-style: italic;
                color: #8a91a0;
                margin-left: 8px;
            }
            .idea-desc {
                font-size: 0.95em;
                color: #b0b3b8;
                margin-bottom: 15px;
            }
            .idea-status {
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 0.8em;
                font-weight: 700;
                color: #ffffff; /* **UPDATED**: Changed to white for better contrast on all backgrounds */
                display: inline-block;
            }
            
            /* Status Colors */
            .status-pending { background-color: #ffca28; }
            .status-entry { background-color: #1e88e5; }
            .status-invalid { background-color: #ef5350; }
            .status-win { background-color: #26a69a; }
            .status-loss { background-color: #ef5350; }
            
            .border-pending { border-left-color: #ffca28; }
            .border-entry { border-left-color: #1e88e5; }
            .border-invalid { border-left-color: #ef5350; }
            .border-win { border-left-color: #26a69a; }
            .border-loss { border-left-color: #ef5350; }

            /* Checklist View Styles */
            .checklist-container {
                max-width: 700px;
                margin: auto;
            }
            .question-box {
                background-color: #2a2e39;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #444;
            }
            .final-result {
                padding: 20px;
                border-radius: 10px;
                font-weight: bold;
                text-align: center;
                font-size: 1.2em;
            }
            /* **UPDATED**: Brighter text colors for final results for better contrast */
            .result-win { background-color: rgba(38, 166, 154, 0.2); border: 1px solid #26a69a; color: #50fa7b;}
            .result-loss { background-color: rgba(239, 83, 80, 0.2); border: 1px solid #ef5350; color: #ff5555;}
            .result-invalid { background-color: rgba(108, 117, 125, 0.2); border: 1px solid #6c757d; color: #b0b3b8;}
            .result-entry { background-color: rgba(30, 136, 229, 0.2); border: 1px solid #1e88e5; color: #80aaff;}

            /* Responsive Grid for Idea List */
            @media (max-width: 768px) {
                .stMultiColumn {
                    grid-template-columns: 1fr !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

# --- Khởi tạo State ---
if 'ideas' not in st.session_state:
    st.session_state.ideas = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'list'
if 'current_idea_id' not in st.session_state:
    st.session_state.current_idea_id = None

# --- Dữ liệu và Logic ---
question_status_map = {
    'htf_c2': 'Chờ HTF Nến 2',
    'ltf_c2': 'Chờ LTF CISD Nến 2',
    'ltf_c3_path_A': 'Chờ LTF CISD Nến 3',
    'htf_c3': 'Chờ HTF Nến 3',
    'ltf_c3_path_B': 'Chờ LTF CISD Nến 3'
}

def get_idea_by_id(idea_id):
    """Tìm một ý tưởng trong state bằng ID."""
    for idea in st.session_state.ideas:
        if idea['id'] == idea_id:
            return idea
    return None

def add_idea(ticker, htf, description):
    """Thêm một ý tưởng mới vào danh sách."""
    new_idea = {
        'id': str(uuid.uuid4()),
        'ticker': ticker,
        'htf': htf,
        'description': description,
        'status': 'pending',
        'current_question': 'htf_c2',
        'answers': {},
        'result_text': ''
    }
    st.session_state.ideas.insert(0, new_idea)

def delete_idea(idea_id):
    """Xóa một ý tưởng khỏi danh sách."""
    st.session_state.ideas = [idea for idea in st.session_state.ideas if idea['id'] != idea_id]

def handle_answer(idea_id, question, answer):
    """Xử lý logic checklist khi người dùng trả lời."""
    idea = get_idea_by_id(idea_id)
    if not idea: return

    idea['answers'][question] = answer
    next_question = None
    
    # Logic Flowchart
    if question == 'htf_c2':
        next_question = 'ltf_c2' if answer else 'htf_c3'
    elif question == 'ltf_c2':
        if answer:
            idea['status'] = 'entry'
        else:
            next_question = 'ltf_c3_path_A'
    elif question == 'ltf_c3_path_A':
        if answer:
            idea['status'] = 'entry'
        else:
            idea['status'] = 'invalid'
            idea['result_text'] = 'Thiếu xác nhận LTF CISD trong Nến 3.'
    elif question == 'htf_c3':
        if answer:
            next_question = 'ltf_c3_path_B'
        else:
            idea['status'] = 'invalid'
            idea['result_text'] = 'Thiếu tín hiệu đóng cửa HTF Nến 3.'
    elif question == 'ltf_c3_path_B':
        if answer:
            idea['status'] = 'entry'
        else:
            idea['status'] = 'invalid'
            idea['result_text'] = 'Thiếu xác nhận LTF CISD trong Nến 3.'
            
    if next_question:
        idea['current_question'] = next_question

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

    with st.expander("Thêm Ý Tưởng Mới", expanded=True):
        with st.form(key="add_idea_form"):
            col1, col2 = st.columns([1, 1])
            with col1:
                ticker = st.text_input("Mã Giao dịch", placeholder="VD: EURUSD")
            with col2:
                htf = st.text_input("HTF", placeholder="VD: H4")
            
            description = st.text_area("Mô tả ý tưởng", placeholder="VD: Đảo chiều tăng sau khi quét đáy tuần...")
            
            submitted = st.form_submit_button("➕ Thêm Ý Tưởng")
            if submitted and ticker and htf and description:
                add_idea(ticker, htf, description)
                st.rerun()

    st.markdown("---")
    
    if not st.session_state.ideas:
        st.info("Chưa có ý tưởng nào. Hãy thêm một ý tưởng mới để bắt đầu!")
        return

    # Hiển thị danh sách 2 cột
    cols = st.columns(2, gap="large")
    for i, idea in enumerate(st.session_state.ideas):
        with cols[i % 2]:
            # Container cho mỗi ý tưởng
            container = st.container()
            
            status_text = ''
            if idea['status'] == 'pending':
                status_text = question_status_map.get(idea['current_question'], 'Đang chờ')
            elif idea['status'] == 'entry':
                status_text = 'Chờ kết quả'
            elif idea['status'] == 'invalid':
                status_text = f"Không hợp lệ: {idea['result_text']}"
            elif idea['status'] == 'win':
                status_text = 'Thắng'
            elif idea['status'] == 'loss':
                status_text = 'Thua'
            
            container.markdown(f"""
            <div class="idea-card border-{idea['status']}">
                <div class="idea-header">
                    <div>
                        <span class="idea-title">{idea['ticker'].upper()}</span>
                        <span class="idea-htf">({idea['htf']})</span>
                    </div>
                </div>
                <div class="idea-desc">{idea['description']}</div>
                <div class="idea-status status-{idea['status']}">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

            # Buttons
            btn_col1, btn_col2 = container.columns(2)
            if btn_col1.button("📝 Checklist", key=f"check_{idea['id']}"):
                st.session_state.current_idea_id = idea['id']
                st.session_state.current_view = 'checklist'
                st.rerun()
            if btn_col2.button("❌ Xóa", key=f"del_{idea['id']}"):
                delete_idea(idea['id'])
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
        st.markdown(f'<div class="checklist-container">', unsafe_allow_html=True)
        
        st.header(f"Checklist: {idea['ticker'].upper()} ({idea['htf']})")
        st.caption(idea['description'])
        st.markdown("---")
        
        # Hiển thị câu hỏi hoặc kết quả
        if idea['status'] == 'pending':
            with st.container():
                st.markdown('<div class="question-box">', unsafe_allow_html=True)
                question_key = idea['current_question']
                question_text = question_status_map.get(question_key, "").replace("Chờ", "Có tín hiệu") + "?"
                st.subheader(question_text)
                
                col1, col2 = st.columns(2)
                if col1.button("✅ Có", key=f"yes_{question_key}"):
                    handle_answer(idea['id'], question_key, True)
                    st.rerun()
                if col2.button("❌ Không", key=f"no_{question_key}"):
                    handle_answer(idea['id'], question_key, False)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        elif idea['status'] == 'entry':
            st.markdown('<div class="final-result result-entry">Thiết lập hợp lệ. Ghi nhận kết quả giao dịch:</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            if col1.button("🏆 Thắng (Win)"):
                record_outcome(idea['id'], 'win')
                st.rerun()
            if col2.button("💔 Thua (Loss)"):
                record_outcome(idea['id'], 'loss')
                st.rerun()

        elif idea['status'] == 'invalid':
            st.markdown(f'<div class="final-result result-invalid">Không hợp lệ: {idea["result_text"]}</div>', unsafe_allow_html=True)
        
        elif idea['status'] == 'win':
            st.markdown('<div class="final-result result-win">KẾT QUẢ CUỐI CÙNG: THẮNG (WIN)</div>', unsafe_allow_html=True)
        
        elif idea['status'] == 'loss':
            st.markdown('<div class="final-result result-loss">KẾT QUẢ CUỐI CÙNG: THUA (LOSS)</div>', unsafe_allow_html=True)

        st.markdown("---")
        col_b1, col_b2 = st.columns([1,1])
        if col_b1.button("◀️ Quay lại Danh sách"):
            st.session_state.current_view = 'list'
            st.rerun()
        if col_b2.button("🔄 Reset Ý tưởng này"):
            reset_idea(idea['id'])
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Logic ---
local_css()

if st.session_state.current_view == 'list':
    render_list_view()
else:
    render_checklist_view()
