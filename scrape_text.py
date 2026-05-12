import re
from collections import Counter

# Read the content
with open(r"C:\Users\seif alaa\.gemini\antigravity\brain\eab2812f-3ab3-42cd-b87e-81cc49def807\.system_generated\steps\5\content.md", "r", encoding="utf-8") as f:
    text = f.read()

# Extract the body
# From the markdown, the body seems to start at "## مول ذا كور الشيخ زايد Mall Za Core Sheikh Zayed"
# and ends around "## بروشور وصور Za Core Mall Sheikh Zayed"
start_str = "## مول ذا كور الشيخ زايد Mall Za Core Sheikh Zayed"
end_str = "## بروشور وصور Za Core Mall Sheikh Zayed"

start_idx = text.find(start_str)
end_idx = text.find(end_str)

if start_idx != -1 and end_idx != -1:
    body = text[start_idx:end_idx]
else:
    body = text

# Clean body text from markdown links, headers, etc.
body = re.sub(r'#+\s', '', body)
body = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', body)
body = re.sub(r'[-*]\s', '', body)

sentences = [s.strip() for s in re.split(r'[.،:؟\n]+', body) if len(s.strip()) > 10]

# Now, we want to extract words. 
# The user said: "you cannot give me a frequency for a word x and then a sentence below has still the word, it mustn't be repeated"
# This likely means: If we extract unique terms, we shouldn't show them if they are already inside the sentences we list?
# Or maybe they want to partition the text into disjoint chunks?
# What if we just find the most frequent N words, and then for the sentences, we ONLY list sentences that DO NOT contain these N words?
# Let's count words first.

words = [w for w in re.findall(r'\b[\w\u0600-\u06FF]+\b', body) if not w.isnumeric()]
# stop words
stopwords = set(["في", "من", "على", "إلى", "عن", "مع", "أن", "هذا", "هذه", "أو", "لا", "بين", "كما", "ما", "لم", "ولكن", "كل", "التي", "الذي", "و", "قد", "فهنا", "فقد"])

words = [w for w in words if w not in stopwords and len(w) > 2]
word_counts = Counter(words)

# Top 20 words
top_words = [w for w, c in word_counts.most_common(20)]

# Sentences without the top words? If we do that, we might have 0 sentences.
# Wait, "you cannot give me a frequency for a word x and then a sentence below has still the word"
# What if the user means: DO NOT give me a list of words, just give me a frequency of words/sentences in a mutually exclusive way? 
# i.e., "I want to see what is repeated, but if a long phrase/sentence is repeated, don't count its individual words." 
# Since they said: "common words & sentences ... the words cannot be repeated"
# Let's find common sentences first. If a sentence is repeated, count it. Then remove it from the text before counting words!

sentence_counts = Counter(sentences)
common_sentences = {s: c for s, c in sentence_counts.items() if c >= 1}

# Let's just output the text analysis to a json or txt to see.
with open("scrape_output.txt", "w", encoding="utf-8") as f:
    f.write("--- WORD COUNTS ---\n")
    for w, c in word_counts.most_common(30):
        f.write(f"{w}: {c}\n")
        
    f.write("\n--- SENTENCES ---\n")
    for s, c in sentence_counts.most_common(30):
        f.write(f"{s}: {c}\n")
