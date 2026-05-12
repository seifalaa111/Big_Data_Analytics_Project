import re
from collections import Counter

with open(r"C:\Users\seif alaa\.gemini\antigravity\brain\eab2812f-3ab3-42cd-b87e-81cc49def807\.system_generated\steps\5\content.md", "r", encoding="utf-8") as f:
    text = f.read()

start_str = "## مول ذا كور الشيخ زايد Mall Za Core Sheikh Zayed"
end_str = "## بروشور وصور Za Core Mall Sheikh Zayed"

start_idx = text.find(start_str)
end_idx = text.find(end_str)

body = text[start_idx:end_idx] if start_idx != -1 and end_idx != -1 else text

body = re.sub(r'#+\s', '', body)
body = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', body)
body = re.sub(r'[-*]\s', '', body)

sentences = [s.strip() for s in re.split(r'[.،:؟\n]+', body) if len(s.strip()) > 10]

words = [w for w in re.findall(r'\b[\w\u0600-\u06FF]+\b', body) if not w.isnumeric()]
stopwords = set(["في", "من", "على", "إلى", "عن", "مع", "أن", "هذا", "هذه", "أو", "لا", "بين", "كما", "ما", "لم", "ولكن", "كل", "التي", "الذي", "و", "قد", "فهنا", "فقد"])
words = [w for w in words if w not in stopwords and len(w) > 2]

word_counts = Counter(words)
sentence_counts = Counter(sentences)

# Get top words
top_words = [w for w, c in word_counts.most_common(15)]

# Filter sentences that do NOT contain ANY of the top words
filtered_sentences = []
for s in sentences:
    has_top_word = False
    for tw in top_words:
        if re.search(rf'\b{tw}\b', s):
            has_top_word = True
            break
    if not has_top_word:
        filtered_sentences.append(s)

filtered_sentence_counts = Counter(filtered_sentences)

with open("scrape_output2.txt", "w", encoding="utf-8") as f:
    f.write("--- TOP 15 WORDS ---\n")
    for w in top_words:
        f.write(f"{w}: {word_counts[w]}\n")
        
    f.write("\n--- FILTERED SENTENCES (NO TOP WORDS) ---\n")
    for s, c in filtered_sentence_counts.most_common(20):
        f.write(f"{s}: {c}\n")
