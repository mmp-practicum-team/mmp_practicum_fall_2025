def find_palindrome(s: str) -> str:
    input_str = s
    is_pal = [
        [False] * len(input_str) for _ in input_str
    ]  # is_pal[i][j] == True iff input_str[i:j+1] is palindromic

    for i in range(len(input_str)):
        is_pal[i][i] = True

    ans = input_str[0]
    for substring_len in range(2, len(input_str) + 1):
        cur_res = None
        for i in range(len(input_str) - substring_len + 1):
            j = i + substring_len - 1
            tmp_res = (input_str[i] == input_str[j]) and (
                substring_len <= 3 or is_pal[i + 1][j - 1]
            )
            is_pal[i][j] = tmp_res
            if tmp_res and cur_res is None:
                cur_res = input_str[i : j + 1]
        if cur_res is not None:
            ans = cur_res
    return ans