import streamlit as st
import json
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="Benchmark Results Viewer", layout="wide")

CSV_PATH = "benchmark_results_3.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    return df


df = load_data()

st.title("Benchmark Results — Overall Summaries")

# Add expandable instructions section at the top
with st.expander("📖 Evaluation Instructions - Click to expand", expanded=False):
    st.markdown("""
    ## Evaluation Guidelines

    Rate each response on **five independent dimensions** using a 5-point scale. 
    Each dimension should be rated without reference to the others.

    ---

    ### 1. Correctness
    Is the factual content of the answer accurate, based on your own knowledge?

    This dimension does not ask whether claims are supported by the cited sources (→ Faithfulness), 
    or whether the answer is complete (→ Completeness).

    - **5** — Every verifiable claim is accurate. No errors found.
    - **4** — One or two minor generalisations or inferences that do not materially affect the meaning.
    - **3** — Some errors present, but the main substance of the answer remains accurate.
    - **2** — At least one significant factual error that would mislead a user acting on this information.
    - **1** — Major factual errors, fabricated information, or fundamentally misleading content.

    ---

    ### 2. Completeness
    Does the answer address all aspects of the question that was asked?

    Rate against the question as asked, not against what you think should have been asked.
    This dimension does not ask whether the answer is accurate (→ Correctness) or 
    well-presented (→ Desirability).

    For questions with many valid answers (e.g. "who are the Vice Presidents of the Bureau?" 
    where there are 14), completeness should be judged proportionally. An answer that provides 
    most of the expected items is not a failure — judge whether the coverage is reasonable 
    given the question.

    - **5** — Every distinct part of the question is addressed. Nothing asked for is omitted.
    - **4** — All main parts addressed; at most one minor detail missing.
    - **3** — The central question is answered but at least one secondary aspect is omitted.
    - **2** — The answer addresses part of the question but leaves out at least one substantive component.
    - **1** — The answer fails to address most or all of what was asked.

    ---

    ### 3. Satisfaction
    How satifying is the answer, independent of its accuracy or completeness?

    A factually perfect but poorly structured answer can score low here. Some questions 
    may be unanswerable by the system in a given moment — due to retrieval failure, 
    a gap in the index, or a system limitation — even if they are in principle answerable. 
    A response that clearly explains the situation and guides the user appropriately can 
    still score high here.

    - **5** — Clear, well-structured, appropriately concise, easy to act on.
    - **4** — Good presentation with only minor issues (e.g. slightly verbose, minor structural awkwardness).
    - **3** — Adequate. Gets the information across but requires some effort to read or parse.
    - **2** — Presentation notably hinders usability — e.g. disorganised, key information buried, very disjoint or confusing.
    - **1** — Very unsatisfying. Incoherent, or so verbose that useful content is obscured. Unclear or inconsistent about limitations or scope.

    ---

    ### 4. Faithfulness
    Are the claims in the answer directly supported by the cited sources?

    This dimension does not ask whether claims are factually true in the world (→ Correctness), 
    or whether the right sources were retrieved (→ Source Appropriateness). Focus only on 
    whether what the answer says is consistent with what the cited sources actually say.
    Out-of-date information is not a faithfulness failure — if the answer accurately reflects 
    its sources, Faithfulness should be rated highly regardless of whether those sources 
    are current.

    - **5** — Every claim is directly traceable to a cited source. No unsupported assertions.
    - **4** — Nearly all claims are grounded. At most one minor reasonable inference beyond the source.
    - **3** — Most claims are grounded but the answer includes at least one inference not directly supported.
    - **2** — A substantial portion of the answer is not supported by sources, or a claim misrepresents a source.
    - **1** — Major claims contradict sources, or most content appears to be hallucinated.

    ---

    ### 5. Source Appropriateness
    Are the retrieved and cited sources relevant to the question?

    Assess the sources independently of the answer quality — you are evaluating retrieval, 
    not generation. Ask: given this question, would a reasonable person reach for these sources?

    For questions involving contested or politically sensitive topics, also consider whether 
    the sources represent a reasonable range of perspectives. Sources that are individually 
    relevant but collectively one-sided — covering only one political group, nationality, 
    or position — should be penalised here even if each source is on-topic.

    - **5** — All cited sources are directly relevant. No clearly missing sources.
    - **4** — Sources are relevant; at most one tangential source or one obvious gap.
    - **3** — Sources are generally on-topic but include tangential material, or an important source type is absent.
    - **2** — Several sources are only loosely related, or a primary source is clearly missing.
    - **1** — Sources are largely irrelevant, or no sources are provided where they should be.

    ---

    ## Examples

    These examples illustrate cases where scores diverge across dimensions. 
    Use them to calibrate your judgements before rating.

    **A response can score highly on Faithfulness while failing on Correctness.**
    For example: the system accurately summarises sources that are now out of date. 
    The answer reflects the sources correctly, but the underlying information has since changed. 
    Faithfulness should not be penalised — the failure is in the age of the retrieved sources.

    **A response can score highly on Correctness while failing on Completeness.**
    For example: the answer addresses one part of a multi-part question accurately and well. 
    The remaining parts are not addressed at all. Do not let the quality of what is present 
    inflate your assessment of what is missing.

    **A response can score highly on Correctness while failing on Faithfulness and Source Appropriateness.**
    For example: the answer is factually accurate, but the cited sources do not actually support 
    the claims made. The system may have generated from background knowledge rather than 
    retrieved evidence. The answer being correct does not make the sources appropriate.

    **A response can score highly on Desirability while failing on Completeness.**
    For example: the system cannot find relevant sources and clearly says so, explaining what 
    it does and does not have access to. This is a well-handled non-answer. 
    Do not penalise Desirability because the system could not answer — reserve low scores 
    for responses that are confusing or unhelpful in how they handle the situation.

    **A response can score highly on all dimensions except Desirability.**
    For example: the answer is accurate, complete, grounded in appropriate sources, and 
    faithful to them — but it presents the information as a dense wall of text with no 
    structure, buries the most relevant detail at the end, and includes substantial 
    repetition. The content is sound; the presentation makes it difficult to use.
    """)

questions = df["question"].dropna().unique().tolist()

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

col_prev, col_select, col_next = st.columns([1, 6, 1])

with col_prev:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Prev", key="prev_btn", use_container_width=True, disabled=st.session_state.q_index <= 0):
        st.session_state.q_index -= 1
        st.rerun()

with col_next:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Next →", key="next_btn", use_container_width=True, disabled=st.session_state.q_index >= len(questions) - 1):
        st.session_state.q_index += 1
        st.rerun()

with col_select:
    selected_question = st.selectbox(
        "Select a question",
        questions,
        index=st.session_state.q_index,
    )
    # Only update q_index if the selectbox value actually changed from user interaction
    current_question_from_index = questions[st.session_state.q_index]
    if selected_question != current_question_from_index:
        new_index = questions.index(selected_question)
        st.session_state.q_index = new_index

filtered = df[df["question"] == questions[st.session_state.q_index]]

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
        
        # Create two columns: answer on left, citations on right
        col_answer, col_citations = st.columns([2, 1])
        
        with col_answer:
            st.markdown(answer)
        
        with col_citations:
            # Display citations if available
            citations = row.get("overall_summary_citations", "")
            if citations and not pd.isna(citations):
                try:
                    import ast
                    # Parse citations (Python format with single quotes)
                    if isinstance(citations, str):
                        parsed_citations = ast.literal_eval(citations)
                    else:
                        parsed_citations = citations
                    
                    if parsed_citations and isinstance(parsed_citations, list):
                        st.markdown("**Sources cited:**")
                        
                        # Add custom CSS to wrap text
                        st.markdown("""
                        <style>
                        .stMarkdown p {
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Parse SSE events to get source mapping
                        captured_sse_events = row.get("captured_sse_events", "")
                        source_map = {}
                        if captured_sse_events and not pd.isna(captured_sse_events):
                            try:
                                events = ast.literal_eval(captured_sse_events) if isinstance(captured_sse_events, str) else captured_sse_events
                                if isinstance(events, dict):
                                    test_source_debug = events.get('test_source_debug', [])
                                    for event in test_source_debug:
                                        sources = event.get('payload', {}).get('sources', [])
                                        for source in sources:
                                            chunk_id = source.get('chunk_id', '')
                                            if chunk_id:
                                                source_map[chunk_id] = source
                            except:
                                pass
                        
                        for citation in parsed_citations:
                            ref_num = citation.get('reference_number', '')
                            title = citation.get('citation_title', '')
                            url = citation.get('url', '')
                            chunk_id = citation.get('chunk_id', '')
                            
                            # Get source details from source_map if available
                            source_details = source_map.get(chunk_id, {})
                            source_title = source_details.get('title', title)
                            source_url = source_details.get('url', url)
                            
                            # Create citation display
                            if source_url:
                                st.markdown(f"[{ref_num}] [{source_title or chunk_id}]({source_url})")
                            else:
                                # Show text content inline with title
                                text_content = source_details.get('text', '')
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"[{ref_num}] {source_title or chunk_id or 'Source'}")
                                with col2:
                                    if text_content:
                                        show_content = st.checkbox("View", key=f"show_citation_{feedback_key}_{ref_num}", value=False)
                                
                                if text_content and show_content:
                                    # Display text content
                                    try:
                                        parsed_json = json.loads(text_content)
                                        st.json(parsed_json)
                                    except (json.JSONDecodeError, TypeError):
                                        # Display as wrapped text in a styled container
                                        st.markdown(f"""
                                        <div style="
                                            padding: 10px;
                                            background-color: #f0f2f6;
                                            border-radius: 5px;
                                            font-size: 0.85em;
                                            max-height: 300px;
                                            overflow-y: auto;
                                            white-space: pre-wrap;
                                            word-wrap: break-word;
                                        ">
                                        {text_content}
                                        </div>
                                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.caption(f"Citations error: {str(e)}")
        
        st.divider()
        st.markdown("### Feedback")
        
        current_feedback = st.session_state.feedback.get(feedback_key, {})
        
        # 1. Correctness - 5-point Likert scale
        st.markdown("**Correctness:** *Is the provided information accurate and up to date?*")
        st.caption("1 = Not at all correct  |  5 = Correct")
        correctness = st.radio(
            "Correctness rating",
            options=[1, 2, 3, 4, 5],
            index=[1, 2, 3, 4, 5].index(current_feedback.get("correctness")) if current_feedback.get("correctness") in [1, 2, 3, 4, 5] else None,
            key=f"correctness_{feedback_key}",
            horizontal=True,
            label_visibility="collapsed"
        )
        if correctness:
            st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
            st.session_state.feedback[feedback_key]["correctness"] = correctness
        
        # 2. Completeness - 5-point Likert scale
        st.markdown("**Completeness:** *Does the answer address all aspects of the question?*")
        st.caption("1 = Not at all complete  |  5 = Complete")
        completeness = st.radio(
            "Completeness rating",
            options=[1, 2, 3, 4, 5],
            index=[1, 2, 3, 4, 5].index(current_feedback.get("completeness")) if current_feedback.get("completeness") in [1, 2, 3, 4, 5] else None,
            key=f"completeness_{feedback_key}",
            horizontal=True,
            label_visibility="collapsed"
        )
        if completeness:
            st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
            st.session_state.feedback[feedback_key]["completeness"] = completeness
        
        # 3. Satisfaction - 5-point Likert scale
        st.markdown("**Satisfaction/Desirability:** *How satisfying is the answer?*")
        st.caption("1 = Not at all satisfying  |  5 = Satisfying")
        satisfaction = st.radio(
            "Satisfaction rating",
            options=[1, 2, 3, 4, 5],
            index=[1, 2, 3, 4, 5].index(current_feedback.get("satisfaction")) if current_feedback.get("satisfaction") in [1, 2, 3, 4, 5] else None,
            key=f"satisfaction_{feedback_key}",
            horizontal=True,
            label_visibility="collapsed"
        )
        if satisfaction:
            st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
            st.session_state.feedback[feedback_key]["satisfaction"] = satisfaction
        
        # 4. Faithfulness - 5-point Likert scale
        st.markdown("**Faithfulness:** *Is the information in the answer consistent with the source material?*")
        st.caption("1 = Not at all faithful  |  5 = Faithful")
        faithfulness = st.radio(
            "Faithfulness rating",
            options=[1, 2, 3, 4, 5],
            index=[1, 2, 3, 4, 5].index(current_feedback.get("faithfulness")) if current_feedback.get("faithfulness") in [1, 2, 3, 4, 5] else None,
            key=f"faithfulness_{feedback_key}",
            horizontal=True,
            label_visibility="collapsed"
        )
        if faithfulness:
            st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
            st.session_state.feedback[feedback_key]["faithfulness"] = faithfulness
        
        # 5. Source Appropriateness - 5-point Likert scale
        st.markdown("**Source Appropriateness:** *Are the cited sources relevant and appropriate for answering the question?*")
        st.caption("1 = Not at all appropriate  |  5 = Appropriate")
        source_appropriateness = st.radio(
            "Source appropriateness rating",
            options=[1, 2, 3, 4, 5],
            index=[1, 2, 3, 4, 5].index(current_feedback.get("source_appropriateness")) if current_feedback.get("source_appropriateness") in [1, 2, 3, 4, 5] else None,
            key=f"source_appropriateness_{feedback_key}",
            horizontal=True,
            label_visibility="collapsed"
        )
        if source_appropriateness:
            st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
            st.session_state.feedback[feedback_key]["source_appropriateness"] = source_appropriateness
        
        comments = st.text_area(
            "Additional comments (optional):",
            value=current_feedback.get("comments", ""),
            key=f"comments_{feedback_key}",
            placeholder="Add any additional feedback or observations..."
        )
        
        if comments != current_feedback.get("comments", ""):
            st.session_state.feedback[feedback_key] = st.session_state.feedback.get(feedback_key, {})
            st.session_state.feedback[feedback_key]["comments"] = comments
    
    # Research process section - Collapsible
    captured_sse_events = row.get("captured_sse_events", "")
    if captured_sse_events and not pd.isna(captured_sse_events):
        try:
            import ast
            events = ast.literal_eval(captured_sse_events) if isinstance(captured_sse_events, str) else captured_sse_events
            
            if isinstance(events, dict):
                search_llm_messages = events.get('search_llm_message', [])
                test_source_debug = events.get('test_source_debug', [])
                
                # Make the entire research process collapsible
                with st.expander("🔍 Research Process - Click to expand", expanded=False):
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
                                                if 'params' in sources[0]:
                                                    st.write(f"**Filter:** {" ".join([f'{k}: `{v}`' for k, v in sources[0]['params'].items()])}")
                                                else:
                                                    query = sources[0]['source_provenance']
                                                    st.write(f"**Query:** `{query.get('query', '')}, Filters: {query.get('filters', '')}`")
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

# Upload existing annotations section - moved to bottom
st.divider()
st.subheader("📤 Load Previous Annotations")

uploaded_file = st.file_uploader(
    "Upload a previously saved annotation file to continue your work:",
    type=['json'],
    help="Upload the JSON file you downloaded earlier to restore your progress",
    key="annotation_uploader"
)

if uploaded_file is not None:
    try:
        uploaded_data = json.load(uploaded_file)
        
        # Validate the structure
        if "annotations" in uploaded_data:
            # Show preview of what will be loaded
            num_annotations = len(uploaded_data['annotations'])
            st.info(f"📋 Found {num_annotations} annotations in this file")
            
            # Show a sample of what will be loaded
            if num_annotations > 0:
                sample_key = list(uploaded_data['annotations'].keys())[0]
                sample = uploaded_data['annotations'][sample_key]
                st.caption(f"Sample: {len([k for k in sample.keys() if sample.get(k)])} ratings")
            
            if st.button("Load Annotations", type="primary", key="load_btn"):
                # Load the annotations into session state
                st.session_state.feedback = uploaded_data["annotations"]
                st.success(f"✅ Successfully loaded {num_annotations} annotations!")
                st.balloons()
                st.rerun()
        else:
            st.error("❌ Invalid annotation file format. Please upload a valid annotations JSON file.")
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
