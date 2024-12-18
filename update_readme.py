import requests
import os
import time
from collections import defaultdict

# GitHubユーザー名（変更しない場合）
USERNAME = "emon2358"

# GitHub API URL
USER_REPOS_API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"  # 100件のリポジトリを一度に取得
LANGUAGES_API_URL = "https://api.github.com/repos/{}/{}/languages"

# リポジトリの読み込みと、進行状況バーをMarkdownに書き出す関数
def fetch_and_update_readme():
    # ユーザーのリポジトリを取得
    response = requests.get(USER_REPOS_API_URL)
    if response.status_code == 200:
        repos = response.json()
        language_counts = defaultdict(int)
        total_lines = 0

        # 各リポジトリの言語データを取得して集計
        for repo in repos:
            repo_name = repo['name']
            language_response = requests.get(LANGUAGES_API_URL.format(USERNAME, repo_name))
            if language_response.status_code == 200:
                languages = language_response.json()
                for language, count in languages.items():
                    language_counts[language] += count
                    total_lines += count
        
        if total_lines == 0:
            print("No code found in repositories.")
            return
        
        # 言語の使用割合を計算
        language_percentages = {lang: (count / total_lines) * 100 for lang, count in language_counts.items()}
        
        # Markdown形式に変換
        markdown = generate_markdown(language_percentages)
        
        # README.mdを更新
        with open("README.md", "r") as file:
            readme_content = file.read()
        
        new_readme_content = update_readme_content(readme_content, markdown)
        
        # 更新された内容でREADME.mdを上書き
        with open("README.md", "w") as file:
            file.write(new_readme_content)
        
        print("README.md has been updated successfully.")
    else:
        print("Failed to fetch repositories from GitHub API.")

# Markdownを生成する関数
def generate_markdown(language_percentages):
    markdown = f"# Language Usage for {USERNAME}\n\n"
    for lang, percentage in sorted(language_percentages.items(), key=lambda x: x[1], reverse=True):
        filled = '█' * int(percentage // 2)
        unfilled = '░' * (50 - len(filled))
        markdown += f"{lang}: {filled}{unfilled} {percentage:.1f}%\n"
    return markdown

# README.mdの既存の内容に新しいMarkdownを埋め込む関数
def update_readme_content(existing_content, new_markdown):
    start_marker = "<!--START_LANGUAGE_USAGE-->"
    end_marker = "<!--END_LANGUAGE_USAGE-->"
    
    # マーカーが存在しない場合は、新しく追加
    if start_marker not in existing_content:
        updated_content = existing_content + "\n" + start_marker + "\n" + new_markdown + "\n" + end_marker
    else:
        # マーカー間の内容を更新
        updated_content = existing_content.split(start_marker)[0] + start_marker + "\n" + new_markdown + "\n" + end_marker + existing_content.split(end_marker)[1]
    
    return updated_content

# メインの処理ループ
if __name__ == "__main__":
    # 初回の更新
    fetch_and_update_readme()

    # 60分ごとに更新
    while True:
        time.sleep(3600)  # 3600秒 (1時間)
        fetch_and_update_readme()
