#!/usr/bin/env python3
"""
scripts/fetch_boj_problem.py
백준에서 문제 정보를 수집합니다.
"""

import argparse
import json
import re
import requests
import time
from bs4 import BeautifulSoup

def get_solved_ac_info(problem_id):
    """solved.ac API에서 문제 정보 가져오기"""
    try:
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("titleKo", ""),
                "level": data.get("level", 0),
                "tags": [tag["displayNames"][0]["name"] for tag in data.get("tags", [])]
            }
    except Exception as e:
        print(f"solved.ac API 오류: {e}")
    
    return {}

def scrape_boj_problem(problem_id):
    """백준에서 문제 정보 스크래핑"""
    url = f"https://www.acmicpc.net/problem/{problem_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 문제가 존재하지 않는 경우
        if "존재하지 않는" in response.text or response.status_code == 404:
            return None
        
        # 문제 정보 추출
        problem_info = {}
        
        # 문제 설명
        desc_elem = soup.find('div', {'id': 'problem_description'})
        problem_info['description'] = desc_elem.get_text(strip=True) if desc_elem else ""
        
        # 입력 형식
        input_elem = soup.find('div', {'id': 'problem_input'})
        problem_info['input_format'] = input_elem.get_text(strip=True) if input_elem else ""
        
        # 출력 형식
        output_elem = soup.find('div', {'id': 'problem_output'})
        problem_info['output_format'] = output_elem.get_text(strip=True) if output_elem else ""
        
        # 제한사항
        limit_elem = soup.find('div', {'id': 'problem_limit'})
        problem_info['limits'] = limit_elem.get_text(strip=True) if limit_elem else ""
        
        # 예제 입출력
        samples = []
        sample_inputs = soup.find_all('pre', {'id': re.compile(r'sample_input_\d+')})
        sample_outputs = soup.find_all('pre', {'id': re.compile(r'sample_output_\d+')})
        
        for i, (inp, out) in enumerate(zip(sample_inputs, sample_outputs)):
            samples.append({
                "input": inp.get_text().strip(),
                "output": out.get_text().strip(),
                "case_number": i + 1
            })
        
        problem_info['samples'] = samples
        
        return problem_info
        
    except Exception as e:
        print(f"백준 스크래핑 오류: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='백준 문제 정보 수집')
    parser.add_argument('--problem-id', required=True, help='백준 문제 번호')
    args = parser.parse_args()
    
    problem_id = args.problem_id
    
    print(f"📥 문제 {problem_id} 정보 수집 중...")
    
    # solved.ac 정보 수집
    solved_ac_info = get_solved_ac_info(problem_id)
    
    # 백준 상세 정보 수집
    time.sleep(1)  # Rate limiting
    boj_info = scrape_boj_problem(problem_id)
    
    if not boj_info:
        print(f"::error::문제 {problem_id}를 찾을 수 없습니다.")
        # 빈 정보로라도 계속 진행
        boj_info = {
            "description": "",
            "input_format": "",
            "output_format": "",
            "limits": "",
            "samples": []
        }
    
    # 정보 통합
    complete_info = {
        "problem_id": problem_id,
        "title": solved_ac_info.get("title", f"문제 {problem_id}"),
        "level": solved_ac_info.get("level", 0),
        "tags": solved_ac_info.get("tags", []),
        **boj_info
    }
    
    # JSON 파일로 저장
    with open('problem_info.json', 'w', encoding='utf-8') as f:
        json.dump(complete_info, f, ensure_ascii=False, indent=2)
    
    # 샘플 테스트케이스 별도 저장
    sample_tests = {
        "problem_id": problem_id,
        "test_cases": complete_info['samples']
    }
    
    with open('sample_tests.json', 'w', encoding='utf-8') as f:
        json.dump(sample_tests, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 문제 정보 수집 완료:")
    print(f"  - 제목: {complete_info['title']}")
    print(f"  - 샘플 테스트케이스: {len(complete_info['samples'])}개")
    print(f"  - 태그: {', '.join(complete_info['tags'][:3])}")

if __name__ == "__main__":
    main()