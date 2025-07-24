#!/usr/bin/env python3
"""
scripts/update_readme.py
테스트 통과 시 README.md를 업데이트합니다.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

def load_readme():
    """기존 README.md 로드"""
    readme_path = Path('README.md')
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return create_initial_readme()

def create_initial_readme():
    """초기 README.md 템플릿 생성"""
    return """# 🚀 알고리즘 스터디

백준 온라인 저지 문제 해결 기록입니다.

## 📊 진행 현황

### 전체 통계
- **해결한 문제**: 0문제
- **참여 인원**: 0명
- **마지막 업데이트**: {today}

### 문제별 해결 현황

| 문제 번호 | 문제 제목 | 해결자 | 제출일 | 언어 | 상태 |
|----------|----------|--------|--------|------|------|

## 📅 주간 일정

| 주차 | 기간 | 문제 | 마감일 |
|------|------|------|--------|

## 🏆 개인 통계

| 참가자 | 해결 문제 수 | 최근 제출 |
|--------|-------------|----------|

## 📝 스터디 규칙

1. **제출 방식**: Fork 후 PR로 제출
2. **파일명 규칙**: `문제번호_문제명.확장자` (예: `1654_랜선자르기.py`)
3. **마감시간**: 매주 일요일 23:59
4. **코드 리뷰**: 자동 테스트 통과 후 자동 머지

## 🔧 자동화 기능

- ✅ 자동 테스트 (샘플 + AI 생성 반례)
- ✅ README 자동 업데이트
- ✅ 마감일 알림 (Mattermost)
- ✅ 진행 상황 추적

---
*Last updated: {today} by GitHub Actions* 🤖
""".format(today=datetime.now().strftime('%Y-%m-%d'))

def parse_existing_stats(readme_content):
    """기존 README에서 통계 정보 파싱"""
    stats = {
        'solved_problems': 0,
        'participants': set(),
        'problems': {}
    }
    
    # 문제별 해결 현황 테이블 파싱
    table_pattern = r'\| 문제 번호 \| 문제 제목 \| 해결자 \| 제출일 \| 언어 \| 상태 \|\n\|[-\s\|]+\|\n((?:\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\n?)*)'
    table_match = re.search(table_pattern, readme_content)
    
    if table_match:
        table_rows = table_match.group(1).strip().split('\n')
        for row in table_rows:
            if row.strip() and '|' in row:
                parts = [p.strip() for p in row.split('|')[1:-1]]  # 양끝 빈 요소 제거
                if len(parts) >= 6 and parts[0].isdigit():
                    problem_id = parts[0]
                    solver = parts[2]
                    stats['problems'][problem_id] = {
                        'title': parts[1],
                        'solver': solver,
                        'date': parts[3],
                        'language': parts[4],
                        'status': parts[5]
                    }
                    stats['participants'].add(solver)
    
    stats['solved_problems'] = len(stats['problems'])
    return stats

def update_problem_table(readme_content, problem_id, author, submission_date, language, title=""):
    """문제 해결 테이블 업데이트"""
    # 기존 통계 파싱
    stats = parse_existing_stats(readme_content)
    
    # 새 문제 추가
    stats['problems'][problem_id] = {
        'title': title or f"문제 {problem_id}",
        'solver': author,
        'date': submission_date,
        'language': language,
        'status': '✅'
    }
    stats['participants'].add(author)
    
    # 테이블 재생성
    table_header = """| 문제 번호 | 문제 제목 | 해결자 | 제출일 | 언어 | 상태 |
|----------|----------|--------|--------|------|------|"""
    
    table_rows = []
    for prob_id in sorted(stats['problems'].keys(), key=int):
        prob_info = stats['problems'][prob_id]
        row = f"| {prob_id} | {prob_info['title']} | {prob_info['solver']} | {prob_info['date']} | {prob_info['language']} | {prob_info['status']} |"
        table_rows.append(row)
    
    new_table = table_header + '\n' + '\n'.join(table_rows)
    
    # 기존 테이블 교체
    table_pattern = r'\| 문제 번호 \| 문제 제목 \| 해결자 \| 제출일 \| 언어 \| 상태 \|\n\|[-\s\|]+\|\n(?:\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\n?)*'
    
    if re.search(table_pattern, readme_content):
        updated_content = re.sub(table_pattern, new_table, readme_content)
    else:
        # 테이블이 없으면 적절한 위치에 삽입
        marker = "### 문제별 해결 현황"
        if marker in readme_content:
            updated_content = readme_content.replace(
                marker,
                f"{marker}\n\n{new_table}"
            )
        else:
            updated_content = readme_content + f"\n\n### 문제별 해결 현황\n\n{new_table}"
    
    return updated_content, stats

def update_overall_stats(readme_content, stats):
    """전체 통계 업데이트"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 전체 통계 섹션 업데이트
    stats_section = f"""### 전체 통계
- **해결한 문제**: {stats['solved_problems']}문제
- **참여 인원**: {len(stats['participants'])}명
- **마지막 업데이트**: {today}"""
    
    # 기존 전체 통계 섹션 교체
    stats_pattern = r'### 전체 통계\n(?:- \*\*[^*]+\*\*: [^\n]+\n)*'
    
    if re.search(stats_pattern, readme_content):
        updated_content = re.sub(stats_pattern, stats_section, readme_content)
    else:
        # 전체 통계 섹션이 없으면 진행 현황 아래에 추가
        marker = "## 📊 진행 현황"
        if marker in readme_content:
            updated_content = readme_content.replace(
                marker,
                f"{marker}\n\n{stats_section}"
            )
        else:
            updated_content = readme_content
    
    return updated_content

def update_personal_stats(readme_content, stats):
    """개인 통계 테이블 업데이트"""
    # 참가자별 통계 계산
    personal_stats = {}
    for problem_id, prob_info in stats['problems'].items():
        solver = prob_info['solver']
        if solver not in personal_stats:
            personal_stats[solver] = {
                'solved_count': 0,
                'latest_date': prob_info['date']
            }
        personal_stats[solver]['solved_count'] += 1
        if prob_info['date'] > personal_stats[solver]['latest_date']:
            personal_stats[solver]['latest_date'] = prob_info['date']
    
    # 개인 통계 테이블 생성
    personal_table_header = """| 참가자 | 해결 문제 수 | 최근 제출 |
|--------|-------------|----------|"""
    
    personal_rows = []
    for participant in sorted(personal_stats.keys()):
        stats_info = personal_stats[participant]
        row = f"| {participant} | {stats_info['solved_count']}문제 | {stats_info['latest_date']} |"
        personal_rows.append(row)
    
    new_personal_table = personal_table_header + '\n' + '\n'.join(personal_rows)
    
    # 기존 개인 통계 테이블 교체
    personal_pattern = r'\| 참가자 \| 해결 문제 수 \| 최근 제출 \|\n\|[-\s\|]+\|\n(?:\|[^|]*\|[^|]*\|[^|]*\|\n?)*'
    
    if re.search(personal_pattern, readme_content):
        updated_content = re.sub(personal_pattern, new_personal_table, readme_content)
    else:
        # 개인 통계 테이블이 없으면 적절한 위치에 삽입
        marker = "## 🏆 개인 통계"
        if marker in readme_content:
            updated_content = readme_content.replace(
                marker,
                f"{marker}\n\n{new_personal_table}"
            )
        else:
            updated_content = readme_content
    
    return updated_content

def update_last_updated(readme_content):
    """마지막 업데이트 시간 갱신"""
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 기존 Last updated 라인 교체
    last_updated_pattern = r'\*Last updated: [^*]+ by GitHub Actions\* 🤖'
    new_last_updated = f"*Last updated: {today} by GitHub Actions* 🤖"
    
    if re.search(last_updated_pattern, readme_content):
        return re.sub(last_updated_pattern, new_last_updated, readme_content)
    else:
        # 없으면 파일 끝에 추가
        return readme_content + f"\n\n---\n{new_last_updated}\n"

def main():
    parser = argparse.ArgumentParser(description='README.md 업데이트')
    parser.add_argument('--problem-id', required=True)
    parser.add_argument('--author', required=True)
    parser.add_argument('--submission-date', required=True)
    parser.add_argument('--language', required=True)
    parser.add_argument('--title', default='')
    args = parser.parse_args()
    
    print(f"📝 README.md 업데이트 중...")
    print(f"  - 문제: {args.problem_id}")
    print(f"  - 해결자: {args.author}")
    print(f"  - 언어: {args.language}")
    
    try:
        # 기존 README 로드
        readme_content = load_readme()
        
        # 1. 문제 해결 테이블 업데이트
        readme_content, stats = update_problem_table(
            readme_content, 
            args.problem_id, 
            args.author, 
            args.submission_date, 
            args.language,
            args.title
        )
        
        # 2. 전체 통계 업데이트
        readme_content = update_overall_stats(readme_content, stats)
        
        # 3. 개인 통계 업데이트
        readme_content = update_personal_stats(readme_content, stats)
        
        # 4. 마지막 업데이트 시간 갱신
        readme_content = update_last_updated(readme_content)
        
        # README.md 저장
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ README.md 업데이트 완료!")
        print(f"  - 총 해결 문제: {stats['solved_problems']}개")
        print(f"  - 참여 인원: {len(stats['participants'])}명")
        
    except Exception as e:
        print(f"::error::README 업데이트 실패: {e}")
        raise

if __name__ == "__main__":
    main()