import streamlit as st
import json
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="Benchmark Results Viewer", layout="wide")

CSV_PATH = "benchmark_results_1.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    return df


df = load_data()

st.title("Benchmark Results — Overall Summaries")

questions = df["question"].dropna().unique().tolist()

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

col_prev, col_select, col_next = st.columns([1, 6, 1])

with col_prev:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Prev", use_container_width=True, disabled=st.session_state.q_index <= 0):
        st.session_state.q_index -= 1
        st.rerun()

with col_next:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Next →", use_container_width=True, disabled=st.session_state.q_index >= len(questions) - 1):
        st.session_state.q_index += 1
        st.rerun()

with col_select:
    selected_question = st.selectbox(
        "Select a question",
        questions,
        index=st.session_state.q_index,
        key="question_select",
    )
    new_index = questions.index(selected_question)
    if new_index != st.session_state.q_index:
        st.session_state.q_index = new_index
        st.rerun()

filtered = df[df["question"] == selected_question]

for idx, (row_idx, row) in enumerate(filtered.iterrows()):
    answer = row.get("overall_summary", "")
    if pd.isna(answer) or answer == "":
        answer = "*No answer available.*"
    status = row.get("status", "unknown")
    duration = row.get("duration_seconds", None)
    
    header_parts = [f"**Status:** `{status}`"]
    if duration is not None and not pd.isna(duration):
        header_parts.append(f"**Duration:** `{duration:.2f}s`")
    
    # Use request_id if available, otherwise use row index for unique identification
    request_id = row.get("request_id", "")
    if request_id and not pd.isna(request_id):
        feedback_key = f"{request_id}"
    else:
        feedback_key = f"{selected_question}_{row_idx}_{idx}"
    
    with st.expander(
        f"Response {idx + 1}  —  {status}  —  {duration:.1f}s"
        if duration and not pd.isna(duration)
        else f"Response {idx + 1}  —  {status}",
        expanded=(idx == 0),
    ):
        question_text = row.get("question", "") or ""
        if question_text:
            st.subheader(f'*"{question_text}"*')
        
        st.markdown(answer)
        
        st.divider()
        st.markdown("### Feedback")
        
        current_feedback = st.session_state.feedback.get(feedback_key, {})
        
        st.markdown("**Completeness:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Complete", key=f"complete_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("completeness") == "complete" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["completeness"] = "complete"
        with col2:
            if st.button("⚠️ Partially Complete", key=f"partial_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("completeness") == "partially_complete" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["completeness"] = "partially_complete"
        with col3:
            if st.button("❌ Incomplete", key=f"incomplete_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("completeness") == "incomplete" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["completeness"] = "incomplete"
        
        st.markdown("**Correctness:**")
        col4, col5, col6 = st.columns(3)
        with col4:
            if st.button("✅ Correct", key=f"correct_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("correctness") == "correct" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["correctness"] = "correct"
        with col5:
            if st.button("⚠️ Mostly Correct", key=f"mostly_correct_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("correctness") == "mostly_correct" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["correctness"] = "mostly_correct"
        with col6:
            if st.button("❌ Incorrect", key=f"incorrect_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("correctness") == "incorrect" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["correctness"] = "incorrect"
        
        st.markdown("**Satisfaction/Desirability:**")
        col7, col8, col9 = st.columns(3)
        with col7:
            if st.button("😀 Very Satisfying", key=f"very_satisfying_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("satisfaction") == "very_satisfying" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["satisfaction"] = "very_satisfying"
        with col8:
            if st.button("😐 Somewhat Satisfying", key=f"somewhat_satisfying_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("satisfaction") == "somewhat_satisfying" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["satisfaction"] = "somewhat_satisfying"
        with col9:
            if st.button("😞 Not Satisfying", key=f"not_satisfying_{feedback_key}", use_container_width=True, type="primary" if current_feedback.get("satisfaction") == "not_satisfying" else "secondary"):
                st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
                st.session_state.feedback[feedback_key]["satisfaction"] = "not_satisfying"
        
        comments = st.text_area(
            "Additional comments (optional):",
            value=current_feedback.get("comments", ""),
            key=f"comments_{feedback_key}",
            placeholder="Add any additional feedback or observations..."
        )
        
        if comments != current_feedback.get("comments", ""):
            st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
            st.session_state.feedback[feedback_key]["comments"] = comments
    
    # Research process section - OUTSIDE the expander
    captured_sse_events = row.get("captured_sse_events", "")
    if captured_sse_events and not pd.isna(captured_sse_events):
        try:
            import ast
            events = ast.literal_eval(captured_sse_events) if isinstance(captured_sse_events, str) else captured_sse_events
            
            if isinstance(events, dict):
                search_llm_messages = events.get('search_llm_message', [])
                test_source_debug = events.get('test_source_debug', [])
                    
                # Display each search LLM message with related sources
                for step_idx, step in enumerate(search_llm_messages):
                    phase = step.get('payload', {}).get('phase', 'unknown')
                    text = step.get('payload', {}).get('text', '')
                    timestamp = step.get('timestamp', 'N/A')
                    
                    # Phase container
                    with st.container(border=True):
                        st.subheader(f"Phase {step_idx + 1}: {phase.replace('_', ' ').title()}")
                        if timestamp != 'N/A':
                            dt = datetime.fromtimestamp(timestamp)
                        
                        # LLM Message
                        st.write("**LLM Strategy:**")
                        st.info(f'"{text}"')
                        
                        # Find matching debug events for this phase
                        matching_events = [e for e in test_source_debug if e.get('payload', {}).get('phase') == phase]
                        
                        if matching_events:
                            st.write("**Tools & Sources:**")
                            
                            for event_idx, event in enumerate(matching_events):
                                payload = event.get('payload', {})
                                if 'tool' in payload:
                                    tool = payload['tool']
                                else:
                                    continue
                                source_count = payload.get('source_count', 0)
                                snapshot_kind = payload.get('snapshot_kind', '')
                                
                                # Tool container (indented using empty column)
                                tool_indent, tool_content = st.columns([0.05, 0.95])
                                with tool_content:
                                    with st.container(border=True):
                                        if tool:
                                            st.write(f"🔧 **Tool:** `{tool}` ({source_count} sources)")
                                        sources = payload.get('sources', [])
                                        if sources:
                                            if st.checkbox(f"Show Retrieved Sources ({len(sources)})", key=f"show_sources_{feedback_key}_{step_idx}_{event_idx}", value=False):
                                                for i, source in enumerate(sources):
                                                    title = source.get('title', '')
                                                    text_content = source.get('text', '')
                                                    if 'url' in source:
                                                        url = source['url']
                                                    else:
                                                        doc_id = None
                                                        if 'doc_id' in source:
                                                            if source['doc_id'].startswith('CRE-'):
                                                                doc_id = source['doc_id']
                                                            else:
                                                                doc_id = re.sub(r'\(\d{4}\)', '', source['doc_id']).replace('_', '-')
                                                                # Insert hyphen between last alpha char and first numeric char
                                                                doc_id = re.sub(r'([A-Za-z])(\d)', r'\1-\2', doc_id)
                                                                if doc_id.startswith('A') or doc_id.startswith('B'):
                                                                    parts = doc_id.split('-')
                                                                    doc_id = "-".join(parts[:2]) + f"-{parts[3]}-{parts[2]}"
                                                        if doc_id:
                                                            url = f'https://www.europarl.europa.eu/doceo/document/{doc_id}_EN.html'
                                                        else:
                                                            url = None
                                                    chunk_id = source.get('chunk_id', '')
                                                    
                                                    source_name = title or chunk_id or f"Source {i+1}"
                                                    if url:
                                                        st.markdown(f"- [{source_name}]({url})")
                                                    else:
                                                        st.markdown(f"- {source_name}")
                                                        if text_content:
                                                            # Try to parse as JSON and pretty-print
                                                            try:
                                                                parsed_json = json.loads(text_content)
                                                                st.json(parsed_json)
                                                            except (json.JSONDecodeError, TypeError):
                                                                # Not JSON, display as text with proper UTF-8 encoding
                                                                st.text(text_content)
                        
                    st.write("")
            else:
                st.json(events)
        except (json.JSONDecodeError, Exception) as e:
            st.error(f"Unable to parse SSE events: {e}")
            st.text(str(captured_sse_events)[:1000])
    
    st.write("")
    st.write("")

# Download feedback section
st.divider()
if st.session_state.feedback:
    st.subheader("📥 Download Your Annotations")
    
    total_annotations = len(st.session_state.feedback)
    complete_annotations = sum(1 for f in st.session_state.feedback.values() 
                                if f.get("completeness") and f.get("correctness") and f.get("satisfaction"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Responses Annotated", total_annotations)
    with col2:
        st.metric("Fully Annotated", complete_annotations)
    
    # Prepare the feedback data with metadata
    export_data = {
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "total_annotations": total_annotations,
            "fully_annotated": complete_annotations,
            "csv_file": CSV_PATH
        },
        "annotations": st.session_state.feedback
    }
    
    feedback_json = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📥 Download Annotations as JSON",
        data=feedback_json,
        file_name=f"benchmark_annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
        help="Download your feedback and annotations to share with the team"
    )
    
    st.info("💡 After downloading, you can share this file via email or upload it to a shared folder.")
else:
    st.info("No annotations yet. Rate some responses to enable downloading your feedback.")

