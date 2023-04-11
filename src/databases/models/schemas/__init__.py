
import re


def contains_malicious_patterns(_input: str) -> bool:
    """
        will return true if the string matches any of the attack patterns
    :param _input:
    :return:
    """
    attack_pattern = r"(select|update|delete|drop|create|alter|insert|into|from|where|union|having|or|and|exec|script|javascript|xss|sql|cmd|../|..\|buffer|format|code|include|shell|rfi|lfi|phish)"
    return re.search(attack_pattern, _input, re.IGNORECASE) is not None

