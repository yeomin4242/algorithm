#!/usr/bin/env python3
"""
scripts/deadline_checker.py
마감일을 체크하고 Mattermost로 알림을 보냅니다.
"""

import os
import json
import requests
import subprocess
from datetime import datetime, timedelta
import pytz

def get_repository_info():
    """GitHub 레포지토리 정보 가져오기"""
    try:
        # GitHub API를 통해 레포지토리 정보 가져오기
        token = os.getenv('GITHUB_TOKEN')
        repo = os.getenv('GITHUB_REPOSITORY')  # 예: 'username/repo-name'
        
        if not token or not repo:
            print("GitHub 환경변수가 설정되지 않았습니다.")
            return None
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 레포지토리 기본 정보
        repo_url = f"https://api.github.com/repos/{repo}"
        response = requests.get(repo_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"GitHub API 오류: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"레포지토리 정보 조회 실패: {e}")
        return None

def get_current_week_deadline():
    """현재 주차의 마감일 계산"""
    # 한국 시간 기준
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    
    # 일요일을 주의 마지막으로 간주 (0=월요일, 6=일요일)
    days_until_sunday = (6 - now.weekday()) % 7
    if days_until_sunday == 0 and now.hour >= 23:  # 일요일 밤 11시 이후면 다음 주
        days_until_sunday = 7
    
    deadline = now + timedelta(days=days_until_sunday)
    deadline = deadline.replace(hour=23, minute=59, second=59, microsecond=0)
    
    return deadline

def get_participants_from_readme():
    """README.md에서 참가자 목록 추출"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 개인 통계 테이블에서 참가자 추출
        import re
        pattern = r'\| ([^|]+) \| \d+문제 \| [^|]+ \|'
        matches = re.findall(pattern, content)
        
        participants = [match.strip() for match in matches if match.strip()]
        return participants
        
    except Exception as e:
        print(f"README에서 참가자 추출 실패: {e}")
        return []

def get_recent_submissions():
    """최근 제출 현황 조회"""
    try:
        # 최근 1주일간의 PR 조회
        token = os.getenv('GITHUB_TOKEN')
        repo = os.getenv('GITHUB_REPOSITORY')
        
        if not token or not repo:
            return []
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 일주일 전 날짜
        week_ago = datetime.now() - timedelta(days=7)
        since_date = week_ago.isoformat()
        
        # 최근 PR 조회
        pr_url = f"https://api.github.com/repos/{repo}/pulls?state=closed&since={since_date}&per_page=100"
        response = requests.get(pr_url, headers=headers)
        
        if response.status_code == 200:
            prs = response.json()
            recent_submissions = []
            
            for pr in prs:
                if pr.get('merged_at'):  # 머지된 PR만
                    recent_submissions.append({
                        'author': pr['user']['login'],
                        'title': pr['title'],
                        'merged_at': pr['merged_at']
                    })
            
            return recent_submissions
        else:
            return []
            
    except Exception as e:
        print(f"최근 제출 조회 실패: {e}")
        return []

def check_who_needs_reminder(participants, recent_submissions, deadline):
    """알림이 필요한 사용자 확인"""
    # 최근 제출한 사용자들
    recent_submitters = {sub['author'] for sub in recent_submissions}
    
    # 제출하지 않은 사용자들
    need_reminder = [p for p in participants if p not in recent_submitters]
    
    return need_reminder

def send_mattermost_notification(message):
    """Mattermost 웹훅으로 알림 전송"""
    webhook_url = os.getenv('MATTERMOST_WEBHOOK_URL')
    
    if not webhook_url:
        print("Mattermost 웹훅 URL이 설정되지 않았습니다.")
        return False
    
    payload = {
        "text": message,
        "username": "Algorithm Study Bot",
        "icon_emoji": ":robot_face:"
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ Mattermost 알림 전송 성공")
            return True
        else:
            print(f"❌ Mattermost 알림 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Mattermost 알림 전송 예외: {e}")
        return False

def create_reminder_message(deadline, need_reminder, repo_info):
    """알림 메시지 생성"""
    kst = pytz.timezone('Asia/Seoul')
    deadline_kst = deadline.astimezone(kst)
    
    # 마감까지 남은 시간 계산
    now = datetime.now(kst)
    time_left = deadline_kst - now
    hours_left = int(time_left.total_seconds() / 3600)
    
    repo_name = repo_info.get('name', 'Algorithm Study') if repo_info else 'Algorithm Study'
    repo_url = repo_info.get('html_url', '') if repo_info else ''
    
    if hours_left <= 2:
        # 2시간 이내 긴급 알림
        urgency = "🚨 **긴급**"
        time_msg = f"{hours_left}시간 {int((time_left.total_seconds() % 3600) / 60)}분"
    elif hours_left <= 24:
        # 24시간 이내 일반 알림
        urgency = "⏰ **마감 임박**"
        time_msg = f"{hours_left}시간"
    else:
        # 일반 알림
        urgency = "📅 **알림**"
        time_msg = f"{int(hours_left/24)}일 {hours_left%24}시간"
    
    message =