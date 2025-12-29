import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="KoELSA AI 안전 문진봇", page_icon="??")

st.title("?? AI 승강기 안전 소통 문진표")
st.markdown("---")
st.info("?? 검사 전, 고객님의 불안 사항을 미리 듣고 맞춤형으로 점검해 드립니다.")

# --- 2. 세션 상태 초기화 (대화 기록 저장) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 첫 인사 및 첫 번째 질문 (건물 정보)
    st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 한국승강기안전공단 AI 챗봇입니다. \n\n먼저 **건물명과 승강기 고유번호**를 입력해 주세요."})

if "step" not in st.session_state:
    st.session_state.step = 0 # 진행 단계 추적

if "diagnosis" not in st.session_state:
    st.session_state.diagnosis = None # 진단 결과 저장

# --- 3. 그래픽 리포트 생성 함수 (matplotlib) ---
def generate_report(diagnosis_type, complaint):
    fig, ax = plt.subplots(figsize=(4, 6))
    
    # 승강기 배경
    ax.add_patch(patches.Rectangle((0.1, 0.1), 0.8, 0.8, linewidth=2, edgecolor='#333', facecolor='#f9f9f9'))
    ax.add_patch(patches.Rectangle((0.2, 0.2), 0.6, 0.6, linewidth=2, edgecolor='black', facecolor='white'))
    
    # 부위 정의
    parts = {
        "DOOR": patches.Rectangle((0.45, 0.2), 0.1, 0.6, facecolor='gray', alpha=0.1),
        "MACHINE": patches.Rectangle((0.2, 0.82), 0.6, 0.15, facecolor='gray', alpha=0.1)
    }
    for p in parts.values(): ax.add_patch(p)

    # 진단에 따른 하이라이트
    target = None
    diag_text = ""
    
    if diagnosis_type == "DOOR":
        target = parts["DOOR"]
        diag_text = "도어(Door) 정밀 점검"
    elif diagnosis_type == "MACHINE":
        target = parts["MACHINE"]
        diag_text = "권상기/로프 소음 점검"
    
    if target:
        target.set_facecolor('#FF4444')
        target.set_alpha(0.8)
        target.set_edgecolor('red')
        ax.add_patch(target)
        ax.text(0.5, 0.5 if diagnosis_type == "DOOR" else 0.9, "CHECK HERE!", 
                color='red', fontweight='bold', ha='center', fontsize=12)

    ax.axis('off')
    st.pyplot(fig) # 웹 화면에 출력

# --- 4. 채팅 인터페이스 구현 ---
# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("답변을 입력해주세요..."):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 챗봇 응답 로직 (단계별 질문)
    response = ""
    
    # Step 0: 건물 정보 입력 후 -> 관리자 선임 여부 질문
    if st.session_state.step == 0:
        response = "확인되었습니다. \n\n**최근 1년 이내에 안전관리자가 변경된 적이 있나요?**\n(승강기 안전관리법 제29조에 따라 변경 시 신고가 필요합니다.)"
        st.session_state.step = 1
        
    # Step 1: 관리자 답변 후 -> 보험 가입 여부 질문
    elif st.session_state.step == 1:
        if "네" in prompt or "예" in prompt:
            response = "?? **[안내]** 관리자 변경 신고가 누락되지 않도록 확인 부탁드립니다. \n\n다음으로, **승강기 책임보험(사고배상 책임보험)에 가입되어 있나요?**"
        else:
            response = "네, 알겠습니다. \n\n다음으로, **승강기 책임보험(사고배상 책임보험)에 가입되어 있나요?**"
        st.session_state.step = 2
        
    # Step 2: 보험 답변 후 -> 불안 요소(주관식) 질문
    elif st.session_state.step == 2:
        response = "확인 감사합니다. 이제 고객님의 불안 사항을 듣겠습니다. \n\n**평소 이용하시면서 소음, 진동, 문 닫힘 등 불편하거나 불안했던 점이 있다면 자유롭게 적어주세요.**"
        st.session_state.step = 3

    # Step 3: AI 분석 및 리포트 생성
    elif st.session_state.step == 3:
        # 간단한 키워드 분석 로직
        diagnosis = "NORMAL"
        if "문" in prompt or "닫힐" in prompt or "쾅" in prompt:
            diagnosis = "DOOR"
            analysis_msg = "?? **AI 분석 결과:** '도어 개폐 장치' 관련 이상이 의심됩니다."
        elif "소리" in prompt or "웅" in prompt or "진동" in prompt:
            diagnosis = "MACHINE"
            analysis_msg = "?? **AI 분석 결과:** '권상기 또는 로프' 관련 소음이 의심됩니다."
        else:
            analysis_msg = "? **AI 분석 결과:** 특이 사항이 감지되지 않았으나, 전반적인 정밀 점검을 진행하겠습니다."

        response = f"{analysis_msg}\n\n잠시만 기다려주세요. **맞춤형 안심 리포트**를 생성 중입니다..."
        st.session_state.diagnosis = diagnosis
        st.session_state.step = 4

    # 챗봇 메시지 표시
    with st.chat_message("assistant"):
        st.markdown(response)
        
        # 마지막 단계면 그래픽 리포트 출력
        if st.session_state.step == 4 and st.session_state.diagnosis:
            with st.spinner('그래픽 리포트 생성 중...'):
                time.sleep(1.5) # 생성하는 척 연출
                generate_report(st.session_state.diagnosis, prompt)
                st.success("?? 리포트가 생성되었습니다! 검사원이 해당 부위를 집중 점검하고 결과를 안내해 드릴 예정입니다.")
            
    st.session_state.messages.append({"role": "assistant", "content": response})