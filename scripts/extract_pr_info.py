#!/usr/bin/env python3
"""
scripts/extract_pr_info.py
워크플로우로부터 전달받은 파일 경로에서 작성자, 문제 번호 등의 정보를 추출합니다.
"""

import os
import re
import sys

def extract_info_from_path(file_path):
    """
    '이름/문제번호/Main.java' 형식의 파일 경로에서 정보를 추출합니다.
    - 예시: '민영재/1001/Main.java' -> ('민영재', '1001')
    """
    # OS에 상관없이 경로를 처리하기 위해 정규식 사용
    # 패턴: (슬래시가 아닌 문자들)/(숫자들)/Main.java
    pattern = re.compile(r"^(?P<author>[^/\\]+)[/\\](?P<problem_id>\d+)[/\\]Main\.java$")
    match = pattern.match(file_path)

    if match:
        author = match.group('author')
        problem_id = match.group('problem_id')
        print(f"✅ Path analysis successful: Author='{author}', ProblemID='{problem_id}'")
        return author, problem_id

    print(f"❌ Path analysis failed for: {file_path}. Returning default values.")
    return 'unknown', '0000'

def write_github_output(data):
    """추출한 정보를 GitHub Actions의 다음 단계로 전달하기 위해 출력 파일에 씁니다."""
    output_file = os.environ.get('GITHUB_OUTPUT')
    if not output_file:
        print("⚠️ GITHUB_OUTPUT environment variable not set. Cannot pass outputs.")
        return

    print("\n📤 Writing to GITHUB_OUTPUT:")
    with open(output_file, 'a') as f:
        for key, value in data.items():
            line = f"{key}={value}\n"
            f.write(line)
            print(f"   {line.strip()}")

def main():
    """스크립트의 메인 실행 함수"""
    print("🚀 Starting PR Info Extraction...")

    # 1. 워크플로우에서 설정한 환경 변수로부터 파일 경로를 읽어옵니다.
    main_file = os.environ.get('MAIN_JAVA_FILE_PATH')

    if not main_file:
        print("❌ Error: MAIN_JAVA_FILE_PATH environment variable is not set.")
        sys.exit(1)

    print(f"🎯 File path received from workflow: {main_file}")

    # 2. 파일 경로에서 정보 추출
    author, problem_id = extract_info_from_path(main_file)

    # 3. 출력할 데이터 구성
    output_data = {
        'problem_id': problem_id,
        'code_file': main_file,
        'language': 'java' if main_file.endswith('.java') else 'unknown',
        'author': author
    }

    # 4. 결과를 GitHub Actions 출력으로 전달
    write_github_output(output_data)

    print("\n✅ Extraction complete!")

if __name__ == "__main__":
    main()