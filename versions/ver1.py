import os

def load_wordlist(filename="wordlist"):
    """
    Load dictionary words from a file, one word per line.
    Returns list of words in lowercase.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found in current directory.")
    words = []
    with open(filename, "r") as f:
        for line in f:
            word = line.strip().lower()
            if word:
                words.append(word)
    return words

def load_keymap_conf(filename="keymap.conf"):
    """
    Load keyboard proximity mapping from a file.
    Format example per line:
    o:i,k,l,p,0,9
    i:o,u,j,k
    ...
    Returns dictionary like {'o': ['i', 'k', 'l', 'p', '0', '9'], ...}
    """
    keymap = {}
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found in current directory.")
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip empty lines and comments
            if ":" not in line:
                continue  # skip malformed lines
            key, neighbors = line.split(":", 1)
            neighbor_keys = [k.strip().lower() for k in neighbors.split(",") if k.strip()]
            keymap[key.lower()] = neighbor_keys
    return keymap

def are_keys_nearby(c1, c2, nearby_keys):
    """Check if two characters are nearby on the keyboard based on mapping."""
    c1, c2 = c1.lower(), c2.lower()
    return c2 in nearby_keys.get(c1, [])

def modified_levenshtein_ratio(word1, word2, nearby_keys):
    """
    Compute a similarity ratio between 0 and 1.
    If a substitution involves nearby keys, count it as smaller penalty.
    """
    len1, len2 = len(word1), len(word2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            c1 = word1[i - 1]
            c2 = word2[j - 1]
            if c1 == c2:
                cost = 0
            elif are_keys_nearby(c1, c2, nearby_keys):
                cost = 0.5  # smaller penalty for nearby key substitution
            else:
                cost = 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,       # deletion
                dp[i][j - 1] + 1,       # insertion
                dp[i - 1][j - 1] + cost # substitution
            )
    dist = dp[len1][len2]
    max_len = max(len1, len2) if max(len1, len2) != 0 else 1
    ratio = 1 - dist / max_len
    return ratio

def autocorrect(word, dictionary, threshold=0.75, max_suggestions=5, nearby_keys=None):
    """
    Find corrections for the input word from dictionary.
    Returns (best_match or None, list_of_suggestions)
    """
    if nearby_keys is None:
        nearby_keys = {}

    word = word.lower()
    similarities = []
    for w in dictionary:
        sim = modified_levenshtein_ratio(word, w, nearby_keys)
        if sim >= threshold:
            similarities.append((w, sim))
    similarities.sort(key=lambda x: x[1], reverse=True)

    if not similarities:
        return None, []

    best_match, best_score = similarities[0]
    suggestions = [w for w, _ in similarities[:max_suggestions]]

    if best_score > 0.90:
        return best_match, suggestions
    else:
        return None, suggestions

def yes_no_prompt(prompt):
    """Prompt user for yes/no, returns True for yes, False for no."""
    while True:
        answer = input(prompt + " [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        else:
            print("Please enter 'y' or 'n'.")

def main():
    try:
        dictionary = load_wordlist("wordlist")
        nearby_keys = load_keymap_conf("keymap.conf")
    except FileNotFoundError as e:
        print(e)
        return

    auto_correct_mode = yes_no_prompt("Enable automatic correction if confident?")

    print("\nEnter words to autocorrect, or type 'exit' to quit.")

    while True:
        word = input("\nEnter word: ").strip()
        if word.lower() in ("exit", "quit"):
            print("Exiting.")
            break
        if not word:
            print("Please enter a non-empty word.")
            continue

        corrected, suggestions = autocorrect(word, dictionary, nearby_keys=nearby_keys)
        
        if auto_correct_mode and corrected:
            print(f"Auto-corrected '{word}' to '{corrected}'.")
            continue

        if suggestions:
            print(f"No auto-correction applied for '{word}'. Suggestions:")
            for idx, suggestion in enumerate(suggestions, start=1):
                print(f"  {idx}. {suggestion}")
            selection = input("Pick a number to correct to that word, or press Enter to skip: ").strip()
            if selection.isdigit():
                sel_index = int(selection) - 1
                if 0 <= sel_index < len(suggestions):
                    chosen_word = suggestions[sel_index]
                    print(f"Corrected '{word}' to '{chosen_word}'.")
                else:
                    print("Invalid selection. No correction applied.")
            elif selection == "":
                print("No correction applied.")
            else:
                print("Invalid input. No correction applied.")
        else:
            print(f"No suggestions found for '{word}'.")

if __name__ == "__main__":
    main()
