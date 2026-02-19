-- ============================================================
-- MoodPing DB Schema (MySQL 8.0)
-- Spring Boot 버전(moodping-backend)과 동일한 스키마
-- 문자셋: utf8mb4 (이모지 저장 지원)
-- ============================================================

-- 0. 사용자 테이블
CREATE TABLE IF NOT EXISTS user
(
    id            BIGINT       NOT NULL AUTO_INCREMENT,
    kakao_id      VARCHAR(100) NOT NULL COMMENT '카카오 고유 ID',
    nickname      VARCHAR(100) NULL     COMMENT '카카오 닉네임',
    profile_image VARCHAR(500) NULL     COMMENT '카카오 프로필 이미지 URL',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_kakao_id (kakao_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- 1. 감정 기록 테이블
CREATE TABLE IF NOT EXISTS mood_record
(
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    user_id     VARCHAR(100) NULL     COMMENT '로그인 사용자 ID (없으면 NULL)',
    anon_id     VARCHAR(100) NULL     COMMENT '비로그인 사용자 익명 ID',
    record_date DATE         NOT NULL COMMENT '기록 날짜 (서버 기준)',
    recorded_at DATETIME     NOT NULL COMMENT '기록 일시 (서버 기준)',
    mood_emoji  VARCHAR(20)  NOT NULL COMMENT '감정 이모지 문자 (예: 😊)',
    intensity   TINYINT      NOT NULL COMMENT '감정 강도 0~10',
    mood_text   VARCHAR(500) NULL     COMMENT '감정 설명 텍스트 (선택)',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_mood_record_user_id (user_id),
    INDEX idx_mood_record_anon_id (anon_id),
    INDEX idx_mood_record_recorded_at (recorded_at),
    CONSTRAINT chk_intensity CHECK (intensity >= 0 AND intensity <= 10)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- 2. AI 감정 분석 결과 테이블
CREATE TABLE IF NOT EXISTS mood_analysis
(
    id            BIGINT       NOT NULL AUTO_INCREMENT,
    record_id     BIGINT       NOT NULL COMMENT 'mood_record.id FK',
    user_id       VARCHAR(100) NULL     COMMENT '분석 요청 사용자 ID',
    analysis_text TEXT         NULL     COMMENT 'LLM이 생성한 분석 문단',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_mood_analysis_record_id (record_id),
    CONSTRAINT fk_mood_analysis_record FOREIGN KEY (record_id) REFERENCES mood_record (id) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- 3. 유저 퍼널 이벤트 로그 테이블
CREATE TABLE IF NOT EXISTS event_log
(
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    event_id    VARCHAR(100) NOT NULL COMMENT '프론트에서 생성한 이벤트 고유 UUID',
    session_id  VARCHAR(100) NOT NULL COMMENT '세션 고유 UUID',
    user_id     VARCHAR(100) NULL     COMMENT '로그인 사용자 ID',
    anon_id     VARCHAR(100) NULL     COMMENT '비로그인 사용자 익명 ID',
    event_name  VARCHAR(50)  NOT NULL COMMENT '이벤트 이름',
    occurred_at DATETIME     NOT NULL COMMENT '이벤트 발생 일시',
    extra_data  JSON         NULL     COMMENT '이벤트 추가 데이터',
    PRIMARY KEY (id),
    UNIQUE KEY uk_event_id (event_id),
    INDEX idx_event_log_session_id (session_id),
    INDEX idx_event_log_event_name (event_name),
    INDEX idx_event_log_occurred_at (occurred_at),
    INDEX idx_event_log_user_id (user_id),
    INDEX idx_event_log_anon_id (anon_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- 4. 주간 리포트 테이블
CREATE TABLE IF NOT EXISTS weekly_report
(
    id                BIGINT        NOT NULL AUTO_INCREMENT,
    user_id           BIGINT        NOT NULL COMMENT 'user.id FK',
    week_start        DATE          NOT NULL COMMENT '주간 시작일 (월요일)',
    week_end          DATE          NOT NULL COMMENT '주간 종료일 (일요일)',
    summary_text      TEXT          NULL     COMMENT 'LLM이 생성한 주간 요약',
    record_count      INT           NOT NULL DEFAULT 0,
    avg_intensity     DECIMAL(3,1)  NULL,
    mood_distribution JSON          NULL     COMMENT '감정별 빈도 JSON',
    created_at        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_week (user_id, week_start),
    INDEX idx_weekly_report_user_id (user_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
