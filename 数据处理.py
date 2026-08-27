import json
import os
import copy
import bz2

'''数据处理部分'''

def parse_count_password_line(line: str):
    text = line.rstrip("\n\r")
    text = text.lstrip(" ")
    idx = text.find(" ")
    if idx < 1:
        return None, None
    count_str = text[:idx]
    password = text[idx+1:]
    try:
        count = int(count_str)
    except ValueError:
        return None, None
    return count, password
def read_txt(file_path):
    # SkullSecurity 的旧口令文件按单字节读取，避免无效 UTF-8 字节被替换。
    open_file = bz2.open if str(file_path).lower().endswith(".bz2") else open
    with open_file(file_path, "rt", encoding="latin-1", newline="") as f:
        for raw_line in f:
            if not raw_line:
                continue
            cnt, pwd = parse_count_password_line(raw_line)
            if cnt is not None and pwd is not None:
                yield cnt, pwd


#数据过滤：长度为4~40；全部字符为95可打印ASCii

def is_valid(pwd: str) -> bool:
    for c in pwd:
        o = ord(c)
        if not (32 <= o <= 126):
            return False
    return True

def cleaned_iterator(file_path: str):
    stats = {
    "total_types": 0,
    "total_occurrences": 0,
    "reject_too_short_types": 0,
    "reject_too_short_occurrences": 0,
    "reject_too_long_types": 0,
    "reject_too_long_occurrences": 0,
    "reject_non_ascii_types": 0,
    "reject_non_ascii_occurrences": 0,
    "kept_types": 0,
    "kept_occurrences": 0,
    }
    for cnt, pwd in read_txt(file_path):
        stats["total_types"] += 1
        stats["total_occurrences"] += cnt
        if len(pwd) < 4:
            stats["reject_too_short_types"] += 1
            stats["reject_too_short_occurrences"] += cnt
            continue
        if len(pwd) > 40:
            stats["reject_too_long_types"] += 1
            stats["reject_too_long_occurrences"] += cnt
            continue
        if not is_valid(pwd):        
            stats["reject_non_ascii_types"] += 1
            stats["reject_non_ascii_occurrences"] += cnt
            continue
        stats["kept_types"] += 1
        stats["kept_occurrences"] += cnt
        yield cnt, pwd

    cleaned_iterator.final_stats = copy.deepcopy(stats)

#数据集内存较大，采用流式输出
def process_dataset_stream(file_path: str, output_json_path: str, output_stats_path: str):
    gen = cleaned_iterator(file_path)

    with open(output_json_path, "w", encoding="utf-8") as fw:
        fw.write("{\n")
        source_file_json = json.dumps(
            os.path.basename(file_path),
            ensure_ascii=False
        )
        fw.write(f'  "source_file": {source_file_json},\n')

        # 流式写入passwords数组
        fw.write('  "passwords": [\n')

        first_item = True

        for cnt, pwd in gen:
            item = json.dumps( { "count": cnt,"password": pwd},
                ensure_ascii=False
            )

            if not first_item:
                fw.write(",\n")

            fw.write("    " + item)
            first_item = False

        # passwords数组结束
        fw.write("\n  ],\n")

        stats = cleaned_iterator.final_stats

        # 直接把统计结果写在passwords数组后面
        stats_json = json.dumps(
            stats,
            ensure_ascii=False,
            indent=2
        )

        fw.write(f'  "stats": {stats_json}\n')
        fw.write("}\n")

    save_stats_to_txt(stats, output_stats_path)

def save_stats_to_txt(stats: dict, output_txt_path: str):
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("数据清洗统计结果\n")
        f.write("\n")

        f.write(f"成功解析的口令种类数: {stats['total_types']}\n")
        f.write(f"成功解析的口令总数: {stats['total_occurrences']}\n")

        f.write("\n清洗后保留\n")
        f.write(f"口令种类数: {stats['kept_types']}\n")
        f.write(f"口令总数: {stats['kept_occurrences']}\n")

        f.write("\n长度小于4而删除\n")
        f.write(f"口令种类数: {stats['reject_too_short_types']}\n")
        f.write(
            f"口令总数: "
            f"{stats['reject_too_short_occurrences']}\n"
        )

        f.write("\n长度大于40而删除\n")
        f.write(f"口令种类数: {stats['reject_too_long_types']}\n")
        f.write(
            f"口令总数: "
            f"{stats['reject_too_long_occurrences']}\n"
        )

        f.write("\n包含非可打印ASCII字符而删除\n")
        f.write(f"口令种类数: {stats['reject_non_ascii_types']}\n")
        f.write(
            f"口令总数: "
            f"{stats['reject_non_ascii_occurrences']}\n"
        )
    
if __name__ == "__main__":

    ROCKYOU_PATH = "./data/rockyou-withcount.txt.bz2"
    PHPBB_PATH = "./data/phpbb-withcount.txt.bz2"

    OUT_ROCKYOU = "./rockyou-cleaned-训练集.json"
    OUT_PHPBB = "./phpbb-cleaned-测试集.json"

    process_dataset_stream(ROCKYOU_PATH, OUT_ROCKYOU,"./rockyou-cleaned-数据处理统计结果.txt")
    process_dataset_stream(PHPBB_PATH, OUT_PHPBB,"./phpbb-cleaned-数据处理统计结果.txt")

   
