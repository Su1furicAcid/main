import pygrading as gg
import os
from exception import CG
from utils import Env


@CG.catch
def prework(job: gg.Job):
    config = job.get_config()

    if len(os.listdir(config['submit_dir'])) == 0:
        raise CG.CompileError("No submit file")

    source_code = os.path.join(config["submit_dir"], "*.ml")
    compile_cmd = config['compile_cmd'].format(
        exec_src=config['exec_src'],
        source_dir=source_code
    )
    compile_result = gg.utils.exec(compile_cmd)
    if compile_result.returncode != 0:
        raise CG.CompileError(compile_result.stdout + '\n' + compile_result.stderr)

    # 动态计算测试用例数量
    testcase_dir = Env()["testcase_dir"]
    if "testcase_num" not in config or config["testcase_num"] == 0:
        config["testcase_num"] = len([f for f in os.listdir(testcase_dir) if f.startswith("input") and f.endswith(".txt")])

    if config['testcase_num'] == 0:
        raise CG.UnknownError("No test case file")

    # 创建测试用例
    testcases = gg.create_testcase(config['testcase_num'])
    for i in range(1, config['testcase_num'] + 1):
        input_file = os.path.join(testcase_dir, f"input{i}.txt")
        output_file = os.path.join(testcase_dir, f"output{i}.txt")
        if not os.path.exists(input_file):
            raise IOError(f"Input file not found: {input_file}")
        if not os.path.exists(output_file):
            raise IOError(f"Output file not found: {output_file}")
        testcases.append(
            name=str(i),
            input_src=input_file,
            output_src=output_file,
            score=10
        )
    job.set_testcases(testcases)