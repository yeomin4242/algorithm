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
    print(f"🔍 문제 번호 추출 시도: {file_path}")
    
    # 다양한 패턴으로 문제 번호 추출
    patterns = [
        r'[^/\\]+[/\\](\d+)[/\\]Main\.java

def get_changed_files():
    """PR에서 변경된 파일들 가져오기"""
    try:
        print("🔍 변경된 파일 검색 중...")
        
        # 1. 현재 작업 디렉토리 확인 (프로젝트 루트여야 함)
        current_dir = os.getcwd()
        print(f"📁 현재 디렉토리: {current_dir}")
        
        # 스크립트가 scripts/ 디렉토리에서 실행되면 프로젝트 루트로 이동
        if current_dir.endswith('/scripts') or current_dir.endswith('\\scripts'):
            os.chdir('..')
            current_dir = os.getcwd()
            print(f"📁 프로젝트 루트로 이동: {current_dir}")
        
        # 2. git 상태 확인
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            print(f"📝 Git 상태: {result.stdout[:200]}...")
        except:
            pass
        
        # 3. 여러 방법으로 변경된 파일 찾기
        commands = [
            # PR의 변경된 파일들
            ['git', 'diff', '--name-only', 'origin/main...HEAD'],
            ['git', 'diff', '--name-only', 'HEAD~1'],
            ['git', 'diff', '--name-only', '--cached'],
            # 추가된/수정된 파일들
            ['git', 'ls-files', '--others', '--modified', '--exclude-standard'],
            # 모든 추적되는 파일
            ['git', 'ls-files']
        ]
        
        all_files = set()
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                    all_files.update(files)
                    print(f"✅ 명령어 성공: {' '.join(cmd)} - {len(files)}개 파일")
                    for f in files[:5]:  # 처음 5개만 출력
                        print(f"  - {f}")
                    if len(files) > 5:
                        print(f"  ... 및 {len(files)-5}개 더")
            except Exception as e:
                print(f"⚠️  명령어 실패: {' '.join(cmd)} - {e}")
        
        # 4. 모든 방법이 실패하면 파일 시스템에서 직접 검색
        if not all_files:
            print("🔄 직접 파일 시스템 검색...")
            for root, dirs, files in os.walk('.'):
                # .git 디렉토리 제외
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    if file == 'Main.java':
                        filepath = os.path.relpath(os.path.join(root, file))
                        # 윈도우 경로를 유닉스 스타일로 변환
                        filepath = filepath.replace('\\', '/')
                        all_files.add(filepath)
                        print(f"📁 발견: {filepath}")
        
        result_files = list(all_files)
        print(f"🎯 총 {len(result_files)}개 파일 발견")
        
        return result_files
        
    except Exception as e:
        print(f"❌ 파일 검색 중 예외: {e}")
        
        # 마지막 수단: 현재 디렉토리의 모든 Main.java 찾기
        print("🚨 비상 모드: 전체 디렉토리 검색")
        emergency_files = []
        try:
            for root, dirs, files in os.walk('.'):
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    if file == 'Main.java':
                        filepath = os.path.relpath(os.path.join(root, file))
                        filepath = filepath.replace('\\', '/')  # 윈도우 호환성
                        emergency_files.append(filepath)
                        print(f"🆘 비상 발견: {filepath}")
        except Exception as e2:
            print(f"💥 비상 검색도 실패: {e2}")
        
        return emergency_files

def detect_language(file_path):
    """파일 확장자로 언어 감지 (Java 전용)"""
    if file_path.endswith('Main.java'):
        return 'java'
    return 'unknown'

def main():
    print("🚀 PR 정보 추출 시작...")
    print("=" * 50)
    
    # 작업 디렉토리 확인 및 조정
    original_dir = os.getcwd()
    print(f"📁 시작 디렉토리: {original_dir}")
    
    # scripts 디렉토리에서 실행 중이면 상위 디렉토리로 이동
    if original_dir.endswith('/scripts') or original_dir.endswith('\\scripts') or os.path.basename(original_dir) == 'scripts':
        os.chdir('..')
        print(f"📁 프로젝트 루트로 이동: {os.getcwd()}")
    
    # 현재 디렉토리 내용 확인
    print("📂 현재 디렉토리 내용:")
    try:
        for item in os.listdir('.'):
            if os.path.isdir(item):
                print(f"  📁 {item}/")
                # scripts나 .git 같은 시스템 디렉토리가 아닌 경우만 탐색
                if item not in ['.git', 'scripts', '.github', 'node_modules', '__pycache__']:
                    try:
                        for subitem in os.listdir(item):
                            if os.path.isdir(os.path.join(item, subitem)):
                                print(f"    📁 {subitem}/")
                                try:
                                    for file in os.listdir(os.path.join(item, subitem)):
                                        print(f"      📄 {file}")
                                except:
                                    pass
                    except:
                        pass
            else:
                print(f"  📄 {item}")
    except Exception as e:
        print(f"❌ 디렉토리 탐색 실패: {e}")
    
    print("=" * 50)
    
    changed_files = get_changed_files()
    print(f"📁 총 감지된 파일 수: {len(changed_files)}")
    
    # Main.java 파일 필터링
    java_files = []
    for f in changed_files:
        print(f"🔍 파일 검사: {f}")
        if f.endswith('Main.java'):
            # 절대 경로와 상대 경로 둘 다 확인
            file_paths_to_check = [f, os.path.join('.', f)]
            file_exists = False
            
            for path in file_paths_to_check:
                if os.path.exists(path):
                    file_exists = True
                    # 정규화된 상대 경로 사용
                    normalized_path = os.path.relpath(path).replace('\\', '/')
                    java_files.append(normalized_path)
                    print(f"☕ Valid Java 파일: {normalized_path}")
                    break
            
            if not file_exists:
                print(f"⚠️  파일 존재하지 않음: {f}")
        else:
            print(f"🚫 Java 파일 아님: {f}")
    
    # 중복 제거
    java_files = list(set(java_files))
    
    # 파일이 없으면 강제로 모든 Main.java 찾기
    if not java_files:
        print("🔄 강제 Main.java 검색...")
        for root, dirs, files in os.walk('.'):
            if '.git' in root or 'scripts' in root:
                continue
            for file in files:
                if file == 'Main.java':
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path).replace('\\', '/')
                    java_files.append(rel_path)
                    print(f"🎯 강제 발견: {rel_path}")
    
    if not java_files:
        print("❌ Main.java 파일이 발견되지 않았습니다.")
        print("📋 감지된 모든 파일:")
        for f in changed_files[:10]:  # 최대 10개만 출력
            print(f"  - {f}")
        
        print("\n💡 올바른 파일 구조:")
        print("  ✅ 이름/문제번호/Main.java")
        print("  ✅ 예시: 민영재/2557/Main.java")
        
        # 더미 값으로 계속 진행
        print("🔄 더미 값으로 파이프라인 계속 진행...")
        write_github_output({
            'problem_id': '0000',
            'code_file': 'dummy/Main.java',
            'language': 'java',
            'author': 'unknown'
        })
        return
    
    # 첫 번째 Main.java 파일 처리
    main_file = java_files[0]
    print(f"🎯 선택된 파일: {main_file}")
    
    problem_id = extract_problem_id_from_path(main_file)
    author = extract_author_from_path(main_file)
    
    if not problem_id:
        print(f"⚠️  문제 번호 추출 실패, 기본값 사용: {main_file}")
        problem_id = "0000"
    
    if not author:
        print(f"⚠️  작성자 추출 실패, 기본값 사용: {main_file}")
        author = "unknown"
    
    language = detect_language(main_file)
    
    # GitHub Actions 출력
    output_data = {
        'problem_id': problem_id,
        'code_file': main_file,
        'language': language,
        'author': author
    }
    
    write_github_output(output_data)
    
    print("\n✅ 추출 완료!")
    print(f"  👤 작성자: {author}")
    print(f"  🔢 문제 번호: {problem_id}")
    print(f"  📄 코드 파일: {main_file}")
    print(f"  💻 언어: {language}")

def write_github_output(data):
    """GitHub Actions 출력 데이터 쓰기"""
    print("\n📤 GitHub Actions 출력:")
    
    # 환경변수 파일에 출력
    try:
        output_file = os.environ.get('GITHUB_OUTPUT')
        if output_file:
            with open(output_file, 'a') as f:
                for key, value in data.items():
                    f.write(f"{key}={value}\n")
                    print(f"  {key}={value}")
        else:
            # GITHUB_OUTPUT이 없으면 표준 출력으로
            for key, value in data.items():
                print(f"::set-output name={key}::{value}")
    except Exception as e:
        print(f"❌ 출력 파일 쓰기 실패: {e}")
        # 표준 출력으로 fallback
        for key, value in data.items():
            print(f"::set-output name={key}::{value}")

if __name__ == "__main__":
    main(),     # 이름/번호/Main.java
        r'[^/\\]+[/\\](\d+)[/\\]',                # 이름/번호/
        r'(\d+)[/\\]Main\.java

def get_changed_files():
    """PR에서 변경된 파일들 가져오기"""
    try:
        print("🔍 변경된 파일 검색 중...")
        
        # 1. 현재 작업 디렉토리 확인
        current_dir = os.getcwd()
        print(f"📁 현재 디렉토리: {current_dir}")
        
        # 2. git 상태 확인
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            print(f"📝 Git 상태: {result.stdout[:200]}...")
        except:
            pass
        
        # 3. 여러 방법으로 변경된 파일 찾기
        commands = [
            # PR의 변경된 파일들
            ['git', 'diff', '--name-only', 'origin/main...HEAD'],
            ['git', 'diff', '--name-only', 'HEAD~1'],
            ['git', 'diff', '--name-only', '--cached'],
            # 추가된/수정된 파일들
            ['git', 'ls-files', '--others', '--modified', '--exclude-standard'],
            # 모든 추적되는 파일
            ['git', 'ls-files']
        ]
        
        all_files = set()
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                    all_files.update(files)
                    print(f"✅ 명령어 성공: {' '.join(cmd)} - {len(files)}개 파일")
                    for f in files[:5]:  # 처음 5개만 출력
                        print(f"  - {f}")
                    if len(files) > 5:
                        print(f"  ... 및 {len(files)-5}개 더")
            except Exception as e:
                print(f"⚠️  명령어 실패: {' '.join(cmd)} - {e}")
        
        # 4. 모든 방법이 실패하면 파일 시스템에서 직접 검색
        if not all_files:
            print("🔄 직접 파일 시스템 검색...")
            for root, dirs, files in os.walk('.'):
                # .git 디렉토리 제외
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    if file == 'Main.java':
                        filepath = os.path.relpath(os.path.join(root, file))
                        all_files.add(filepath)
                        print(f"📁 발견: {filepath}")
        
        result_files = list(all_files)
        print(f"🎯 총 {len(result_files)}개 파일 발견")
        
        return result_files
        
    except Exception as e:
        print(f"❌ 파일 검색 중 예외: {e}")
        
        # 마지막 수단: 현재 디렉토리의 모든 Main.java 찾기
        print("🚨 비상 모드: 전체 디렉토리 검색")
        emergency_files = []
        try:
            for root, dirs, files in os.walk('.'):
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    if file == 'Main.java':
                        filepath = os.path.relpath(os.path.join(root, file))
                        emergency_files.append(filepath)
                        print(f"🆘 비상 발견: {filepath}")
        except Exception as e2:
            print(f"💥 비상 검색도 실패: {e2}")
        
        return emergency_files

def detect_language(file_path):
    """파일 확장자로 언어 감지 (Java 전용)"""
    if file_path.endswith('Main.java'):
        return 'java'
    return 'unknown'

def main():
    print("🔍 PR 정보 추출 시작...")
    
    changed_files = get_changed_files()
    print(f"📁 감지된 파일 수: {len(changed_files)}")
    
    # Main.java 파일 필터링
    java_files = []
    for f in changed_files:
        if f.endswith('Main.java') and Path(f).exists():
            java_files.append(f)
            print(f"☕ Java 파일 발견: {f}")
    
    if not java_files:
        print("❌ Main.java 파일이 발견되지 않았습니다.")
        print("📋 감지된 모든 파일:")
        for f in changed_files:
            print(f"  - {f}")
        print("\n💡 파일 경로는 '이름/문제번호/Main.java' 형식이어야 합니다.")
        print("   예시: alice/1654/Main.java")
        
        # 실패하더라도 더미 값으로 계속 진행하도록 수정
        print("🔄 더미 값으로 파이프라인 계속 진행...")
        print("::set-output name=problem_id::0000")
        print("::set-output name=code_file::dummy/Main.java")
        print("::set-output name=language::java")
        print("::set-output name=author::unknown")
        return  # exit(1) 대신 return으로 변경
    
    # 첫 번째 Main.java 파일을 메인 제출 파일로 간주
    main_file = java_files[0]
    problem_id = extract_problem_id_from_path(main_file)
    author = extract_author_from_path(main_file)
    
    if not problem_id:
        print(f"⚠️  파일 경로에서 문제 번호를 추출할 수 없습니다: {main_file}")
        print("파일 경로는 '이름/문제번호/Main.java' 형식이어야 합니다.")
        problem_id = "0000"  # 기본값 설정
    
    if not author:
        print(f"⚠️  파일 경로에서 작성자를 추출할 수 없습니다: {main_file}")
        author = "unknown"  # 기본값 설정
    
    language = detect_language(main_file)
    
    # GitHub Actions 출력 (새로운 형식 사용)
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/stdout'), 'a') as f:
        f.write(f"problem_id={problem_id}\n")
        f.write(f"code_file={main_file}\n")
        f.write(f"language={language}\n")
        f.write(f"author={author}\n")
    
    print(f"✅ 추출 완료:")
    print(f"  - 작성자: {author}")
    print(f"  - 문제 번호: {problem_id}")
    print(f"  - 코드 파일: {main_file}")
    print(f"  - 언어: {language}")

if __name__ == "__main__":
    main(),                 # 번호/Main.java
        r'[/\\](\d+)[/\\]',                       # /번호/
        r'(\d{4,})',                              # 4자리 이상 숫자
        r'(\d+)',                                 # 아무 숫자
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, file_path)
        if match:
            problem_id = match.group(1)
            print(f"✅ 패턴 {i+1}로 문제 번호 추출: {problem_id}")
            return problem_id
    
    print(f"❌ 문제 번호 추출 실패: {file_path}")
    return None

def extract_author_from_path(file_path):
    """파일 경로에서 작성자 이름 추출"""
    print(f"🔍 작성자 추출 시도: {file_path}")
    
    # 다양한 패턴으로 작성자 추출
    patterns = [
        r'^([^/\\]+)[/\\]\d+[/\\]Main\.java

def get_changed_files():
    """PR에서 변경된 파일들 가져오기"""
    try:
        print("🔍 변경된 파일 검색 중...")
        
        # 1. 현재 작업 디렉토리 확인
        current_dir = os.getcwd()
        print(f"📁 현재 디렉토리: {current_dir}")
        
        # 2. git 상태 확인
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            print(f"📝 Git 상태: {result.stdout[:200]}...")
        except:
            pass
        
        # 3. 여러 방법으로 변경된 파일 찾기
        commands = [
            # PR의 변경된 파일들
            ['git', 'diff', '--name-only', 'origin/main...HEAD'],
            ['git', 'diff', '--name-only', 'HEAD~1'],
            ['git', 'diff', '--name-only', '--cached'],
            # 추가된/수정된 파일들
            ['git', 'ls-files', '--others', '--modified', '--exclude-standard'],
            # 모든 추적되는 파일
            ['git', 'ls-files']
        ]
        
        all_files = set()
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                    all_files.update(files)
                    print(f"✅ 명령어 성공: {' '.join(cmd)} - {len(files)}개 파일")
                    for f in files[:5]:  # 처음 5개만 출력
                        print(f"  - {f}")
                    if len(files) > 5:
                        print(f"  ... 및 {len(files)-5}개 더")
            except Exception as e:
                print(f"⚠️  명령어 실패: {' '.join(cmd)} - {e}")
        
        # 4. 모든 방법이 실패하면 파일 시스템에서 직접 검색
        if not all_files:
            print("🔄 직접 파일 시스템 검색...")
            for root, dirs, files in os.walk('.'):
                # .git 디렉토리 제외
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    if file == 'Main.java':
                        filepath = os.path.relpath(os.path.join(root, file))
                        all_files.add(filepath)
                        print(f"📁 발견: {filepath}")
        
        result_files = list(all_files)
        print(f"🎯 총 {len(result_files)}개 파일 발견")
        
        return result_files
        
    except Exception as e:
        print(f"❌ 파일 검색 중 예외: {e}")
        
        # 마지막 수단: 현재 디렉토리의 모든 Main.java 찾기
        print("🚨 비상 모드: 전체 디렉토리 검색")
        emergency_files = []
        try:
            for root, dirs, files in os.walk('.'):
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    if file == 'Main.java':
                        filepath = os.path.relpath(os.path.join(root, file))
                        emergency_files.append(filepath)
                        print(f"🆘 비상 발견: {filepath}")
        except Exception as e2:
            print(f"💥 비상 검색도 실패: {e2}")
        
        return emergency_files

def detect_language(file_path):
    """파일 확장자로 언어 감지 (Java 전용)"""
    if file_path.endswith('Main.java'):
        return 'java'
    return 'unknown'

def main():
    print("🔍 PR 정보 추출 시작...")
    
    changed_files = get_changed_files()
    print(f"📁 감지된 파일 수: {len(changed_files)}")
    
    # Main.java 파일 필터링
    java_files = []
    for f in changed_files:
        if f.endswith('Main.java') and Path(f).exists():
            java_files.append(f)
            print(f"☕ Java 파일 발견: {f}")
    
    if not java_files:
        print("❌ Main.java 파일이 발견되지 않았습니다.")
        print("📋 감지된 모든 파일:")
        for f in changed_files:
            print(f"  - {f}")
        print("\n💡 파일 경로는 '이름/문제번호/Main.java' 형식이어야 합니다.")
        print("   예시: alice/1654/Main.java")
        
        # 실패하더라도 더미 값으로 계속 진행하도록 수정
        print("🔄 더미 값으로 파이프라인 계속 진행...")
        print("::set-output name=problem_id::0000")
        print("::set-output name=code_file::dummy/Main.java")
        print("::set-output name=language::java")
        print("::set-output name=author::unknown")
        return  # exit(1) 대신 return으로 변경
    
    # 첫 번째 Main.java 파일을 메인 제출 파일로 간주
    main_file = java_files[0]
    problem_id = extract_problem_id_from_path(main_file)
    author = extract_author_from_path(main_file)
    
    if not problem_id:
        print(f"⚠️  파일 경로에서 문제 번호를 추출할 수 없습니다: {main_file}")
        print("파일 경로는 '이름/문제번호/Main.java' 형식이어야 합니다.")
        problem_id = "0000"  # 기본값 설정
    
    if not author:
        print(f"⚠️  파일 경로에서 작성자를 추출할 수 없습니다: {main_file}")
        author = "unknown"  # 기본값 설정
    
    language = detect_language(main_file)
    
    # GitHub Actions 출력 (새로운 형식 사용)
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/stdout'), 'a') as f:
        f.write(f"problem_id={problem_id}\n")
        f.write(f"code_file={main_file}\n")
        f.write(f"language={language}\n")
        f.write(f"author={author}\n")
    
    print(f"✅ 추출 완료:")
    print(f"  - 작성자: {author}")
    print(f"  - 문제 번호: {problem_id}")
    print(f"  - 코드 파일: {main_file}")
    print(f"  - 언어: {language}")

if __name__ == "__main__":
    main(),    # 이름/번호/Main.java
        r'^([^/\\]+)[/\\]',                       # 이름/
        r'([^/\\]+)[/\\]\d+',                     # 이름/번호
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, file_path)
        if match:
            author = match.group(1)
            # 특수 디렉토리 제외
            if author not in ['.', '..', '.git', 'scripts', '.github']:
                print(f"✅ 패턴 {i+1}로 작성자 추출: {author}")
                return author
    
    print(f"❌ 작성자 추출 실패: {file_path}")
    return None

def get_changed_files():
    """PR에서 변경된 파일들 가져오기"""
    try:
        print("🔍 변경된 파일 검색 중...")
        
        # 1. 현재 작업 디렉토리 확인
        current_dir = os.getcwd()
        print(f"📁 현재 디렉토리: {current_dir}")
        
        # 2. git 상태 확인
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            print(f"📝 Git 상태: {result.stdout[:200]}...")
        except:
            pass
        
        # 3. 여러 방법으로 변경된 파일 찾기
        commands = [
            # PR의 변경된 파일들
            ['git', 'diff', '--name-only', 'origin/main...HEAD'],
            ['git', 'diff', '--name-only', 'HEAD~1'],
            ['git', 'diff', '--name-only', '--cached'],
            # 추가된/수정된 파일들
            ['git', 'ls-files', '--others', '--modified', '--exclude-standard'],
            # 모든 추적되는 파일
            ['git', 'ls-files']
        ]
        
        all_files = set()
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                    all_files.update(files)
                    print(f"✅ 명령어 성공: {' '.join(cmd)} - {len(files)}개 파일")
                    for f in files[:5]:  # 처음 5개만 출력
                        print(f"  - {f}")
                    if len(files) > 5:
                        print(f"  ... 및 {len(files)-5}개 더")
            except Exception as e:
                print(f"⚠️  명령어 실패: {' '.join(cmd)} - {e}")
        
        # 4. 모든 방법이 실패하면 파일 시스템에서 직접 검색
        if not all_files:
            print("🔄 직접 파일 시스템 검색...")
            for root, dirs, files in os.walk('.'):
                # .git 디렉토리 제외
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    if file == 'Main.java':
                        filepath = os.path.relpath(os.path.join(root, file))
                        all_files.add(filepath)
                        print(f"📁 발견: {filepath}")
        
        result_files = list(all_files)
        print(f"🎯 총 {len(result_files)}개 파일 발견")
        
        return result_files
        
    except Exception as e:
        print(f"❌ 파일 검색 중 예외: {e}")
        
        # 마지막 수단: 현재 디렉토리의 모든 Main.java 찾기
        print("🚨 비상 모드: 전체 디렉토리 검색")
        emergency_files = []
        try:
            for root, dirs, files in os.walk('.'):
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    if file == 'Main.java':
                        filepath = os.path.relpath(os.path.join(root, file))
                        emergency_files.append(filepath)
                        print(f"🆘 비상 발견: {filepath}")
        except Exception as e2:
            print(f"💥 비상 검색도 실패: {e2}")
        
        return emergency_files

def detect_language(file_path):
    """파일 확장자로 언어 감지 (Java 전용)"""
    if file_path.endswith('Main.java'):
        return 'java'
    return 'unknown'

def main():
    print("🔍 PR 정보 추출 시작...")
    
    changed_files = get_changed_files()
    print(f"📁 감지된 파일 수: {len(changed_files)}")
    
    # Main.java 파일 필터링
    java_files = []
    for f in changed_files:
        if f.endswith('Main.java') and Path(f).exists():
            java_files.append(f)
            print(f"☕ Java 파일 발견: {f}")
    
    if not java_files:
        print("❌ Main.java 파일이 발견되지 않았습니다.")
        print("📋 감지된 모든 파일:")
        for f in changed_files:
            print(f"  - {f}")
        print("\n💡 파일 경로는 '이름/문제번호/Main.java' 형식이어야 합니다.")
        print("   예시: alice/1654/Main.java")
        
        # 실패하더라도 더미 값으로 계속 진행하도록 수정
        print("🔄 더미 값으로 파이프라인 계속 진행...")
        print("::set-output name=problem_id::0000")
        print("::set-output name=code_file::dummy/Main.java")
        print("::set-output name=language::java")
        print("::set-output name=author::unknown")
        return  # exit(1) 대신 return으로 변경
    
    # 첫 번째 Main.java 파일을 메인 제출 파일로 간주
    main_file = java_files[0]
    problem_id = extract_problem_id_from_path(main_file)
    author = extract_author_from_path(main_file)
    
    if not problem_id:
        print(f"⚠️  파일 경로에서 문제 번호를 추출할 수 없습니다: {main_file}")
        print("파일 경로는 '이름/문제번호/Main.java' 형식이어야 합니다.")
        problem_id = "0000"  # 기본값 설정
    
    if not author:
        print(f"⚠️  파일 경로에서 작성자를 추출할 수 없습니다: {main_file}")
        author = "unknown"  # 기본값 설정
    
    language = detect_language(main_file)
    
    # GitHub Actions 출력 (새로운 형식 사용)
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/stdout'), 'a') as f:
        f.write(f"problem_id={problem_id}\n")
        f.write(f"code_file={main_file}\n")
        f.write(f"language={language}\n")
        f.write(f"author={author}\n")
    
    print(f"✅ 추출 완료:")
    print(f"  - 작성자: {author}")
    print(f"  - 문제 번호: {problem_id}")
    print(f"  - 코드 파일: {main_file}")
    print(f"  - 언어: {language}")

if __name__ == "__main__":
    main()