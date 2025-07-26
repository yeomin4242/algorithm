#!/usr/bin/env python3
"""
scripts/session_counter.py
회차 정보를 관리하는 스크립트
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

SESSION_FILE = 'session_info.json'

def load_session_info():
    """회차 정보 로드"""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"회차 정보 로드 실패: {e}")
    
    # 기본값 반환
    return {
        'current_session': 1,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'last_week_start': None,
        'last_week_end': None
    }

def save_session_info(session_info):
    """회차 정보 저장"""
    try:
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"회차 정보 저장 실패: {e}")
        return False

def get_current_week_info():
    """현재 주차 정보 계산 (일요일 기준)"""
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
        'monday': current_monday.strftime('%Y-%m-%d'),
        'sunday': current_sunday.strftime('%Y-%m-%d'),
        'deadline': current_sunday.strftime('%Y-%m-%d 23:59')
    }

def get_week_info_for_date(date_str):
    """특정 날짜의 주차 정보 계산 (일요일 기준)"""
    target_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 해당 날짜가 속한 주의 일요일 찾기
    days_until_sunday = (6 - target_date.weekday()) % 7  # 월=0, 일=6
    if days_until_sunday == 0 and target_date.weekday() == 6:  # 해당 날짜가 일요일
        current_sunday = target_date
    else:
        current_sunday = target_date + timedelta(days=days_until_sunday)
    
    # 해당 주 월요일 계산
    current_monday = current_sunday - timedelta(days=6)
    
    return {
        'monday': current_monday.strftime('%Y-%m-%d'),
        'sunday': current_sunday.strftime('%Y-%m-%d'),
        'deadline': current_sunday.strftime('%Y-%m-%d 23:59')
    }

def get_session_info(submission_date=None):
    """현재 회차 정보 반환"""
    session_info = load_session_info()
    
    if submission_date:
        # 제출 날짜 기준으로 주차 계산
        target_week = get_week_info_for_date(submission_date)
        target_week_start = target_week['monday']
        last_week_start = session_info.get('last_week_start')
        
        # 새로운 주차인 경우 회차 증가
        if last_week_start != target_week_start:
            session_info['current_session'] += 1
            session_info['last_week_start'] = target_week_start
            session_info['last_week_end'] = target_week['sunday']
            save_session_info(session_info)
            print(f"🔄 새로운 회차 감지: {session_info['current_session']}회차 시작")
        
        return {
            'session_number': session_info['current_session'],
            'monday': target_week['monday'],
            'sunday': target_week['sunday'],
            'deadline': target_week['deadline']
        }
    else:
        # 현재 날짜 기준으로 주차 계산
        current_week = get_current_week_info()
        
        # 이번 주가 새로운 주차인지 확인
        current_week_start = current_week['monday']
        last_week_start = session_info.get('last_week_start')
        
        # 새로운 주차인 경우 회차 증가
        if last_week_start != current_week_start:
            session_info['current_session'] += 1
            session_info['last_week_start'] = current_week_start
            session_info['last_week_end'] = current_week['sunday']
            save_session_info(session_info)
            print(f"🔄 새로운 회차 감지: {session_info['current_session']}회차 시작")
        
        return {
            'session_number': session_info['current_session'],
            'monday': current_week['monday'],
            'sunday': current_week['sunday'],
            'deadline': current_week['deadline']
        }

def reset_session_counter():
    """회차 카운터 초기화 (1회차로 리셋)"""
    session_info = {
        'current_session': 1,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'last_week_start': None,
        'last_week_end': None
    }
    return save_session_info(session_info)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='회차 정보 관리')
    parser.add_argument('--reset', action='store_true', help='회차 카운터 초기화')
    args = parser.parse_args()
    
    if args.reset:
        if reset_session_counter():
            print("✅ 회차 카운터가 1회차로 초기화되었습니다.")
        else:
            print("❌ 회차 카운터 초기화 실패")
    else:
        session_info = get_session_info()
        print(f"현재 회차: {session_info['session_number']}회차")
        print(f"기간: {session_info['monday']} ~ {session_info['sunday']}")
        print(f"마감: {session_info['deadline']}") 