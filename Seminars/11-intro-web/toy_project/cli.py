import argparse
from longest_palindrome import find_palindrome

def main():
    parser = argparse.ArgumentParser(description="Find the longest palindrome in a string.")
    parser.add_argument("--input-word", type=str, help="The input string")
    args = parser.parse_args()

    result = find_palindrome(args.input_word)
    print(f"Longest palindrome: {result}")

if __name__ == "__main__":
    main()