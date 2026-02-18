from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/api/feedback",
    tags=["feedback"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/", response_model=schemas.Feedback)
def generate_feedback(record_id: int, db: Session = Depends(database.get_db)):
    # 1. Fetch Record
    record = db.query(models.EmotionRecord).filter(models.EmotionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # 2. Prepare Prompt
    emotion = record.emotion_type
    intensity = record.intensity
    note = record.note if record.note else "별도의 메모 없음"
    
    # 정교한 심리 분석 및 인지 재구성을 위한 프롬프트
    prompt = f"""
    [사용자 상황 데이터]
    - 감정 상태: {emotion}
    - 주관적 강도: {intensity} (1~5척도)
    - 상황 메모: {note}

    [당신의 역할]
    당신은 인지행동치료(CBT)와 메타인지(Metacognition) 이론에 정통한 최고 수준의 심리 분석 전문가입니다.
    단순한 위로나 3인칭 소설 묘사가 아니라, 사용자의 상황을 '구조적'으로 분석하고 '상위 관점(Meta-View)'을 제시하여 사용자가 스스로 상황을 객관화할 수 있도록 도와야 합니다.

    [작성 가이드라인 - 반드시 이 순서와 논리를 따를 것]
    
    1. 🌱 지금 당신의 마음은 (상황의 타당화):
       - 사용자가 처한 환경과 상황을 사용자의 입장에서 정확히 인지했음을 보여주세요.
       - 그 상황에서 사용자가 느끼는 감정(패닉, 불안 등)이 생물학적/심리적으로 매우 자연스러운 반응임을 인정해 주세요. (예: "책임감이 강한 사람이기에 느끼는 당연한 고통입니다.")

    2. 🔍 사실을 다시 보면 (인지적 재구성):
       - 사용자의 '주관적 해석'(예: "나는 골칫덩어리다", "끝장났다")과 '객관적 사실'(예: "업무상 실수가 발생했다")을 분리해 주세요.
       - 이 사건을 '개인의 인격적 결함'이 아닌, 복잡한 업무 환경 속에서 발생할 수 있는 '확률적 사고'나 '프로세스의 에러'로 재정의(Re-define)해 주세요.

    3. 🔭 조금 더 넓게 보면 (상위 관점 제시):
       - 시야를 넓혀(Zoom-out) 이 사건을 인생이나 긴 커리어의 관점에서 바라보게 하세요.
       - "누구에게나 일어날 수 있는 일"임을 통계적/보편적 관점에서 언급하여 고립감을 해소해 주세요.
       - 감정에 매몰되지 않고, 이 상황이 '수습하고 넘어가야 할 하나의 에피소드'임을 인지시켜 주세요.

    [어조 및 형식]
    - 반드시 위의 **3가지 소제목(🌱 지금 당신의 마음은, 🔍 사실을 다시 보면, 🔭 조금 더 넓게 보면)**을 사용하여 단락을 구분하세요. (볼드체 처리를 위한 별표 ** 는 사용하지 마세요)
    - 문학적 비유나 모호한 표현을 피하고, 명확하고 분석적인 통찰을 제공하세요.
    - 너무 딱딱하거나 가르치려 들지 말고, 사용자를 존중하는 전문가의 태도를 유지하세요.
    - 공백 포함 300자 ~ 400자 내외로 작성하세요.
    """

    try:
        # 3. Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 사용자의 감정과 상황을 구조적으로 분석하여 메타인지적 통찰을 제공하는 심리 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.6 # 논리적이고 안정적인 답변을 위해 온도를 적절히 조절
        )
        content = response.choices[0].message.content.strip()

    except Exception as e:
        print(f"OpenAI API Error Details: {str(e)}") # Detailed logging
        # Fallback if API fails or key is missing
        content = "오늘 하루도 정말 고생 많으셨어요. 당신의 감정은 소중합니다. (AI 연결 문제로 기본 메시지가 전송되었습니다)"

    # 4. Save & Return Feedback
    feedback = crud.create_feedback(db, record_id, content)
    return feedback
