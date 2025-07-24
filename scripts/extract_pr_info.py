#!/usr/bin/env python3
"""
scripts/extract_pr_info.py
PR에서 문제 번호와 코드 파일 정보를 추출합니다.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

def extract_problem_id_from_path(file_path):
    """파일 경로에서 문제 번호 추출"""
    # 예: alice/1654/Main.java -> 1654
    # 예: bob/2805/Main.java -> 2805
    patterns = [
        r'[^/\\]+[/\\](\d+)[/\\]Main\.java',  # 이름/번호/Main.java
        r'[^/\\]+[/\\](\d+)[/\\]',             # 이름/번호/
        r'(\d+)[/\\]Main\.java',               # 번호/Main.java
    ]
    
    for pattern in patterns:
        match = re.search(pattern, file_path)
        if match:
            return match.group(1)
    
    return None

def extract_author_from_path(file_path):
    """파일 경로에서 작성자 이름 추출"""
    # 예: alice/1654/Main.java -> alice
    match = re.match(r'([^/\\]+)[/\\]\d+[/\\]Main\.java', file_path)
    if match:
        return match.group(1)
    return None

def get_changed_files():
    """PR에서 변경된 파일들 가져오기"""
    try:
        # PR의 변경된 파일들 조회
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'origin/main...HEAD'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []

def detect_language(file_path):
    """파일 확장자로 언어 감지 (Java 전용)"""
    if file_path.endswith('Main.java'):
        return 'java'
    return 'unknown'

def main():
    changed_files = get_changed_files()
    
    # Main.java 파일 필터링
    java_files = [
        f for f in changed_files 
        if f.endswith('Main.java') and Path(f).exists()
    ]
    
    if not java_files:
        print("::error::Main.java 파일이 발견되지 않았습니다.")
        sys.exit(1)
    
    # 첫 번째 Main.java 파일을 메인 제출 파일로 간주
    main_file = java_files[0]
    problem_id = extract_problem_id_from_path(main_file)
    author = extract_author_from_path(main_file)
    
    if not problem_id:
        print(f"::error::파일 경로에서 문제 번호를 추출할 수 없습니다: {main_file}")
        print("파일 경로는 '이름/문제번호/Main.java' 형식이어야 합니다.")
        sys.exit(1)
    
    if not author:
        print(f"::error::파일 경로에서 작성자를 추출할 수 없습니다: {main_file}")
        sys.exit(1)
    
    language = detect_language(main_file)
    
    # GitHub Actions 출력
    print(f"::set-output name=problem_id::{problem_id}")
    print(f"::set-output name=code_file::{main_file}")
    print(f"::set-output name=language::{language}")
    print(f"::set-output name=author::{author}")
    
    print(f"✅ 추출 완료:")
    print(f"  - 작성자: {author}")
    print(f"  - 문제 번호: {problem_id}")
    print(f"  - 코드 파일: {main_file}")
    print(f"  - 언어: {language}")

if __name__ == "__main__":
    main()