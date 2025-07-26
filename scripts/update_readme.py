#!/usr/bin/env python3
"""
scripts/update_readme.py
테스트 통과 시 README.md를 업데이트합니다.
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

def load_readme():
    """기존 README.md 로드"""
    readme_path = Path('README.md')
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return create_initial_readme()

def get_week_info(submission_date=None):
    """현재 회차 정보 계산 (새로운 회차 시스템)"""
    try:
        # session_counter 모듈에서 회차 정보 가져오기
        from session_counter import get_session_info, get_week_info_for_date
        
        if submission_date:
            # 제출 날짜 기준으로 주차 계산
            session_info = get_session_info(submission_date)
            
            return {
                'session_number': session_info['session_number'],
                'monday': session_info['monday'],
                'sunday': session_info['sunday'],
                'deadline': session_info['deadline']
            }
        else:
            # 현재 날짜 기준으로 주차 계산
            session_info = get_session_info()
            
            return {
                'session_number': session_info['session_number'],
                'monday': session_info['monday'],
                'sunday': session_info['sunday'],
                'deadline': session_info['deadline']
            }
    except ImportError:
        # fallback: 기존 방식 사용
        today = datetime.now()
        
        # 이번 주 일요일 찾기 (오늘이 일요일이면 오늘, 아니면 다음 일요일)
        days_until_sunday = (6 - today.weekday()) % 7  # 월=0, 일=6
        if days_until_sunday == 0 and today.weekday() == 6:  # 오늘이 일요일
            current_sunday = today
        else:
            current_sunday = today + timedelta(days=days_until_sunday)
        
        # 이번 주 월요일 계산
        current_monday = current_sunday - timedelta(days=6)
        
        return {
            'session_number': 1,  # 기본값
            'monday': current_monday.strftime('%Y-%m-%d'),
            'sunday': current_sunday.strftime('%Y-%m-%d'),
            'deadline': current_sunday.strftime('%Y-%m-%d 23:59')
        }

def create_current_week_section():
    """현재 회차 섹션 생성"""
    week_info = get_week_info()
    
    # 주간 날짜 계산
    monday = datetime.strptime(week_info['monday'], '%Y-%m-%d')
    week_dates = []
    for i in range(7):
        date = monday + timedelta(days=i)
        week_dates.append(date.strftime('%m/%d'))
    
    return f"""# 🚀 알고리즘 스터디

## 📅 {week_info['session_number']}회차 현황
**기간**: {week_info['monday']} ~ {week_info['sunday']}  
**마감**: {week_info['deadline']}

### 제출 현황

| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |
|--------|----|----|----|----|----|----|---|
|        | {week_dates[0]} | {week_dates[1]} | {week_dates[2]} | {week_dates[3]} | {week_dates[4]} | {week_dates[5]} | {week_dates[6]} |

"""

def create_static_info_section():
    """정적 정보 섹션 생성"""
    return """
## 🤖 자동화 시스템 소개

### 🔧 주요 기능
- **자동 테스트**: 샘플 테스트케이스 + AI 생성 반례 테스트
- **스마트 채점**: 부분 점수 지원 (샘플만/생성 테스트만 통과)
- **개인 알림**: Mattermost 개인 DM으로 결과 통知
- **자동 README 업데이트**: 제출 현황 실시간 반영

### 🧠 사용 기술
- **AI 모델**: Google Gemini 2.5-flash
- **테스트 생성**: 문제 분석 → 반례 자동 생성
- **플랫폼**: GitHub Actions + Python
- **개인 알림**: 사용자별 주간 현황 체크 + 맞춤 알림

### 📝 사용 방법

#### 1. Repository 설정
```bash
# 1. 이 Repository Fork
# 2. 본인 디렉토리 생성: 본인깃허브아이디/문제번호/Main.java
# 3. 코드 작성 후 PR 생성
```

#### 2. 필요한 Secrets 설정
Repository Settings → Secrets and variables → Actions에서 다음 설정:

```
GEMINI_API_KEY=your_gemini_api_key
MATTERMOST_WEBHOOK_URL=your_default_channel_webhook  # 기본 채널용
본인깃허브아이디_MATTERMOST_URL=your_personal_webhook  # 개인 DM용 (필수)
```

**📱 개인 알림 설정**: 주간 5문제 미달 시 개인 DM 알림을 받으려면 반드시 개인 webhook URL을 설정하세요. 
자세한 설정 방법은 `docs/개인알림_설정가이드.md`를 참고하세요.

#### 3. 디렉토리 구조
```
본인깃허브아이디/
├── 1000/
│   └── Main.java
├── 1001/
│   └── Main.java
└── 2557/
    └── Main.java
```

#### 4. PR 제출 과정
1. **브랜치 생성**: `git checkout -b week-N-solutions`  
2. **코드 작성**: 위 구조대로 파일 배치
3. **PR 생성**: main 브랜치로 Pull Request
4. **자동 테스트**: GitHub Actions에서 자동 실행
5. **결과 확인**: 개인 DM + PR 댓글로 결과 통知
6. **자동 병합**: 테스트 통과 시 자동 README 업데이트 후 병합

### 🎯 테스트 기준
- **완전 성공**: 샘플 + 생성 테스트 모두 통과
- **부분 성공**: 샘플 또는 생성 테스트 중 하나만 통과  
- **실패**: 모든 테스트 실패
- **PR 승인**: 한 문제 이상 성공 시 자동 승인

### 🚨 주의사항
- Java 11 환경에서 테스트됩니다
- 파일명은 반드시 `Main.java`로 통일
- 패키지 선언 없이 작성해주세요
- 무한루프나 과도한 메모리 사용 시 타임아웃됩니다

### 📞 문의사항
- GitHub Issues 또는 Mattermost 채널에서 문의
- 버그 리포트나 개선 제안 환영합니다!"""

def create_initial_readme():
    """초기 README.md 템플릿 생성"""
    current_week = create_current_week_section()
    static_info = create_static_info_section()
    return current_week + static_info

def parse_current_week_stats(readme_content, submission_date=None):
    """현재 회차 README에서 제출 현황 파싱"""
    current_week = get_week_info(submission_date)
    
    # 회차 정보 확인 - README의 회차와 현재 회차가 다르면 초기화
    week_pattern = rf"## 📅 (\d+)회차 현황"
    week_match = re.search(week_pattern, readme_content)
    
    if not week_match or int(week_match.group(1)) != current_week['session_number']:
        # 회차가 바뀌었으므로 빈 통계 반환 (초기화)
        return {
            'participants': {},
            'need_reset': True
        }
    
    stats = {
        'participants': {},
        'need_reset': False
    }
    
    # 테이블에서 참가자 정보 추출 (간단한 방식)
    lines = readme_content.split('\n')
    table_started = False
    
    for i, line in enumerate(lines):
        # 테이블 시작 확인
        if '| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |' in line:
            table_started = True
            continue
            
        # 테이블 구분선 건너뛰기
        if table_started and '|---' in line:
            continue
            
        # 날짜 행 건너뛰기
        if table_started and line.strip().startswith('|') and not line.strip().split('|')[1].strip():
            continue
            
        # 테이블 종료 조건 (--- 라인은 건너뛰고 실제 컨텐츠에서 종료)
        if table_started and not line.strip().startswith('|') and line.strip() != '' and line.strip() != '---' and '##' in line:
            break
            
        # 참가자 데이터 행 처리
        if table_started and line.strip().startswith('|'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            
            # 참가자 이름이 있는 행 (문제 번호도 같은 행에 있음)
            if len(parts) >= 8 and parts[0] and parts[0] != '':
                participant = parts[0]
                
                # 요일별 데이터 구성 (같은 행에서 바로 가져오기)
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                participant_data = {}
                
                for j, weekday in enumerate(weekdays):
                    problems = []
                    if j + 1 < len(parts) and parts[j + 1]:  # +1은 참가자 이름 칸 때문
                        # 문제 번호들 파싱 (콤마로 구분, ... 제거)
                        problem_text = parts[j + 1].replace('...', '').strip()
                        if problem_text and problem_text != '---':
                            # 숫자만 추출 (공백 제거 후)
                            problems = [p.strip() for p in problem_text.split(',') if p.strip().isdigit()]
                    participant_data[weekday] = problems
                
                stats['participants'][participant] = participant_data
    
    return stats

def get_weekday_from_date(date_str):
    """날짜 문자열에서 요일 인덱스 반환 (월=0, 일=6)"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.weekday()  # 월=0, 일=6

def update_current_week_table(readme_content, problem_id, author, submission_date, language, title=""):
    """현재 주차 제출 현황 테이블 업데이트 - 완전 새로 생성 방식"""
    current_week = get_week_info(submission_date)
    
    # 제출일이 현재 주차 범위 내인지 확인
    submission_weekday = get_weekday_from_date(submission_date)
    weekday_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    weekday_name = weekday_names[submission_weekday]
    
    # 기존 통계 파싱
    stats = parse_current_week_stats(readme_content, submission_date)
    
    # 주차가 바뀌었거나 README가 없으면 새로 생성
    if stats['need_reset'] or '## 📅' not in readme_content:
        # 새 참가자 정보 추가
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        participant_data = {day: [] for day in weekdays}
        participant_data[weekday_name] = [problem_id]
        
        stats = {
            'participants': {
                author: participant_data
            },
            'need_reset': False
        }
    else:
        # 기존 참가자 정보 업데이트
        if author in stats['participants']:
            participant_info = stats['participants'][author]
            
            # 해당 요일에 문제 추가 (중복 방지)
            if problem_id not in participant_info[weekday_name]:
                participant_info[weekday_name].append(problem_id)
        else:
            # 새 참가자 추가
            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            participant_data = {day: [] for day in weekdays}
            participant_data[weekday_name] = [problem_id]
            stats['participants'][author] = participant_data
    
    # 완전히 새로운 README 생성 (--- 라인 없이)
    print(f"🔧 참가자 정보: {stats['participants']}")
    updated_content = create_complete_readme(stats['participants'], current_week)
    print(f"✅ 새로운 README 생성 완료")
    
    return updated_content, stats

def create_complete_readme(participants, current_week):
    """완전히 새로운 README 생성 (--- 라인 제거)"""
    # 주간 달력 테이블 생성
    table = create_participant_table(participants, current_week)
    
    # 주간 날짜 계산
    monday = datetime.strptime(current_week['monday'], '%Y-%m-%d')
    week_dates = []
    for i in range(7):
        date = monday + timedelta(days=i)
        week_dates.append(date.strftime('%m/%d'))
    
    # 완전한 README 컨텐츠 생성
    readme_content = f"""# 🚀 알고리즘 스터디

## 📅 {current_week['session_number']}회차 현황
**기간**: {current_week['monday']} ~ {current_week['sunday']}  
**마감**: {current_week['deadline']}

### 제출 현황

{table}

## 🤖 자동화 시스템 소개

### 🔧 주요 기능
- **자동 테스트**: 샘플 테스트케이스 + AI 생성 반례 테스트
- **스마트 채점**: 부분 점수 지원 (샘플만/생성 테스트만 통과)
- **개인 알림**: Mattermost 개인 DM으로 결과 통知
- **자동 README 업데이트**: 제출 현황 실시간 반영

### 🧠 사용 기술
- **AI 모델**: Google Gemini 2.5-flash
- **테스트 생성**: 문제 분석 → 반례 자동 생성
- **플랫폼**: GitHub Actions + Python
- **개인 알림**: 사용자별 주간 현황 체크 + 맞춤 알림

### 📝 사용 방법

#### 1. Repository 설정
```bash
# 1. 이 Repository Fork
# 2. 본인 디렉토리 생성: 본인깃허브아이디/문제번호/Main.java
# 3. 코드 작성 후 PR 생성
```

#### 2. 필요한 Secrets 설정
Repository Settings → Secrets and variables → Actions에서 다음 설정:

```
GEMINI_API_KEY=your_gemini_api_key
MATTERMOST_WEBHOOK_URL=your_default_channel_webhook  # 기본 채널용
본인깃허브아이디_MATTERMOST_URL=your_personal_webhook  # 개인 DM용 (필수)
```

**📱 개인 알림 설정**: 주간 5문제 미달 시 개인 DM 알림을 받으려면 반드시 개인 webhook URL을 설정하세요. 
자세한 설정 방법은 `docs/개인알림_설정가이드.md`를 참고하세요.

#### 3. 디렉토리 구조
```
본인깃허브아이디/
├── 1000/
│   └── Main.java
├── 1001/
│   └── Main.java
└── 2557/
    └── Main.java
```

#### 4. PR 제출 과정
1. **브랜치 생성**: `git checkout -b week-N-solutions`  
2. **코드 작성**: 위 구조대로 파일 배치
3. **PR 생성**: main 브랜치로 Pull Request
4. **자동 테스트**: GitHub Actions에서 자동 실행
5. **결과 확인**: 개인 DM + PR 댓글로 결과 통知
6. **자동 병합**: 테스트 통과 시 자동 README 업데이트 후 병합

### 🎯 테스트 기준
- **완전 성공**: 샘플 + 생성 테스트 모두 통과
- **부분 성공**: 샘플 또는 생성 테스트 중 하나만 통과  
- **실패**: 모든 테스트 실패
- **PR 승인**: 한 문제 이상 성공 시 자동 승인

### 🚨 주의사항
- Java 11 환경에서 테스트됩니다
- 파일명은 반드시 `Main.java`로 통일
- 패키지 선언 없이 작성해주세요
- 무한루프나 과도한 메모리 사용 시 타임아웃됩니다

### 📞 문의사항
- GitHub Issues 또는 Mattermost 채널에서 문의
- 버그 리포트나 개선 제안 환영합니다!

---
*Auto-updated by GitHub Actions 🤖*
"""
    
    return readme_content

def create_participant_table(participants, current_week):
    """참가자 테이블 생성 (주간 달력 형식)"""
    # 주간 날짜 계산
    monday = datetime.strptime(current_week['monday'], '%Y-%m-%d')
    week_dates = []
    for i in range(7):
        date = monday + timedelta(days=i)
        week_dates.append(date.strftime('%m/%d'))
    
    # 테이블 헤더 (올바른 마크다운 테이블 형식)
    table_header = f"""| 참가자 | 월 | 화 | 수 | 목 | 금 | 토 | 일 |
|--------|----|----|----|----|----|----|---|
|        | {week_dates[0]} | {week_dates[1]} | {week_dates[2]} | {week_dates[3]} | {week_dates[4]} | {week_dates[5]} | {week_dates[6]} |"""
    
    table_rows = []
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for participant in sorted(participants.keys()):
        participant_data = participants[participant]
        
        # 참가자 행: 참가자 이름과 문제 번호들
        row_parts = [participant]
        for weekday in weekdays:
            problems = participant_data[weekday]
            if problems:
                # 3개 넘으면 3개만 표시하고 ... 붙이기
                if len(problems) > 3:
                    problem_text = ', '.join(problems[:3]) + '...'
                else:
                    problem_text = ', '.join(problems)
                row_parts.append(problem_text)
            else:
                row_parts.append('')
        
        row = '| ' + ' | '.join(row_parts) + ' |'
        table_rows.append(row)
    
    # 마지막에 구분선 추가하지 않음 (테이블 끝)
    return table_header + '\n' + '\n'.join(table_rows)

def update_last_updated(readme_content):
    """마지막 업데이트 시간 갱신 (중복 제거)"""
    # 다양한 형식의 Auto-updated 문구들을 모두 제거
    patterns_to_remove = [
        r'\n---\n\*Auto-updated by GitHub Actions 🤖\*\n*$',
        r'\n---\n_Auto-updated by GitHub Actions 🤖_\n*$',
        r'\*Auto-updated by GitHub Actions 🤖\*\n*$',
        r'_Auto-updated by GitHub Actions 🤖_\n*$',
        r'\n+---\n+\*Auto-updated by GitHub Actions 🤖\*\n*',
        r'\n+---\n+_Auto-updated by GitHub Actions 🤖_\n*'
    ]
    
    # 기존 Auto-updated 문구들 모두 제거
    cleaned_content = readme_content
    for pattern in patterns_to_remove:
        cleaned_content = re.sub(pattern, '', cleaned_content)
    
    # 끝부분 공백 정리
    cleaned_content = cleaned_content.rstrip()
    
    # 새로운 Auto-updated 문구 한 번만 추가
    return cleaned_content + "\n\n---\n*Auto-updated by GitHub Actions 🤖*\n"

def main():
    parser = argparse.ArgumentParser(description='README.md 업데이트')
    parser.add_argument('--problem-id', required=True)
    parser.add_argument('--author', required=True)
    parser.add_argument('--submission-date', required=True)
    parser.add_argument('--language', required=True)
    parser.add_argument('--title', default='')
    args = parser.parse_args()
    
    current_week = get_week_info(args.submission_date)
    
    print(f"📝 README.md 업데이트 중...")
    print(f"  - 회차: {current_week['session_number']}회차")
    print(f"  - 문제: {args.problem_id}")
    print(f"  - 해결자: {args.author}")
    print(f"  - 제출일: {args.submission_date}")
    
    try:
        # 기존 README 로드
        readme_content = load_readme()
        
        # 1. 현재 주차 제출 현황 테이블 업데이트
        readme_content, stats = update_current_week_table(
            readme_content, 
            args.problem_id, 
            args.author, 
            args.submission_date, 
            args.language,
            args.title
        )
        
        # 2. 마지막 업데이트 시간 갱신
        readme_content = update_last_updated(readme_content)
        
        # README.md 저장
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ README.md 업데이트 완료!")
        if stats['need_reset']:
            print("  - 🔄 새로운 주차로 초기화됨")
        print(f"  - 현재 주차 참여 인원: {len(stats['participants'])}명")
        
        # 참가자별 현황 출력
        for participant, weekday_data in stats['participants'].items():
            total_problems = sum(len(problems) for problems in weekday_data.values())
            active_days = sum(1 for problems in weekday_data.values() if problems)
            print(f"    - {participant}: {total_problems}개 문제, {active_days}일 활동")
        
    except Exception as e:
        print(f"::error::README 업데이트 실패: {e}")
        raise

if __name__ == "__main__":
    main()