import sys
import os

# Add the parent directory to the path so we can import core.classifier
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.classifier import classify_dispute

def test():
    test_prompts = [
        "My boss fired me without paying my last salary.",
        "Someone hacked my facebook account and is asking friends for money.",
        "I need a divorce from my husband, he is very abusive.",
        "The builder is refusing to give possession of the flat.",
        "A truck hit my bike yesterday and broke my leg.",
        "General inquiry about how to file a case in court."
    ]

    print("--- Testing Fine-Tuned InLegalBERT Classifier ---")
    
    for prompt in test_prompts:
        print(f"\nUser Query: '{prompt}'")
        category, process, court = classify_dispute(prompt)
        print(f"-> Classification: {category}")
        print(f"-> Process:        {process}")
        print(f"-> Court:          {court}")

if __name__ == "__main__":
    test()
