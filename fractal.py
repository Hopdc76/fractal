import streamlit as st
import uuid

# Cấu hình trang
st.set_page_config(page_title="Checklist Giao Dịch Fractal", layout="wide")

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
            }
            .stButton>button {
                width: 100%;
                border-radius: 5px;
                color: #ffffff;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                opacity: 0.8;
            }
            
            /* Idea Item Styles */
            [data-testid="stVerticalBlock"] {
                border-left: 5px solid transparent;
                background-color: #2a2e39;
                padding: 15px !important;
                border-radius: 8px;
                margin-bottom: 1rem;
            }
            .idea-ticker {
                font-weight: 700;
                font-size: 1.2em;
                color: #fff;
            }
            .idea-htf {
                font-style: italic;
                color: #8a91a0;
                margin: 0 5px;
            }
            .idea-desc {
                font-size: 0.9em;
                color: #e0e3e9;
            }
            .idea-status {
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.8em;
                font-weight: 700;
                color: #131722;
                margin-top: 8px;
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
    st.title("Danh Sách Ý Tưởng Giao Dịch")

    with st.form(key="add_idea_form"):
        col1, col2 = st.columns([1, 3])
        with col1:
            ticker = st.text_input("Mã Giao dịch", placeholder="VD: EURUSD")
            htf = st.text_input("HTF", placeholder="VD: H4")
        with col2:
            description = st.text_area("Mô tả ý tưởng", placeholder="VD: Đảo chiều tăng sau khi quét đáy tuần...")
        
        submitted = st.form_submit_button("Thêm Ý Tưởng")
        if submitted and ticker and htf and description:
            add_idea(ticker, htf, description)
            st.rerun()

    st.markdown("---")
    
    if not st.session_state.ideas:
        st.info("Chưa có ý tưởng nào. Hãy thêm một ý tưởng mới để bắt đầu!")
        return

    # Hiển thị danh sách 2 cột
    cols = st.columns(2)
    for i, idea in enumerate(st.session_state.ideas):
        with cols[i % 2]:
            # Container cho mỗi ý tưởng
            container_html = f"""
                <div class="border-{idea['status']}" style="border-left-width: 5px; border-left-style: solid; background-color: #2a2e39; padding: 15px; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 8px;">
                        <div>
                            <span class="idea-ticker">{idea['ticker'].upper()}</span>
                            <span class="idea-htf">({idea['htf']})</span>
                        </div>
                    </div>
                    <div class="idea-desc" style="margin-bottom: 12px;">- {idea['description']}</div>
                </div>
            """
            st.markdown(container_html, unsafe_allow_html=True)
            
            # Status badge
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
            
            st.markdown(f'<span class="idea-status status-{idea['status']}">{status_text}</span>', unsafe_allow_html=True)

            # Buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Checklist", key=f"check_{idea['id']}"):
                    st.session_state.current_idea_id = idea['id']
                    st.session_state.current_view = 'checklist'
                    st.rerun()
            with btn_col2:
                if st.button("Xóa", key=f"del_{idea['id']}"):
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

    st.title(f"Checklist cho: {idea['ticker'].upper()} ({idea['htf']})")
    st.caption(idea['description'])
    st.markdown("---")
    
    # Hiển thị câu hỏi hoặc kết quả
    if idea['status'] == 'pending':
        question_key = idea['current_question']
        question_text = question_status_map.get(question_key, "").replace("Chờ", "Có tín hiệu") + "?"
        st.subheader(question_text)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Có", key=f"yes_{question_key}"):
                handle_answer(idea['id'], question_key, True)
                st.rerun()
        with col2:
            if st.button("Không", key=f"no_{question_key}"):
                handle_answer(idea['id'], question_key, False)
                st.rerun()

    elif idea['status'] == 'entry':
        st.info("Thiết lập hợp lệ. Ghi nhận kết quả giao dịch:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Thắng (Win)"):
                record_outcome(idea['id'], 'win')
                st.rerun()
        with col2:
            if st.button("Thua (Loss)"):
                record_outcome(idea['id'], 'loss')
                st.rerun()

    elif idea['status'] == 'invalid':
        st.error(f"Không hợp lệ: {idea['result_text']}")
    
    elif idea['status'] == 'win':
        st.success("KẾT QUẢ CUỐI CÙNG: THẮNG (WIN)")
    
    elif idea['status'] == 'loss':
        st.error("KẾT QUẢ CUỐI CÙNG: THUA (LOSS)")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1,1])
    with col_b1:
        if st.button("Quay lại Danh sách"):
            st.session_state.current_view = 'list'
            st.rerun()
    with col_b2:
        if st.button("Reset Ý tưởng này"):
            reset_idea(idea['id'])
            st.rerun()

# --- Main App Logic ---
local_css()

if st.session_state.current_view == 'list':
    render_list_view()
else:
    render_checklist_view()

