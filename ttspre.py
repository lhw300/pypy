import re


def format_time_for_speech(text: str) -> str:
    """
    把 HH:MM 或 HH:MM:SS 格式的时间，转换成中文自然读法
    "3:00"    -> "3点整"
    "13:24"   -> "13点24分"
    "1:50"    -> "1点50分"
    "9:05:30" -> "9点5分30秒"（如果出现带秒的情况）
    """
    def convert(match):
        h = int(match.group(1))
        m = int(match.group(2))
        s = match.group(3)  # 可能为 None

        if s is not None:
            s = int(s.lstrip(':'))
            if m == 0 and s == 0:
                return f"{h}点整"
            elif s == 0:
                return f"{h}点{m}分"
            else:
                return f"{h}点{m}分{s}秒"
        else:
            if m == 0:
                return f"{h}点整"
            else:
                return f"{h}点{m}分"

    # 注意：不能用 \b 做边界限定，中文字符在 Python re 里也会被判定为 \w，
    # 导致"是3:00"这类"中文紧贴数字"的场景边界检测失效、完全匹配不上
    pattern = r'(\d{1,2}):(\d{2})(:\d{2})?'
    return re.sub(pattern, convert, text)


def format_number_for_digit_reading(text: str) -> str:
    """
    把"工单号：1234"这类编号型数字，转换成逐位读的形式
    "工单号：1234" → "工单号：1 2 3 4"
    避免 TTS 前端的 number.fst 把连续数字当成基数词读（比如读成"一千二百三十四"）

    只对紧跟在编号类关键词后面的数字生效，不影响正常的数量表达
    （比如"3天"、"100元"这种量词/金额场景不受影响，会正常读成整体数值）
    """
    # 需要按数字串逐位处理的关键词，按你实际业务场景增减
    id_keywords = r'(工单|工单号|订单号|流水号|编号|验证码|工号|卡号|案件号)'

    def spacing_digits(match):
        keyword = match.group(1)
        sep = match.group(2) or ''   # "是"/"为"/"："/空格等分隔词，原样保留
        digits = match.group(3)
        spaced = ' '.join(list(digits))  # "1234" → "1 2 3 4"
        return f"{keyword}{sep}{spaced}"

    pattern = id_keywords + r'([是为：:\s]*)(\d+)'
    return re.sub(pattern, spacing_digits, text)


def normalize_for_tts(text: str) -> str:
    """
    给 TTS 引擎发送文本前的统一预处理入口，顺序很重要：
    必须先处理时间，再处理编号——因为工单号处理会在数字间插入空格，
    如果顺序反了，时间正则就没法再匹配到连续的 HH:MM 数字了。
    """
    text = format_time_for_speech(text)           # 先处理时间
    text = format_number_for_digit_reading(text)  # 再处理编号
    return text


if __name__ == "__main__":
    print("=== 时间格式化测试 ===")
    time_tests = [
        "预约时间是3:00，请准时到达。",
        "从13:24到15:00进行会议。",
        "闹钟设置在1:50",
        "会议时间3:00到13:24",
        "工单号：1234",              # 确认不会被时间函数误伤
        "时间是3:00到13:24和1:50",
    ]
    for t in time_tests:
        print(f"输入: {t}")
        print(f"输出: {format_time_for_speech(t)}")
        print()

    print("=== 工单号/编号格式化测试 ===")
    number_tests = [
        "工单号 1234，请记录一下。",
        "工单号是1234，请记录一下。",
        "工单号：1234，请留意后续处理。",
        "工单号为1234",
        "您的工单号1234已生成",
        "处理费用为100元，请知悉。",     # 金额，不应被拆分
        "预计300天内处理完毕",           # 天数，不应被拆分
        "工单号1234处理费用100元",       # 混合场景，两种数字都出现
    ]
    for t in number_tests:
        print(f"输入: {t}")
        print(f"输出: {format_number_for_digit_reading(t)}")
        print()

    print("=== 组合管道测试（normalize_for_tts，实际调用入口）===")
    combined_tests = [
        "时间是3:00到13:24和1:50",
        "工单号1234的预约时间是3:00",
        "您的工单号是1234，处理费用为100元，预计3天内完成，请于13:24前确认。",
    ]
    for t in combined_tests:
        print(f"输入: {t}")
        print(f"输出: {normalize_for_tts(t)}")
        print()