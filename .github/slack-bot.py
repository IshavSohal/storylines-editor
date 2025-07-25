import os
import json
import re
from transformers import pipeline

# Get the PR body and labels from environment variables
pr_body = os.environ.get('PR_BODY', '')
pr_labels_json = os.environ.get('PR_LABELS_JSON', '[]')
pr_labels = json.loads(pr_labels_json)

# Summarization (example model, could be adjusted)
summarizer = pipeline('summarization', model='tuner007/pegasus_summarizer')
neutral_summary = summarizer(pr_body, max_length=200, min_length=25, do_sample=False)[0]['summary_text']

# Characters we don’t want treated as part of the URL itself
TRAILING_PUNCT = '.,;:!?)\\]}"\''

# URL matcher regex
url_regex = re.compile(
    r'(https?://\S+|'          # full http/https URL
    r'www\.\S+|'               # www.example.com
    r'[A-Za-z0-9.-]+\.[A-Za-z]{2,}\S*)',   # bare domain + path
    re.IGNORECASE
)

def strip_unsafe_links(text: str) -> str:
    def replace_bad_links(m: re.Match) -> str:
        whole     = m.group(0)

        # Split into "URL part" and any trailing punctuation
        url_part  = whole.rstrip(TRAILING_PUNCT)
        trailing  = whole[len(url_part):]

        # Normalise so every comparison looks the same
        normalized = url_part
        if not normalized.lower().startswith(('http://', 'https://')):
            normalized = 'https://' + normalized

        # Keep only links in the ramp4-pcar4 org
        if normalized.lower().startswith('https://github.com/ramp4-pcar4'):
            return url_part + trailing         # keep + put the punctuation back

        # Everything else gets scrubbed
        return '(LINK EXPUNGED)' + trailing

    return url_regex.sub(replace_bad_links, text)

neutral_summary = strip_unsafe_links(neutral_summary)

# Replace all double quotes with single quotes in the summary
neutral_summary = neutral_summary.replace('"', "'")

# PR label types with associated metadata
pr_label_types = {
    'PR: Active': ['Active', 'https://github.com/search?q=org%3Aramp4-pcar4+state%3A%22open%22+type%3A%22pr%22+label%3A%22PR%3A+Active%22&type=pullrequests'],
    'PR: Build': ['Build', 'https://github.com/search?q=org%3Aramp4-pcar4+state%3A%22open%22+type%3A%22pr%22+label%3A%22PR%3A+Active%22%2C%22PR%3A+Build%22+&type=pullrequests'],
    'PR: Frontend': ['Frontend', 'https://github.com/search?q=org%3Aramp4-pcar4+state%3A%22open%22+type%3A%22pr%22+label%3A%22PR%3A+Active%22%2C%22PR%3A+Frontend%22+&type=pullrequests'],
    'PR: Geo': ['Geo', 'https://github.com/search?q=org%3Aramp4-pcar4+state%3A%22open%22+type%3A%22pr%22+label%3A%22PR%3A+Active%22%2C%22PR%3A+Geo%22+&type=pullrequests']
}

# Format PR label links as Slack mrkdwn links
pr_label_str = ", ".join(
    f"<{pr_label_types[label['name']][1]}|{pr_label_types[label['name']][0]}>"
    for label in pr_labels if pr_label_types.get(label['name'])
)
if (len(pr_label_str) == 0):
    pr_label_str = "None"

# Handle regular labels (not in pr_label_types)
reg_label_str = ", ".join(
    label['name'] for label in pr_labels if pr_label_types.get(label['name']) is None
)
if (len(reg_label_str) == 0):
    reg_label_str = "None"

# Write all results to environment
with open(os.environ['GITHUB_ENV'], 'a') as env_file:
    env_file.write(f'NEUTRAL_SUMMARY={neutral_summary}\n')
    env_file.write(f'PR_LABEL_STR={pr_label_str}\n')
    env_file.write(f'REG_LABEL_STR={reg_label_str}\n')
